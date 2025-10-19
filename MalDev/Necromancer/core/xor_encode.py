from .enc_base import EncBase
from utils.helper import print_bytes_in_hex

class XorEncode(EncBase):
    def __init__(self):
        self.__name__ = "XOR Encoder"
        self.data = None
        self.options = None
        pass

    def input_options(self, data, options={}):
        self.data = data
        self.options = options

    def encode(self):
        if not isinstance(self.data, bytes):
            raise TypeError("Data must be of type 'bytes'")
        
        if self.options is None and not isinstance(self.options, dict) and 'key' not in self.options:
            raise ValueError("Options must be a dictionary containing the 'key' parameter")
        
        print('Plaintext: ', end='')
        print_bytes_in_hex(self.data)

        key = self.options.get('key', 0x00)
        if not (0 <= key <= 255):
            raise ValueError("Key must be an integer between 0 and 255")
        
        encoded = bytearray()
        for byte in self.data:
            encoded.append(byte ^ key)

        print('Cipher text: ', end='')
        print_bytes_in_hex(encoded)

        return bytes(encoded)