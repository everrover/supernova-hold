# Necromancer application

### Description : An encoding/decoding tool for byte and string shell payloads

### Author : @everrover

**Windows**

```ps
python3 -m venv venv
.\venv\Scripts\activate
pip install -r req.txt

cd necromancer # navigate to the necromancer directory
python cli.py
```

**Linux**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r req.txt
cd necromancer # navigate to the necromancer directory

python cli.py
```

### Commands

```shell
list        - List all available encoding/decoding methods

help <command> - Show help for a specific command
Use: help xor enc

```

### Specific Commands

```txt
xor [enc/dec] - Encode/Decode using XOR
> -f - Input file
> -s - Input string(default)
> -k - Key (default: 0xAA)
> -o - Output file(default: print to console, outputs the file in parent of root directory)
Use: xor dec "string to decode" -k 0xAC
     xor enc -f "filename-relative-path" -k 0xDA -o "output-filename-relative-path"

aes [enc/dec] - Encode/Decode using AES
> -f - Input file
> -s - Input string(default)
> -k - Key (default: 0123456789abcdef)
> -iv - Initialization Vector (default: 0123456789abcdef)
> -o - Output file(default: print to console, outputs the file in parent of root directory)
Use: aes dec "string to decode" -k "key" -iv "initialization vector"
     aes enc -f "filename-relative-path" -k "key" -iv "initialization vector" -o "output-filename-relative-path"

```

