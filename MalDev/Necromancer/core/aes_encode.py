from .dec_base import DecBase
from utils.helper import print_bytes_in_hex
from utils.fileops import print_output_to_file


class XorDecode(DecBase):
    """
    XOR Decoder
    Performs XOR decryption on byte data using a single-byte key.

    > xor dec <key:int> <data:hex>

    key -> 0-255
    data -> hex encoded string (e.g., '4a6f686e')
    """
    def __init__(self):
        self.__name__ = "XOR Decoder"
        self.data = None
        self.options = None
        pass

    def input_options(self, data, options={}):
        self.data = data
        self.options = options

    def decode(self):
        if not isinstance(self.data, bytes):
            raise TypeError("Data must be of type 'bytes'")
        if self.options is None and not isinstance(self.options, dict) and 'key' not in self.options:
            raise ValueError("Options must be a dictionary containing the 'key' parameter")
        
        key = self.options.get('key', 0x00)
        if not (0 <= key <= 255):
            raise ValueError("Key must be an integer between 0 and 255")
        
        print('Cipher text: ', end='')
        print_bytes_in_hex(self.data)

        decoded = bytearray()
        for byte in self.data:
            decoded.append(byte ^ key)
        
        print('Decoded plaintext: ', end='')
        print_bytes_in_hex(decoded)

        return bytes(decoded)