https://play.picoctf.org/practice/challenge/187

Personal note :: Was curious how use-after-free vulns are exploited, hence this.

Memory allocation and de-allocation block addresses - fetched via Ghidra

```sh
ghidra auto -t vulnerable_binary
# run complete

gdb ./vulnerable_binary
# logs
(gdb) break *0x08048d6f
Breakpoint 1 at 0x8048d6f
(gdb) break *0x08048a76
Breakpoint 2 at 0x8048a76
(gdb) break *0x08048aff
Breakpoint 3 at 0x8048aff
# stuff i ran
OOP! Memory leak...0x80487d6
(gdb) x/8gwx 0x804c1a0 - 4

0x804c19c:	0x00000011	0x08048988	0x0804c5c0	0x00000000
0x804c1ac:	0x00000411	0x6f740a53	0x000a6f72	0x00000000
```

apt-get update
apt-get install python3 python3-pip python3-dev git libssl-dev libffi-dev build-essential
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade pwntools