# stego.py
from PIL import Image
from utils import _str_to_bits, _bits_to_str

def _ensure_capacity(img, message_bits_len):
    w, h = img.size
    capacity = w * h * 3
    return message_bits_len <= capacity

def embed_message(in_path: str, out_path: str, message: str):
    img = Image.open(in_path).convert('RGB')
    bits = _str_to_bits(message)
    bits += '0' * 16  # delimiter
    if not _ensure_capacity(img, len(bits)):
        raise ValueError("Image doesn't have enough capacity for message")

    pixels = list(img.getdata())
    new_pixels = []
    bit_idx = 0
    for px in pixels:
        r, g, b = px
        r = (r & ~1) | (int(bits[bit_idx]) if bit_idx < len(bits) else 0); bit_idx += 1 if bit_idx < len(bits) else 0
        g = (g & ~1) | (int(bits[bit_idx]) if bit_idx < len(bits) else 0); bit_idx += 1 if bit_idx < len(bits) else 0
        b = (b & ~1) | (int(bits[bit_idx]) if bit_idx < len(bits) else 0); bit_idx += 1 if bit_idx < len(bits) else 0
        new_pixels.append((r, g, b))

    # if there are leftover pixels (shouldn't be), append them
    if len(new_pixels) < len(pixels):
        new_pixels.extend(pixels[len(new_pixels):])

    stego = Image.new(img.mode, img.size)
    stego.putdata(new_pixels)
    stego.save(out_path, format='PNG')
    return out_path

def extract_message(stego_path: str):
    img = Image.open(stego_path).convert('RGB')
    pixels = list(img.getdata())
    bits = ''
    for r, g, b in pixels:
        bits += str(r & 1)
        bits += str(g & 1)
        bits += str(b & 1)
    delim = '0' * 16
    if delim in bits:
        bits = bits.split(delim)[0]
    else:
        raise ValueError("No hidden message found (delimiter missing)")
    return _bits_to_str(bits)
