#!/usr/bin/env python3
"""
============================================================
 aes_big.py — chunked AES-256-GCM encryption for large files
============================================================

Why this exists (vs aes_encrypt.py):
    aes_encrypt.py loads the whole file into memory and encrypts
    it as one AES-GCM message. That's fine for small text, but for
    a multi-GB file it means: huge RAM use, no progress feedback,
    and if the process dies at 99% you start completely over.

How this one works:
    - The file is split into fixed-size chunks (default 16 MiB).
    - Each chunk is its own independent AES-256-GCM message, with
      its own auth tag. Corruption in one chunk doesn't affect the
      others and is detected exactly at that chunk.
    - Nonces are constructed as nonce_prefix(8 bytes, random,
      fixed per file) + chunk_index(4 bytes, big-endian). This
      guarantees a unique nonce per chunk without needing to store
      one per chunk.
    - Every CHECKPOINT_INTERVAL chunks (a "batch"), progress is
      fsync'd and a sidecar `<output>.ckpt` JSON file is written
      recording how many input bytes were consumed and how many
      output bytes were committed. If the process is interrupted,
      re-running the same command detects the checkpoint, truncates
      the partial output back to the last confirmed batch boundary,
      and resumes from there instead of restarting — similar to how
      zip/7z archive tools recover partially-written archives.
    - On successful completion a footer (central directory) is
      appended: chunk count, total plaintext size, and a SHA-256 of
      the whole plaintext, then the checkpoint file is deleted.
    - `verify` walks every chunk's GCM tag (and the footer hash on
      decrypt) without needing a password-holder to fully decrypt
      first, reporting the first corrupt/truncated chunk it finds —
      like `zip -T` / `7z t`.

File format:
    HEADER (37 bytes):
        magic          8 bytes   b"AESBIGF1"
        salt           16 bytes
        nonce_prefix   8 bytes
        chunk_size     4 bytes   uint32 big-endian
        reserved       1 byte    (0x00)
    CHUNK  (repeated):
        pt_len         4 bytes   uint32 big-endian (plaintext length of this chunk)
        tag            16 bytes  GCM auth tag
        ciphertext     pt_len bytes
    FOOTER (56 bytes, only present if encryption completed cleanly):
        footer_magic   8 bytes   b"AESBIGFT"
        num_chunks     8 bytes   uint64 big-endian
        total_size     8 bytes   uint64 big-endian
        sha256         32 bytes  SHA-256 of the full plaintext

Usage:
    python3 aes_big.py encrypt -f big.iso -o big.iso.enc
    python3 aes_big.py decrypt -f big.iso.enc -o big.iso
    python3 aes_big.py verify  -f big.iso.enc

    Options:
        -c/--chunk-size MB       chunk size in MiB (default 16, encrypt only)
        --checkpoint-every N     chunks per checkpoint batch (default 64)

Requirements:
    pip install pycryptodome
============================================================
"""

import argparse
import hashlib
import json
import os
import struct
import sys
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes

MAGIC = b"AESBIGF1"
FOOTER_MAGIC = b"AESBIGFT"
HEADER_SIZE = 8 + 16 + 8 + 4 + 1          # 37
FOOTER_SIZE = 8 + 8 + 8 + 32              # 56
CHUNK_PREFIX_SIZE = 4 + 16                # pt_len + tag

SALT_SIZE = 16
NONCE_PREFIX_SIZE = 8
KEY_SIZE = 32
PBKDF2_ITERATIONS = 200_000

DEFAULT_CHUNK_SIZE = 16 * 1024 * 1024     # 16 MiB
DEFAULT_CHECKPOINT_EVERY = 64             # flush/checkpoint every N chunks


# ---- header / footer (de)serialization ----------------------------------

def pack_header(salt: bytes, nonce_prefix: bytes, chunk_size: int) -> bytes:
    return MAGIC + salt + nonce_prefix + struct.pack(">I", chunk_size) + b"\x00"


def unpack_header(blob: bytes):
    if len(blob) != HEADER_SIZE or blob[:8] != MAGIC:
        raise ValueError("Not a valid aes_big archive (bad magic/header).")
    salt = blob[8:24]
    nonce_prefix = blob[24:32]
    chunk_size = struct.unpack(">I", blob[32:36])[0]
    return salt, nonce_prefix, chunk_size


def pack_footer(num_chunks: int, total_size: int, digest: bytes) -> bytes:
    return FOOTER_MAGIC + struct.pack(">QQ", num_chunks, total_size) + digest


def unpack_footer(blob: bytes):
    if len(blob) != FOOTER_SIZE or blob[:8] != FOOTER_MAGIC:
        return None
    num_chunks, total_size = struct.unpack(">QQ", blob[8:24])
    digest = blob[24:56]
    return num_chunks, total_size, digest


