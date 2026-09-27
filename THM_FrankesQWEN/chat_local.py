#!/usr/bin/env python3
import argparse, contextlib, faulthandler, json, os, sys, threading, time

T0 = time.time()
DEBUG = True

def rss_mb():
    try:
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith("VmRSS"):
                    return int(line.split()[1]) // 1024
    except Exception:
        pass
    return -1

def meminfo():
    out = {}
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                k, v = line.split(":")
                if k in ("MemTotal", "MemAvailable", "SwapTotal", "SwapFree"):
                    out[k] = int(v.split()[0]) // 1024
    except Exception:
        pass
    return out

def log(msg):
    if DEBUG:
        print(f"[dbg {time.time() - T0:7.2f}s rss={rss_mb()}MB] {msg}", file=sys.stderr, flush=True)

@contextlib.contextmanager
def phase(name, beat=5, dump_after=30):
    log(f"BEGIN {name}")
    t0 = time.time()
    stop = threading.Event()
    def heartbeat():
        while not stop.wait(beat):
            mi = meminfo()
            log(f"  ... {name} still running ({time.time() - t0:.0f}s) "
                f"avail={mi.get('MemAvailable', '?')}MB swapfree={mi.get('SwapFree', '?')}MB")
    if DEBUG:
        threading.Thread(target=heartbeat, daemon=True).start()
        faulthandler.dump_traceback_later(dump_after, repeat=True, file=sys.stderr)
    try:
        yield
    finally:
        stop.set()
        if DEBUG:
            faulthandler.cancel_dump_traceback_later()
        log(f"END {name} ({time.time() - t0:.2f}s)")

def load(path, dtype, torch, AutoTokenizer, AutoModelForCausalLM):
    path = os.path.abspath(os.path.expanduser(path))
    cfg_path = os.path.join(path, "config.json")
    if not os.path.isfile(cfg_path):
        sys.exit(f"No config.json in {path}")
    log(f"model dir: {path}")
    for fn in sorted(os.listdir(path)):
        fp = os.path.join(path, fn)
        if os.path.isfile(fp):
            log(f"  file {fn:32s} {os.path.getsize(fp) / 1e6:10.1f} MB  readable={os.access(fp, os.R_OK)}")
    with open(cfg_path) as f:
        cfg = json.load(f)
    log("config: " + ", ".join(
        f"{k}={cfg.get(k)}" for k in
        ("model_type", "architectures", "hidden_size", "num_hidden_layers", "vocab_size",
         "max_position_embeddings", "torch_dtype", "dtype") if k in cfg))
    mi = meminfo()
    log(f"memory: total={mi.get('MemTotal')}MB avail={mi.get('MemAvailable')}MB "
        f"swap={mi.get('SwapTotal')}MB  (weights file needs roughly its size in RAM or more)")
    with phase("load tokenizer"):
        tok = AutoTokenizer.from_pretrained(path)
    log(f"tokenizer: {type(tok).__name__} vocab={len(tok)} eos={tok.eos_token!r}({tok.eos_token_id}) "
        f"pad={tok.pad_token!r}({tok.pad_token_id}) has_chat_template={bool(getattr(tok, 'chat_template', None))}")
    with phase("load model weights"):
        model = AutoModelForCausalLM.from_pretrained(path, dtype=dtype)
        model.eval()
    n = sum(p.numel() for p in model.parameters())
    p0 = next(model.parameters())
    log(f"model: {type(model).__name__} params={n / 1e6:.1f}M dtype={p0.dtype} device={p0.device}")
    log(f"generation_config: {model.generation_config.to_dict()}")
    return path, tok, model

def build_inputs(tok, history):
    if getattr(tok, "chat_template", None):
        text = tok.apply_chat_template(history, tokenize=False, add_generation_prompt=True)
    else:
        text = "".join(f"{m['role']}: {m['content']}\n" for m in history) + "assistant:"
    log(f"prompt text ({len(text)} chars): {text[-500:]!r}")
    return tok(text, return_tensors="pt", add_special_tokens=False)

def sibling_models(path):
    parent = os.path.dirname(path)
    return sorted(os.path.join(parent, d) for d in os.listdir(parent)
                  if os.path.isfile(os.path.join(parent, d, "config.json")))

