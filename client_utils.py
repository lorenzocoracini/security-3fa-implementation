import hashlib
import base64

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

DATA_PATH = "data/user_data.csv"


def derive_key_pbkdf2(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=16,
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )
    return kdf.derive(password.encode())


def derive_key_scrypt(password, salt):
    key = hashlib.scrypt(
        password.encode(),
        salt=salt,
        n=16384,  # CPU/memory cost factor
        r=8,  # Tamanho do bloco
        p=1,  # Parallelization factor
        maxmem=0,
        dklen=16,  # Tamanho da chave derivada
    )

    return key


def encrypt_message(message, key, iv):
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(message.encode()) + encryptor.finalize()

    return {
        "ciphertext": base64.b64encode(ciphertext).decode(),
        "iv": base64.b64encode(iv).decode(),
        "tag": base64.b64encode(encryptor.tag).decode(),
    }
