
# audio_stego.py
# LSB steganography for 16-bit PCM WAV files
import wave
import numpy as np

DELIM = '0' * 16  # same delimiter as image stego

def _str_to_bits(s: str) -> str:
    return ''.join(f'{ord(c):08b}' for c in s)

def _bits_to_str(b: str) -> str:
    chars = [b[i:i+8] for i in range(0, len(b), 8)]
    return ''.join(chr(int(byte, 2)) for byte in chars)

def _ensure_capacity(num_samples: int, bits_len: int) -> bool:
    return bits_len <= num_samples

def embed_text_in_wav(in_wav: str, out_wav: str, message: str):
    with wave.open(in_wav, 'rb') as wf:
        if wf.getsampwidth() != 2:
            raise ValueError("Only 16-bit PCM WAV is supported")
        params = wf.getparams()
        frames = wf.readframes(wf.getnframes())

    # Convert to numpy int16 array
    samples = np.frombuffer(frames, dtype=np.int16).copy()

    bits = _str_to_bits(message) + DELIM
    if not _ensure_capacity(samples.size, len(bits)):
        raise ValueError("Audio doesn't have enough capacity for message")

    # Embed into LSB of samples
    bit_idx = 0
    for i in range(samples.size):
        if bit_idx >= len(bits):
            break
        samples[i] = (samples[i] & ~1) | int(bits[bit_idx])
        bit_idx += 1

    # Write back
    with wave.open(out_wav, 'wb') as out:
        out.setparams(params)
        out.writeframes(samples.tobytes())

    return out_wav

def extract_text_from_wav(wav_path: str) -> str:
    with wave.open(wav_path, 'rb') as wf:
        if wf.getsampwidth() != 2:
            raise ValueError("Only 16-bit PCM WAV is supported")
        frames = wf.readframes(wf.getnframes())

    samples = np.frombuffer(frames, dtype=np.int16)
    bits = ''.join(str(int(s & 1)) for s in samples)

    if DELIM in bits:
        bits = bits.split(DELIM)[0]
    else:
        raise ValueError("No hidden message found (delimiter missing)")

    return _bits_to_str(bits)