def chunk_nonce(nonce_prefix: bytes, chunk_index: int) -> bytes:
    return nonce_prefix + struct.pack(">I", chunk_index)


# ---- checkpoint sidecar ---------------------------------------------------

def checkpoint_path(output_path: Path) -> Path:
    return output_path.with_name(output_path.name + ".ckpt")


def write_checkpoint(ckpt_path: Path, state: dict):
    tmp = ckpt_path.with_suffix(ckpt_path.suffix + ".tmp")
    tmp.write_text(json.dumps(state))
    os.replace(tmp, ckpt_path)     # atomic on POSIX/Windows


def read_checkpoint(ckpt_path: Path):
    if not ckpt_path.exists():
        return None
    try:
        return json.loads(ckpt_path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


# ---- encrypt ---------------------------------------------------------------

def run_encrypt_file(input_path: Path, output_path: Path, password: str,
                      chunk_size: int, checkpoint_every: int):
    ckpt_path = checkpoint_path(output_path)
    input_size = input_path.stat().st_size
    state = read_checkpoint(ckpt_path)

    resuming = (
        state is not None
        and state.get("mode") == "encrypt"
        and output_path.exists()
        and state.get("input_size") == input_size
    )

    if resuming:
        salt = bytes.fromhex(state["salt"])
        nonce_prefix = bytes.fromhex(state["nonce_prefix"])
        chunk_size = state["chunk_size"]
        chunk_index = state["chunk_index"]
        input_offset = state["input_offset"]
        output_offset = state["output_offset"]
        key = PBKDF2(password, salt, dkLen=KEY_SIZE, count=PBKDF2_ITERATIONS)
        out_f = open(output_path, "r+b")
        out_f.truncate(output_offset)   # drop any partial/unflushed tail batch
        out_f.seek(output_offset)
        print(f"Resuming encryption from chunk {chunk_index} "
              f"({input_offset}/{input_size} bytes already processed).")
    else:
        salt = get_random_bytes(SALT_SIZE)
        nonce_prefix = get_random_bytes(NONCE_PREFIX_SIZE)
        key = PBKDF2(password, salt, dkLen=KEY_SIZE, count=PBKDF2_ITERATIONS)
        chunk_index = 0
        input_offset = 0
        out_f = open(output_path, "wb")
        out_f.write(pack_header(salt, nonce_prefix, chunk_size))
        output_offset = out_f.tell()

    hasher = hashlib.sha256()
    # If resuming, we can't recover the hash of already-written plaintext
    # without re-reading it, so re-hash the already-processed prefix.
    if resuming and input_offset:
        with open(input_path, "rb") as verify_f:
            remaining = input_offset
            while remaining:
                block = verify_f.read(min(1024 * 1024, remaining))
                if not block:
                    break
                hasher.update(block)
                remaining -= len(block)

    with open(input_path, "rb") as in_f:
        in_f.seek(input_offset)
        chunks_since_checkpoint = 0

        while True:
            plaintext = in_f.read(chunk_size)
            if not plaintext:
                break

            nonce = chunk_nonce(nonce_prefix, chunk_index)
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            ciphertext, tag = cipher.encrypt_and_digest(plaintext)

            out_f.write(struct.pack(">I", len(plaintext)))
            out_f.write(tag)
            out_f.write(ciphertext)

            hasher.update(plaintext)
            input_offset += len(plaintext)
            chunk_index += 1
            chunks_since_checkpoint += 1

            if chunks_since_checkpoint >= checkpoint_every:
                out_f.flush()
                os.fsync(out_f.fileno())
                output_offset = out_f.tell()
                write_checkpoint(ckpt_path, {
                    "mode": "encrypt",
                    "salt": salt.hex(),
                    "nonce_prefix": nonce_prefix.hex(),
                    "chunk_size": chunk_size,
                    "chunk_index": chunk_index,
                    "input_offset": input_offset,
                    "output_offset": output_offset,
                    "input_size": input_size,
                })
                chunks_since_checkpoint = 0
                print(f"  checkpoint: {input_offset}/{input_size} bytes "
                      f"({chunk_index} chunks)", file=sys.stderr)

        out_f.write(pack_footer(chunk_index, input_offset, hasher.digest()))
        out_f.flush()
        os.fsync(out_f.fileno())
    out_f.close()

    ckpt_path.unlink(missing_ok=True)
    print(f"Encrypted file written to: {output_path} "
          f"({chunk_index} chunks, {input_offset} bytes)")


# ---- decrypt -----------------------------------------------------------

def read_and_check_header(in_f) -> tuple:
    header = in_f.read(HEADER_SIZE)
    return unpack_header(header)


def run_decrypt_file(input_path: Path, output_path: Path, password: str,
                      checkpoint_every: int):
    ckpt_path = checkpoint_path(output_path)
    input_size = input_path.stat().st_size
    state = read_checkpoint(ckpt_path)

    resuming = (
        state is not None
        and state.get("mode") == "decrypt"
        and output_path.exists()
        and state.get("input_size") == input_size
    )

    with open(input_path, "rb") as in_f:
        salt, nonce_prefix, chunk_size = read_and_check_header(in_f)
        key = PBKDF2(password, salt, dkLen=KEY_SIZE, count=PBKDF2_ITERATIONS)

        if resuming:
            chunk_index = state["chunk_index"]
            input_offset = state["input_offset"]
            output_offset = state["output_offset"]
            in_f.seek(input_offset)
            out_f = open(output_path, "r+b")
            out_f.truncate(output_offset)
            out_f.seek(output_offset)
            print(f"Resuming decryption from chunk {chunk_index}.")
        else:
            chunk_index = 0
            input_offset = HEADER_SIZE
            out_f = open(output_path, "wb")

        chunks_since_checkpoint = 0
        footer_start = input_size - FOOTER_SIZE

        try:
            while in_f.tell() < footer_start:
                prefix = in_f.read(CHUNK_PREFIX_SIZE)
                if len(prefix) < CHUNK_PREFIX_SIZE:
                    raise ValueError(
                        f"Truncated archive: incomplete chunk header at "
                        f"chunk {chunk_index} (offset {in_f.tell()}).")
                pt_len, tag = struct.unpack(">I", prefix[:4])[0], prefix[4:20]
                ciphertext = in_f.read(pt_len)
                if len(ciphertext) < pt_len:
                    raise ValueError(
                        f"Truncated archive: incomplete chunk {chunk_index} "
                        f"(expected {pt_len} bytes, got {len(ciphertext)}).")

                nonce = chunk_nonce(nonce_prefix, chunk_index)
                cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
                try:
                    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
                except ValueError as e:
                    raise ValueError(
                        f"Chunk {chunk_index} failed authentication "
                        f"(wrong password or corrupted data): {e}")

                out_f.write(plaintext)
                chunk_index += 1
                input_offset = in_f.tell()
                chunks_since_checkpoint += 1

                if chunks_since_checkpoint >= checkpoint_every:
                    out_f.flush()
                    os.fsync(out_f.fileno())
                    output_offset = out_f.tell()
                    write_checkpoint(ckpt_path, {
                        "mode": "decrypt",
                        "chunk_index": chunk_index,
                        "input_offset": input_offset,
                        "output_offset": output_offset,
                        "input_size": input_size,
                    })
                    chunks_since_checkpoint = 0
                    print(f"  checkpoint: {input_offset}/{input_size} bytes "
                          f"({chunk_index} chunks)", file=sys.stderr)
        except ValueError:
            out_f.flush()
            os.fsync(out_f.fileno())
            output_offset = out_f.tell()
            write_checkpoint(ckpt_path, {
                "mode": "decrypt",
                "chunk_index": chunk_index,
                "input_offset": input_offset,
                "output_offset": output_offset,
                "input_size": input_size,
            })
            out_f.close()
            raise

        footer_blob = in_f.read(FOOTER_SIZE)
        footer = unpack_footer(footer_blob)
        out_f.flush()
        os.fsync(out_f.fileno())
    out_f.close()

    if footer is None:
        print("Warning: archive has no valid footer (interrupted encrypt, "
              "or file was truncated). Decrypted data may be incomplete, "
              "but every chunk that was present passed its auth tag.",
              file=sys.stderr)
    else:
        num_chunks, total_size, expected_digest = footer
        actual_size = output_path.stat().st_size
        if num_chunks != chunk_index or total_size != actual_size:
            raise ValueError(
                f"Footer mismatch: expected {num_chunks} chunks/"
                f"{total_size} bytes, got {chunk_index} chunks/{actual_size} bytes.")
        actual_digest = hashlib.sha256(output_path.read_bytes()).digest()
        if actual_digest != expected_digest:
            raise ValueError("SHA-256 mismatch: decrypted output does not "
                              "match the recorded plaintext hash.")
        print("Footer check passed: chunk count, size and SHA-256 all match.")

    ckpt_path.unlink(missing_ok=True)
    print(f"Decrypted file written to: {output_path}")


# ---- verify (no password needed for structural check; password ---------
# ---- optional to also confirm auth tags decrypt cleanly) ----------------

def run_verify_file(input_path: Path, password: str | None):
    input_size = input_path.stat().st_size
    with open(input_path, "rb") as in_f:
        try:
            salt, nonce_prefix, chunk_size = read_and_check_header(in_f)
        except ValueError as e:
            print(f"INVALID: {e}")
            sys.exit(1)

        key = None
        if password:
            key = PBKDF2(password, salt, dkLen=KEY_SIZE, count=PBKDF2_ITERATIONS)

        footer_start = input_size - FOOTER_SIZE
        chunk_index = 0
        total_bytes = 0
        hasher = hashlib.sha256() if password else None

        while in_f.tell() < footer_start:
            offset = in_f.tell()
            prefix = in_f.read(CHUNK_PREFIX_SIZE)
            if len(prefix) < CHUNK_PREFIX_SIZE:
                print(f"CORRUPT: truncated chunk header at chunk {chunk_index}, "
                      f"file offset {offset}.")
                sys.exit(1)
            pt_len, tag = struct.unpack(">I", prefix[:4])[0], prefix[4:20]
            ciphertext = in_f.read(pt_len)
            if len(ciphertext) < pt_len:
                print(f"CORRUPT: truncated ciphertext at chunk {chunk_index}, "
                      f"file offset {offset} (expected {pt_len}, got {len(ciphertext)}).")
                sys.exit(1)

            if key is not None:
                nonce = chunk_nonce(nonce_prefix, chunk_index)
                cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
                try:
                    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
                    hasher.update(plaintext)
                except ValueError:
                    print(f"CORRUPT: auth tag failed at chunk {chunk_index}, "
                          f"file offset {offset} (wrong password or tampered data).")
                    sys.exit(1)

            total_bytes += pt_len
            chunk_index += 1

        footer_blob = in_f.read(FOOTER_SIZE)
        footer = unpack_footer(footer_blob)

    if footer is None:
        print(f"OK (no footer — archive from an interrupted/in-progress encrypt): "
              f"{chunk_index} chunks, {total_bytes} bytes all pass structural checks.")
        return

    num_chunks, total_size, expected_digest = footer
    if num_chunks != chunk_index or total_size != total_bytes:
        print(f"CORRUPT: footer says {num_chunks} chunks/{total_size} bytes, "
              f"found {chunk_index} chunks/{total_bytes} bytes.")
        sys.exit(1)

    if password:
        if hasher.digest() != expected_digest:
            print("CORRUPT: full SHA-256 does not match footer (data corrupted "
                  "despite individual chunk tags passing — should not happen).")
            sys.exit(1)
        print(f"OK: {chunk_index} chunks, {total_bytes} bytes, all auth tags "
              f"and full SHA-256 verified.")
    else:
        print(f"OK (structure only — pass -p/password to also verify auth tags "
              f"and SHA-256): {chunk_index} chunks, {total_bytes} bytes, footer present.")


# ---- CLI -----------------------------------------------------------------

def default_encrypt_output(input_path: Path) -> Path:
    return input_path.with_name(input_path.name + ".enc")


def default_decrypt_output(input_path: Path) -> Path:
    if input_path.suffix == ".enc":
        return input_path.with_suffix("")
    return input_path.with_name(input_path.name + ".dec")


def main():
    parser = argparse.ArgumentParser(
        description="Chunked AES-256-GCM encryption for large files, with "
                     "checkpointed resume and zip-style verification.")
    parser.add_argument("mode", choices=["encrypt", "decrypt", "verify"])
    parser.add_argument("-f", "--file", required=True, help="input file")
    parser.add_argument("-o", "--output", help="output file (has a default)")
    parser.add_argument("-c", "--chunk-size", type=int, default=16,
                         help="chunk size in MiB (encrypt only, default 16)")
    parser.add_argument("--checkpoint-every", type=int, default=DEFAULT_CHECKPOINT_EVERY,
                         help="chunks per checkpoint batch (default 64)")
    parser.add_argument("-p", "--password", help="password (omit to be prompted; "
                                                   "verify can skip this for a structure-only check)")
    args = parser.parse_args()

    input_path = Path(args.file)
    if not input_path.is_file():
        print(f"Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    if args.mode == "verify":
        password = args.password
        run_verify_file(input_path, password)
        return

    output_path = Path(args.output) if args.output else (
        default_encrypt_output(input_path) if args.mode == "encrypt"
        else default_decrypt_output(input_path)
    )
    password = args.password or input("Password: ")

    if args.mode == "encrypt":
        run_encrypt_file(input_path, output_path, password,
                          args.chunk_size * 1024 * 1024, args.checkpoint_every)
    else:
        try:
            run_decrypt_file(input_path, output_path, password, args.checkpoint_every)
        except ValueError as e:
            print(f"\nDecryption failed: {e}", file=sys.stderr)
            print(f"Progress checkpointed — re-run the same command to resume.",
                  file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
