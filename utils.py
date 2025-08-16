# utils.py
def _str_to_bits(s: str) -> str:
    return ''.join(f'{ord(c):08b}' for c in s)

def _bits_to_str(b: str) -> str:
    chars = [b[i:i+8] for i in range(0, len(b), 8)]
    return ''.join(chr(int(byte, 2)) for byte in chars)
