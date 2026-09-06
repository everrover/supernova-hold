#!/usr/bin/env python3
"""
============================================================
req.txt
============================================================
pycryptodome==3.23.0
============================================================
 aes_tool.py — AES-256-GCM text encryption/decryption
============================================================

README
-------
What this is:
    A single script that both encrypts and decrypts text using
    AES-256 in GCM mode (authenticated encryption) with a
    password-derived key.

How it works:
    - Your password + a random 16-byte salt are run through
      PBKDF2-HMAC-SHA256 (200,000 iterations) to derive a 256-bit key.
    - A random 12-byte nonce is generated for AES-GCM.
    - Encrypting produces: salt(16) + nonce(12) + tag(16) + ciphertext,
      all packed together and base64-encoded into one token string.
    - Decrypting reverses this: it slices the token back into its
      parts, re-derives the key from the password + salt, and uses
      the tag to verify integrity (GCM fails loudly if the password
      is wrong or the data was altered).

Requirements:
    pip install -r requirements.txt
    (installs: pycryptodome)

    > OPT: Set up a virtual environment first, then install into it:

        python3 -m venv venv
        source venv/bin/activate       # Windows: venv\\Scripts\\activate
        pip install -r requirements.txt

    (installs: pycryptodome)

    Deactivate later with: deactivate

Usage:
    Text mode (interactive prompts, base64 in/out):
        python3 aes_tool.py encrypt
        python3 aes_tool.py decrypt
        python3 aes_tool.py            # no args -> asks encrypt or decrypt

    File mode (-f/--file input, -o/--output result file):
        python3 aes_tool.py encrypt -f secret.txt -o secret.txt.enc
        python3 aes_tool.py decrypt -f secret.txt.enc -o secret.txt

        -o is optional:
            encrypt defaults to "<input>.enc"
            decrypt defaults to "<input>" with a trailing ".enc" removed,
            or "<input>.dec" if the input doesn't end in ".enc"

Notes:
    - The salt and nonce are stored inside the blob itself, so you
      only need to remember the password to decrypt later.
    - File mode never prints file contents to the terminal — it only
      reads/writes the files you point it at.
    - Never reuse a password with weak/guessable strength for
      anything sensitive — PBKDF2 slows down brute-forcing but
      doesn't make a weak password strong.
============================================================
"""

import argparse
import base64
import sys
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes

SALT_SIZE = 16
NONCE_SIZE = 12
TAG_SIZE = 16
KEY_SIZE = 32          # 256-bit key
PBKDF2_ITERATIONS = 200_000


# ---- core, works on raw bytes -------------------------------------------

def encrypt_bytes(plaintext: bytes, password: str) -> bytes:
    salt = get_random_bytes(SALT_SIZE)
    key = PBKDF2(password, salt, dkLen=KEY_SIZE, count=PBKDF2_ITERATIONS)

    cipher = AES.new(key, AES.MODE_GCM, nonce=get_random_bytes(NONCE_SIZE))
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)

    return salt + cipher.nonce + tag + ciphertext


def decrypt_bytes(blob: bytes, password: str) -> bytes:
    salt = blob[:SALT_SIZE]
    nonce = blob[SALT_SIZE:SALT_SIZE + NONCE_SIZE]
    tag = blob[SALT_SIZE + NONCE_SIZE:SALT_SIZE + NONCE_SIZE + TAG_SIZE]
    ciphertext = blob[SALT_SIZE + NONCE_SIZE + TAG_SIZE:]

    key = PBKDF2(password, salt, dkLen=KEY_SIZE, count=PBKDF2_ITERATIONS)

    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)  # raises if wrong pwd/tampered


# ---- text convenience wrappers (base64 in/out) --------------------------

def encrypt(plaintext: str, password: str) -> str:
    blob = encrypt_bytes(plaintext.encode("utf-8"), password)
    return base64.b64encode(blob).decode("utf-8")


def decrypt(token: str, password: str) -> str:
    blob = decrypt_bytes(base64.b64decode(token), password)
    return blob.decode("utf-8")


# ---- text mode -----------------------------------------------------------

def run_encrypt_text():
    password = input("Password: ")
    plaintext = input("Text to encrypt: ")
    token = encrypt(plaintext, password)
    print("\nEncrypted (base64):")
    print(token)


def run_decrypt_text():
    password = input("Password: ")
    token = input("Encrypted text (base64): ")
    try:
        plaintext = decrypt(token, password)
        print("\nDecrypted text:")
        print(plaintext)
    except (ValueError, KeyError):
        print("\nDecryption failed: wrong password or corrupted/tampered data.")


# ---- file mode -------------------------------------------------------------

def default_encrypt_output(input_path: Path) -> Path:
    return input_path.with_name(input_path.name + ".enc")


def default_decrypt_output(input_path: Path) -> Path:
    if input_path.suffix == ".enc":
        return input_path.with_suffix("")
    return input_path.with_name(input_path.name + ".dec")


def confirm_overwrite(output_path: Path) -> bool:
    if not output_path.exists():
        return True
    answer = input(f"{output_path} already exists — overwrite? [y/N]: ").strip().lower()
    return answer.startswith("y")


def run_encrypt_file(input_path: Path, output_path: Path):
    if not confirm_overwrite(output_path):
        print("Cancelled.")
        return
    password = input("Password: ")
    data = input_path.read_bytes()
    blob = encrypt_bytes(data, password)
    output_path.write_bytes(blob)
    print(f"Encrypted file written to: {output_path}")


def run_decrypt_file(input_path: Path, output_path: Path):
    if not confirm_overwrite(output_path):
        print("Cancelled.")
        return
    password = input("Password: ")
    blob = input_path.read_bytes()
    try:
        data = decrypt_bytes(blob, password)
    except (ValueError, KeyError):
        print("\nDecryption failed: wrong password or corrupted/tampered data.")
        return
    output_path.write_bytes(data)
    print(f"Decrypted file written to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="AES-256-GCM text/file encrypt-decrypt tool.")
    parser.add_argument("mode", nargs="?", choices=["encrypt", "decrypt"],
                         help="encrypt or decrypt (omit for interactive menu)")
    parser.add_argument("-f", "--file", help="input file (switches to file mode)")
    parser.add_argument("-o", "--output", help="output file (file mode only; has a default)")
    args = parser.parse_args()

    mode = args.mode
    if mode is None:
        choice = input("Encrypt or decrypt? [e/d]: ").strip().lower()
        mode = "encrypt" if choice.startswith("e") else "decrypt"

    if args.file:
        input_path = Path(args.file)
        if not input_path.is_file():
            print(f"Input file not found: {input_path}", file=sys.stderr)
            sys.exit(1)

        if mode == "encrypt":
            output_path = Path(args.output) if args.output else default_encrypt_output(input_path)
            run_encrypt_file(input_path, output_path)
        else:
            output_path = Path(args.output) if args.output else default_decrypt_output(input_path)
            run_decrypt_file(input_path, output_path)
    else:
        if mode == "encrypt":
            run_encrypt_text()
        else:
            run_decrypt_text()


if __name__ == "__main__":
    main()
