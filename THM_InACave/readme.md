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

info.txt for one of the files which i read incorrectly with cat(due to an escape character) and was stuck on that for a while. [LINK](https://termack.github.io/thm_writeups/inacave.html) helped me in gettign unstuck...

Also I used java_1.8.0_452 for generating XXE payload from frontend for reflective attack. Application uses 0_251 version but this also worked.