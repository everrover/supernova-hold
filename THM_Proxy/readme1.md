# [THM Proxy](https://tryhackme.com/room/proxy)

VM crashed, lost all logs.

Here's what I remember:

- Found kerberos service running on target, via `nmap` scan
- Found `kerberos` user guest is allowed to login
- Ran `enum4linux` and found hosted shares, including `IT-Shared`
- Found `IT-Shared` folder on the target, with text files
  - `svc.scanner` runs every 2 minutes, adding files to the shares
  - Also found credentials in the text files, but they were useless
  - And a webpage, but of no significance
- Scanned for SIDs using `impacket-lookupsid`
- Created a reverse shell on my machine and and used `smbclient` to connect to the share, executed put command to upload the reverse shell
- `responder` service was running on my own, in separate instance
  - Got a capture there
  - BFed it using `john` and got the password
- Ran `bloodhound` to map the network, added the found nodes to `/etc/hosts` file. i remember one was `ctg.local` and the other was `dc1.ctg.local`. 2 more nodes were found ...
- `constrained` delegation was found, so attempted impersonation of the `Administrator` user, using `impacket-getST` and got the TGT
- `impacket-secretsdump` was used to dump the hashes, and got the `Administrator` hash
- Got in via `evil-winrm`, and found the flags

While I was on Reddit afterwards, i found a post that like easter eggs in games, there are easter eggs in similar activities, and the author of the post had kept their setup files accessible with hidden stuff. Like how they setup rooms and more.

Will have post-exploitation shenanigans next time onwards!