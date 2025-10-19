def print_output_to_file(output: bytes, filename: str):
    try:
        with open(filename, 'wb') as f:
            # write output to file as space separated hex values, add new line after every 16 bytes
            for i in range(0, len(output), 16):
                line = ' '.join(f'0x{byte:02x},' for byte in output[i:i+16]) + '\n'
                f.write(line.encode())
        print(f"Output written to {filename}")
    except Exception as e:
        print(f"Error writing to file {filename}: {e}")

def read_input_from_file(filename: str, df: str) -> bytes:
    try:
        with open(filename, 'rb') as f:
            data = f.read()
        if df == 'str': # `Hello World`
            data = data.strip()
        elif df == 'hex': # `0a 1b 2c`
            data = bytes.fromhex(data.decode().strip())
        elif df == '0x': # `0x0a, 0x01, 0x2c`
            data = data.replace(b'\n', b'').strip()
            data = filter(lambda x: not x.strip() == '', [b for b in data.decode().strip().split(',')])
            data = bytes(int(b, 16) for b in data)

        return data
    except Exception as e:
        print(f"Error reading file {filename}: {e}")
        return b''