import sys
from utils.helper import print_help
from utils.suggest import suggest_command
from utils.fileops import read_input_from_file, print_output_to_file

from core.xor_encode import XorEncode
from core.xor_decode import XorDecode
# from core.aes_encryptor import AESEncryptor
# from core.aes_decryptor import AESDecryptor
import argparse

xorenc = XorEncode()
xordec = XorDecode()
aesenc = None
aesdec = None

parser = argparse.ArgumentParser(description='Necromancer')

parser.add_argument('action', choices=['xor', 'aes', 'help', 'exit', 'list'], help='Action to perform')
parser.add_argument('mode', choices=['enc', 'dec'], help='Method to use', nargs='?')
parser.add_argument('-df', '--data-format', type=str, choices=['str', 'hex', '0x'], help='Input data format (str/hex)', nargs='?', dest='data_format', default='str')
parser.add_argument('-f', '--file', type=str, help='File to process(If absent, reads from stdin) | Take a note of file format', nargs='?', dest='ip_file')
# parser.add_argument('-s', '--hexstr', type=str, help='Hex string to process')
parser.add_argument('-k', '--key', type=int, help='Key for encryption/decryption (default: 0xA1=161)', dest='key', default=0xA1)
parser.add_argument('-o', '--output', type=str, help='Output file to save results(Default: stdout)', nargs='?', dest='op_file')
parser.add_argument('-iv', '--init-vec', type=str, help='Initialization vector for AES(Default: `0123456789abcdef)', nargs='?', dest='iv')

def injection():
    global xorenc, xordec
    if xorenc is None:
        xorenc = XorEncode()
    if xordec is None:
        xordec = XorDecode()
    # Placeholder for AES encryptor/decryptor initialization
    # if aesenc is None:
    #     aesenc = AESEncryptor()
    # if aesdec is None:
    #     aesdec = AESDecryptor()

def parse_command(cmd):
    
    args = parser.parse_args(cmd.split())

    if args.action in ['help', 'exit', 'list']:
        return args.action, None, None
    
    if args.mode not in ['enc', 'dec']:
        print("⚠️  Mode (enc/dec) is required for encryption/decryption operations")
        return None, None, None
    
    if not args.ip_file:
        data = input("Enter data (as bytes): ").encode()
    else:
        data = read_input_from_file(args.ip_file, args.data_format)
        if not data:
            print(f"⚠️  Failed to read data from file '{args.ip_file}'")
            return None, None, None
    args.data = data        
    
    if args.key is None:
        print("⚠️  Key is required for encode/decode operations")
        return None, None, None
    
    return args.action, args.mode, vars(args)

def main():
    print("Necromancer")
    print("🔐 Modular Encryption/Decryption CLI Tool 🔐")
    # print_help()

    injection()

    while True:
        try:
            cmd = input("\n> Enter command: ").strip().lower()
            action, mode, options = parse_command(cmd)
            # print(action, mode, options)

            if action == 'xor':
                if mode == 'enc':
                    xorenc.input_options(options['data'], options)
                    op = xorenc.encode()
                elif mode == 'dec':
                    xordec.input_options(options['data'], options)
                    op = xordec.decode()
                else:
                    print(f"⚠️  Unknown encryption method '{mode}'. Currently only 'xor' is supported.")
                
                if options['op_file'] is not None and op is not None:
                        print_output_to_file(op, options['op_file'])

            elif cmd == 'help':
                print_help()

            elif cmd == 'exit':
                print("Goodbye dawg!")
                sys.exit(0)

            else:
                suggestion = suggest_command(cmd)
                if suggestion:
                    print(f"⚠️  Unknown command '{cmd}'. Did you mean '{suggestion}'?")
                else:
                    print(f"⚠️  Unknown command '{cmd}'. Type 'help' for available commands.")
        except KeyboardInterrupt:
            print("\nGoodbye dawg!")
            sys.exit(0)
        except Exception as e:
            print(f"⚠️  Error: {e}")

if __name__ == '__main__':
    main()