def main():
    global DEBUG
    ap = argparse.ArgumentParser()
    ap.add_argument("-m", "--model", default=os.path.expanduser("~/frankesqwen-v7"))
    ap.add_argument("-s", "--system", default=None)
    ap.add_argument("-n", "--max-new-tokens", type=int, default=512)
    ap.add_argument("-t", "--temperature", type=float, default=None)
    ap.add_argument("--dtype", default="auto", help="auto | float32 | bfloat16 | float16")
    ap.add_argument("--threads", type=int, default=None, help="torch CPU threads")
    ap.add_argument("--no-debug", action="store_true")
    args = ap.parse_args()
    DEBUG = not args.no_debug

    log(f"python {sys.version.split()[0]} | cpus={os.cpu_count()} | argv={sys.argv[1:]}")
    with phase("import torch"):
        import torch
    log(f"torch {torch.__version__} | cuda={torch.cuda.is_available()} | "
        f"threads={torch.get_num_threads()} interop={torch.get_num_interop_threads()}")
    if args.threads:
        torch.set_num_threads(args.threads)
        log(f"torch threads set to {args.threads}")
    with phase("import transformers"):
        import transformers
        from transformers import AutoModelForCausalLM, AutoTokenizer, TextStreamer
    log(f"transformers {transformers.__version__}")
    if DEBUG:
        transformers.logging.set_verbosity_info()

    class DebugStreamer(TextStreamer):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self.n = 0
            self.t0 = time.time()
        def put(self, value):
            if getattr(self, "next_tokens_are_prompt", False):
                log(f"generate() started; prompt tokens={value.numel()}")
            else:
                self.n += 1
                dt = time.time() - self.t0
                if self.n == 1:
                    log(f"first token after {dt:.2f}s (prefill + 1 step)")
                elif self.n % 10 == 0:
                    log(f"{self.n} new tokens, {self.n / dt:.2f} tok/s avg")
            super().put(value)

    dtype = args.dtype if args.dtype == "auto" else getattr(torch, args.dtype)
    path, tok, model = load(args.model, dtype, torch, AutoTokenizer, AutoModelForCausalLM)
    system = args.system
    history = [{"role": "system", "content": system}] if system else []
    name = os.path.basename(path)
    print(f"Ready: {name}  (/models, /model <dir>, /system <text>, /clear, /exit)")

    while True:
        try:
            user = input(f"\n[{name}] you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print(); break
        if not user:
            continue
        if user.startswith("/"):
            cmd, _, arg = user.partition(" "); arg = arg.strip()
            if cmd in ("/exit", "/quit"): break
            elif cmd == "/models":
                for m in sibling_models(path): print(("* " if m == path else "  ") + m)
            elif cmd == "/model":
                cand = arg if os.path.isabs(os.path.expanduser(arg)) else os.path.join(os.path.dirname(path), arg)
                path, tok, model = load(cand if os.path.isdir(cand) else arg, dtype,
                                        torch, AutoTokenizer, AutoModelForCausalLM)
                name = os.path.basename(path)
                history = [{"role": "system", "content": system}] if system else []
                print(f"Switched to {name}; history cleared.")
            elif cmd == "/system":
                system = arg or None
                history = [{"role": "system", "content": system}] if system else []
                print("System prompt set; history cleared.")
            elif cmd == "/clear":
                history = [{"role": "system", "content": system}] if system else []
                print("History cleared.")
            else: print("Unknown command.")
            continue

        history.append({"role": "user", "content": user})
        try:
            inputs = build_inputs(tok, history)
            n_prompt = inputs["input_ids"].shape[1]
            log(f"prompt tokens={n_prompt} history_msgs={len(history)}")
            gen = {"max_new_tokens": args.max_new_tokens,
                   "pad_token_id": tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id}
            if args.temperature is not None:
                if args.temperature > 0: gen.update(do_sample=True, temperature=args.temperature)
                else: gen.update(do_sample=False)
            log(f"generate kwargs: {gen}")
            print(f"{name}> ", end="", flush=True)
            streamer = DebugStreamer(tok, skip_prompt=True, skip_special_tokens=True)
            t_gen = time.time()
            with phase("generate", beat=5, dump_after=45):
                with torch.inference_mode():
                    out = model.generate(**inputs, streamer=streamer, **gen)
            new_ids = out[0][n_prompt:]
            dt = time.time() - t_gen
            last = int(new_ids[-1]) if len(new_ids) else None
            log(f"generated {len(new_ids)} tokens in {dt:.2f}s ({len(new_ids) / max(dt, 1e-9):.2f} tok/s); "
                f"last_token={last} hit_eos={last == tok.eos_token_id}")
            reply = tok.decode(new_ids, skip_special_tokens=True).strip()
            history.append({"role": "assistant", "content": reply})
        except KeyboardInterrupt:
            print("\n[interrupted]"); history.pop()
        except Exception as e:
            import traceback
            print(f"\n[error] {e}")
            if DEBUG: traceback.print_exc()
            history.pop()

if __name__ == "__main__":
    main()
