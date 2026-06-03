# PWN101

Was in learning mode: so just tried, took hints and using it as a reference ... solved almost all the challenges. Finished Challenge 10 with help of Razvi's help, and on 7th my local implementation didn't work on remote.

Most of the exploits I wrote with Claude with some of my tweaks ... so ...

## Challenge 1

Simple buffer overflow! `gets()` doesn't limit the input. BUFFER OVERLOW!

```bash
# terminal --1
┌──(kali㉿kali)-[~/Downloads/PWN101]
└─$ cutter ./pwn101-pwn101


# terminal --2
## put in anything other than 0x539 is capable to bypass the `if` clause
┌──(kali㉿kali)-[~/Downloads/PWN101]
└─$ nc 10.129.182.254 9001
       ┌┬┐┬─┐┬ ┬┬ ┬┌─┐┌─┐┬┌─┌┬┐┌─┐
        │ ├┬┘└┬┘├─┤├─┤│  ├┴┐│││├┤ 
        ┴ ┴└─ ┴ ┴ ┴┴ ┴└─┘┴ ┴┴ ┴└─┘
                 pwn 101          

Hello!, I am going to shopping.
My mom told me to buy some ingredients.
Ummm.. But I have low memory capacity, So I forgot most of them.
Anyway, she is preparing Briyani for lunch, Can you help me to buy those items :D

Type the required ingredients to make briyani: 
11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111
Thanks, Here's a small gift for you <3
whoami
pwn101
ls -al
total 48
drwx------  3 pwn101 pwn101  4096 Feb  8  2022 .
drwxr-xr-x 14 root   root    4096 Jul  5  2025 ..
lrwxrwxrwx  1 pwn101 pwn101     9 Feb  8  2022 .bash_history -> /dev/null
-rw-r--r--  1 pwn101 pwn101   220 Apr  4  2018 .bash_logout
-rw-r--r--  1 pwn101 pwn101  3771 Apr  4  2018 .bashrc
drwxrwxr-x  3 pwn101 pwn101  4096 Feb  8  2022 .local
-rw-r--r--  1 pwn101 pwn101   807 Apr  4  2018 .profile
-rwxrwxrwx  1 pwn101 pwn101    32 Jan 28  2022 flag.txt
-rwxrwxr-x  1 pwn101 pwn101 12760 Feb  8  2022 pwn101
-rwxrwxrwx  1 pwn101 pwn101  1137 Feb  8  2022 pwn101.c
cat flag.txt
THM{xyz---abc}
exit
```

## Challenge 2 - [Exploit](./exploit-pwn102.py)

BUFFER OVERFLOW AGAIN! But this time, I had to use a target address and target value to bypass the `if` clause. 

## Challenge 3 - [Exploit](./exploit-pwn103.py)

RET2WIN along with BOF! Binary was static(no ASLR), so simply fetched the address of `admin_only()` and overflowed the `scanf()` referenced buffer to overwrite the return address on stack.

## Challenge 4 - [Exploit](./exploit-pwn104.py)

`read()` is used for read, without any limit. So BOF again! But this time, there was no `win()` function. Since the binary had stack protection disabled, I simply overwrote the return address of shellcode. ASLR was enabled, so had to leak the stack address first.

## Challenge 5 - [Exploit](./exploit-pwn105.py)

Simple Integer Overflow! So passed some big values, and we done!

## Challenge 6 - [Exploit](./exploit-pwn106.py)

Format String Vulnerability! So, I simply used `%{num}$lX` to leak the relevant addresses. And that way leaked the memory address and value needed as a flag.

## Challenge 7 - [Exploit](./exploit-pwn107.py)

Format String Vulnerability! With canaries. Also limited number of leaks were there so only leaked the canary value and the `get_streak` method address. Then used it for ret2libc attack. 

## Challenge 8 - [Exploit](./exploit-pwn108.py)

Format String Vulnerability! With writable FSV access i.e.`%n`(check the file exn specifics) which writes 'sysout' number of bytes prints --> referenced variable. And also with limited number of leaks. With Global Offset Table and PLT exploits. So, I leaked the address of `puts()`(Picked it because in the end it was the function which got executed after `scanf`) from GOT. Then overwrote the GOT entry of `puts()` with the address of `holiday` method.

## Challenge 9 - [Exploit](./exploit-pwn109.py)

Used ROP to extract `pop rdi; ret` & `ret` gadgets. ASLR doesn't randomize every address(a fact that was hard to find when u are looking at a wall of assembly). So with GOT's (for different dynamically linked functions, `puts`, `gets` and `setvbuf`) and PLT's base address... extracted their dynamic addresses, and the the version of `libc` used in server. Then extracted the address of `system()` and the `/bin/sh` string offset and used it to overwrite the return address to call `system("/bin/sh")` via ROP

The input space for overflow was only 0x200 bytes, so had to use ROP chains effectively.

## Challenge 10 - [Exploit](./exploit-pwn110.py) 

Statically linked binary. `mprotect()` is present, but needs the stack's dynamic page address. Extracted the stack's dynamic page address via BOF. Used it to call `mprotect()` to make the stack page executable, and then executed the shellcode placed in the stack via BOF. 

### Found [this](https://dguerri.hashnode.dev/binary-exploitation-pwn101-write-up) recently, who'll sum it up better than me.