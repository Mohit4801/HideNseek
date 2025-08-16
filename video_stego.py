
# video_stego.py
# Simple LSB steganography for videos using OpenCV.
# Embeds message bits into the LSB of the Blue channel across frames.
import cv2
import numpy as np

DELIM = '0' * 16

def _str_to_bits(s: str) -> str:
    return ''.join(f'{ord(c):08b}' for c in s)

def _bits_to_str(b: str) -> str:
    chars = [b[i:i+8] for i in range(0, len(b), 8)]
    return ''.join(chr(int(byte, 2)) for byte in chars)

def embed_text_in_video(in_video: str, out_video: str, message: str):
    cap = cv2.VideoCapture(in_video)
    if not cap.isOpened():
        raise ValueError("Cannot open input video")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # .avi for portability
    writer = cv2.VideoWriter(out_video, fourcc, fps, (width, height))

    bits = _str_to_bits(message) + DELIM
    bit_idx = 0
    total_capacity = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if bit_idx < len(bits):
            # Flatten blue channel
            B = frame[:, :, 0].copy()
            h, w = B.shape
            capacity = h * w
            total_capacity += capacity
            flat = B.flatten()
            for i in range(flat.size):
                if bit_idx >= len(bits):
                    break
                flat[i] = (flat[i] & ~1) | int(bits[bit_idx])
                bit_idx += 1
            B = flat.reshape((h, w))
            frame[:, :, 0] = B

        writer.write(frame)

    cap.release()
    writer.release()

    if bit_idx < len(bits):
        raise ValueError("Video doesn't have enough capacity for message")

    return out_video

def extract_text_from_video(video_path: str) -> str:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Cannot open video")

    bits = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        B = frame[:, :, 0]  # Blue channel
        flat = B.flatten()
        bits.extend([str(int(px & 1)) for px in flat])

        # Check delimiter early to stop reading too much
        if len(bits) >= 16:
            s = ''.join(bits)
            if DELIM in s:
                bits = s.split(DELIM)[0]
                cap.release()
                return _bits_to_str(bits)

    cap.release()
    s = ''.join(bits)
    if DELIM in s:
        s = s.split(DELIM)[0]
        return _bits_to_str(s)
    raise ValueError("No hidden message found (delimiter missing)")
