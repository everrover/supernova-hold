import argparse
from pwn import *

leak = "0x80487d6"
leak = int(leak, 16)
info(f'leak: {hex(leak)}')
# leak: 0x80487d6

warn(f'leak 2: {flat(leak)}')
# \\xd6\\x87\\x04\\x08