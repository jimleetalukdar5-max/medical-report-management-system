from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
from config import Config

BLOCK_SIZE = 16

def pad(data):
    return data + b"\0" * (BLOCK_SIZE - len(data) % BLOCK_SIZE)

def unpad(data):
    return data.rstrip(b"\0")

def load_key():
    key_b64 = Config.AES_KEY_B64
    if not key_b64:
        raise ValueError("AES_KEY_B64 missing in config.py")
    return base64.b64decode(key_b64)

def encrypt_and_b64(data_bytes):
    key = load_key()
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(data_bytes))
    return (
        base64.b64encode(iv).decode("utf-8"),
        base64.b64encode(encrypted).decode("utf-8")
    )

def decrypt_from_b64(iv_b64, enc_b64):
    key = load_key()
    iv = base64.b64decode(iv_b64)
    encrypted = base64.b64decode(enc_b64)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(encrypted))
    return decrypted
