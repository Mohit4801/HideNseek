# security.py
import base64, os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

def password_to_key(password: str, salt: bytes):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=200_000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def encrypt_message(message: str, password: str) -> str:
    salt = os.urandom(16)
    key = password_to_key(password, salt)
    f = Fernet(key)
    token = f.encrypt(message.encode())
    return base64.b64encode(salt + token).decode()

def decrypt_message(token_b64: str, password: str) -> str:
    raw = base64.b64decode(token_b64)
    salt, token = raw[:16], raw[16:]
    key = password_to_key(password, salt)
    f = Fernet(key)
    return f.decrypt(token).decode()
