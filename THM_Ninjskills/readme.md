# [Ninja Skills](https://tryhackme.com/room/ninjaskills)

```bash
# found files with group-name
find / \( -name 8V2L -o -name bny0 -o -name c4ZX -o -name D8B3 -o -name FHl1 -o -name oiM0 -o -name PFbD -o -name rmfX -o -name SRSq -o -name uqyw -o -name v2Vb -o -name X1Uy \) -group best-group 2>/dev/null | grep -v "Permission"
find / \( -name 8V2L -o -name bny0 -o -name c4ZX -o -name D8B3 -o -name FHl1 -o -name oiM0 -o -name PFbD -o -name rmfX -o -name SRSq -o -name uqyw -o -name v2Vb -o -name X1Uy \) 2>/dev/null | grep -v "Permission" > ./files.txt

# i put down all the file names to a file called files.txt
grep -lE '([0-9]{1,3}\.){3}[0-9]{1,3}' -- $(< files.txt) 2>/dev/null

# the silver bullet is -exec
find / \( -name 8V2L -o -name bny0 -o -name c4ZX -o -name D8B3 -o -name FHl1 -o -name oiM0 -o -name PFbD -o -name rmfX -o -name SRSq -o -name uqyw -o -name v2Vb -o -name X1Uy \) -exec ls -ln {} \; 2>/dev/null | grep -v "Permission"
# sha1sum
# wc -l
# ls -al | grep "rwx|r-x|-wx"
```