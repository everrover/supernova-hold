# THM Jurassic Park

Found SQL injection on `/item.php?id=1` and then checked for several payloads. ` `(bypassed using `+`), `admin`, `password` and a few more keywords/phrases were blacklisted. There was even a page complaining about it from where i got the username `dennis`. `?id=5`

Got access to `users` table. Passwords were in column 5 in plaintext.
SSH command : `ssh dennis@<IP_ADDRESS>`

![dennismadeabobo](./dennis.png)

Got hold of first through fourth flags. `flag1.txt` was in `/home/dennis/`. Looked at `bash_history`(needed a hint here) and found third flag as part of it along with several other hints. 

Flag 2 was `flagTwo.txt`, somewhere. Found using `find / -name *flag* -type f 2>/dev/null`. Flag 4 was absent.

`sudo -l` told me `dennis` had access to `scp` without password. GTFOBINs gave me the command to get a reverse shell using `scp`. Found the root flag. i.e. `flag5.txt` in `/root/`.