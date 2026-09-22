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

Sad part: No copy-paste allowed. Otherwise I prepared this(was to be modded, as req arose):

```bash
#!/usr/bin/env bash
#
# Search the filesystem for a fixed list of filenames, omitting any
# "Permission denied" lines from find's output.
#
# Usage:
#   ./find_files.sh [start_dir]
#
#   start_dir   Directory to start searching from (default: /)
#
# Example:
#   ./find_files.sh            # search the whole system
#   ./find_files.sh /home      # search only under /home
#   sudo ./find_files.sh       # run as root to avoid most permission errors

set -u

SEARCH_DIR="${1:-/}"

FILES=(
  "8V2L"
  "bny0"
  "c4ZX"
  "D8B3"
  "FHl1"
  "oiMO"
  "PFbD"
  "rmfX"
  "SRSq"
  "uqyw"
  "v2Vb"
  "X1Uy"
)

# Build a "-name A -o -name B -o ..." expression for find
NAME_EXPR=()
for f in "${FILES[@]}"; do
  if [ ${#NAME_EXPR[@]} -gt 0 ]; then
    NAME_EXPR+=(-o)
  fi
  NAME_EXPR+=(-name "$f")
done

find "$SEARCH_DIR" \( "${NAME_EXPR[@]}" \) 2>&1 | grep -v "Permission denied"
```