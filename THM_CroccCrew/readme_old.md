┌──(kali㉿kali)-[~/Downloads]
└─$ sudo nano /etc/hosts                                                                                                      
[sudo] password for kali: 
                                                                                                                                                           
┌──(kali㉿kali)-[~/Downloads]
└─$ cat ./nmapop.log 
┌──(kali㉿kali)-[~/Downloads]
└─$ sudo nmap -sC -sV -T5 10.49.191.103
[sudo] password for kali: 
Starting Nmap 7.98 ( https://nmap.org ) at 2026-09-08 10:02 -0600
Nmap scan report for 10.49.191.103
Host is up (0.033s latency).
Not shown: 989 filtered tcp ports (no-response)
PORT     STATE SERVICE       VERSION
53/tcp   open  domain        Simple DNS Plus
80/tcp   open  http          Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
| http-methods: 
|_  Potentially risky methods: TRACE
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-09-08 16:02:36Z)
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: COOCTUS.CORP, Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds?
464/tcp  open  kpasswd5?
593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp  open  tcpwrapped
3389/tcp open  ms-wbt-server Microsoft Terminal Services
| ssl-cert: Subject: commonName=DC.COOCTUS.CORP
| Not valid before: 2026-09-07T16:02:00
|_Not valid after:  2027-03-09T16:02:00
|_ssl-date: 2026-09-08T16:03:18+00:00; -1s from scanner time.
| rdp-ntlm-info: 
|   Target_Name: COOCTUS
|   NetBIOS_Domain_Name: COOCTUS
|   NetBIOS_Computer_Name: DC
|   DNS_Domain_Name: COOCTUS.CORP
|   DNS_Computer_Name: DC.COOCTUS.CORP
|   Product_Version: 10.0.17763
|_  System_Time: 2026-09-08T16:02:38+00:00
Service Info: Host: DC; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-time: 
|   date: 2026-09-08T16:02:39
|_  start_date: N/A
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled and required
|_clock-skew: mean: -1s, deviation: 0s, median: -1s

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 53.52 seconds

                                                                                                                                                           
┌──(kali㉿kali)-[~/Downloads]
└─$ gobuster dir --wordlist /usr/share/wordlists/dirb/common.txt -b 404 -x .php,.xml,.txt -t 50 -o gob-1.log -u target.thm
===============================================================
Gobuster v3.8.2
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://target.thm
[+] Method:                  GET
[+] Threads:                 50
[+] Wordlist:                /usr/share/wordlists/dirb/common.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.8.2
[+] Extensions:              php,xml,txt
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
backdoor.php         (Status: 200) [Size: 529]
index.html           (Status: 200) [Size: 5342323]
robots.txt           (Status: 200) [Size: 70]
robots.txt           (Status: 200) [Size: 70]
Progress: 18452 / 18452 (100.00%)
===============================================================
Finished
===============================================================
                                                                                                                                                           
┌──(kali㉿kali)-[~/Downloads]
└─$ gobuster dir --wordlist /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -b 404 -x .php,.xml,.txt -t 50 -o gob-1.log -u target.thm 
===============================================================
Gobuster v3.8.2
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://target.thm
[+] Method:                  GET
[+] Threads:                 50
[+] Wordlist:                /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.8.2
[+] Extensions:              txt,php,xml
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
robots.txt           (Status: 200) [Size: 70]
backdoor.php         (Status: 200) [Size: 529]
Robots.txt           (Status: 200) [Size: 70]
Backdoor.php         (Status: 200) [Size: 529]
Progress: 882232 / 882232 (100.00%)
===============================================================
Finished
===============================================================

┌──(kali㉿kali)-[~/Downloads]
└─$ rdesktop -g 50% target.thm
Autoselecting keyboard map 'en-us' from locale
Core(warning): Certificate received from server is NOT trusted by this system, an exception has been added by the user to trust this specific certificate.
Failed to initialize NLA, do you have correct Kerberos TGT initialized ?
Core(warning): Certificate received from server is NOT trusted by this system, an exception has been added by the user to trust this specific certificate.
Connection established using SSL.
                                                                                                                                                           
┌──(kali㉿kali)-[~/Downloads]
└─$ ls 
 ap-south-1-everroveractual-premium.ovpn   curlevro                                     exrex          scheme-catcher    thmenv
 athena                                    CVE-2021-26828_ScadaBR_RCE                   gob-1.log      site-main.md      THM__PP
 brr                                       cyberpunk2077                                inacave        site-robots.txt   users.txt
 coorectusr.txt                           'eu-west-3-everroveractual-regular(1).ovpn'   ldapenum.log   THM_Checkmate     validhackers-1.log
 cupp                                      eu-west-3-everroveractual-regular.ovpn       nmapop.log     THM_DogCat        validhackers.log
                                                                                                                                                           
┌──(kali㉿kali)-[~/Downloads]
└─$ mv ./users.txt ./listofusers.txt                               
                                                                                                                                                           
┌──(kali㉿kali)-[~/Downloads]
└─$ cat user.txt                                                        
THM{Gu3st_Pl3as3}                                                                                                                                                           
┌──(kali㉿kali)-[~/Downloads]
└─$ 



**https://github.com/fortra/impacket/releases#release-impacket_0_11_0**
https://github.com/jesusgavancho/TryHackMe_and_HackTheBox/blob/master/Crocc%20Crew.md

# [THM_CroccCrew](https://tryhackme.com/room/crocccrew)

Found possible usernames on `target.thm/`, some curious things in `robots.txt` and exposed DB passwords in `/db-config.bak`.

DB configs were not useful, neither was the `backdoor.php` page.

