def print_help():
    print("""
Available commands:
  encrypt xor - Encrypt using XOR
  decrypt xor - Decrypt using XOR
  help        - Show this help message
  exit        - Exit the tool
""")


def print_str_in_hex(s):
    hex_output = ' '.join(f'{ord(c):02x}' for c in s)
    print(f"Hex: {hex_output}")

def print_bytes_in_hex(b: bytearray):
    hex_output = ' '.join(f'{byte:02x}' for byte in b)
    print(f"Hex: {hex_output}")