import os
import csv
import requests
import hmac
import hashlib
import base64

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

DATA_PATH = "data/user_data.csv"


def sign_data(data, key):
    data_bytes = data.encode()
    signature = hmac.new(key.encode(), data_bytes, hashlib.sha256).digest()
    signed_data = base64.urlsafe_b64encode(data_bytes).decode()
    signed_sig = base64.urlsafe_b64encode(signature).decode()

    return f"{signed_data}.{signed_sig}"


def verify_data(token, key):
    try:
        encoded_data, encoded_sig = token.split(".")
        data = base64.urlsafe_b64decode(encoded_data.encode())
        sig = base64.urlsafe_b64decode(encoded_sig.encode())
        expected_sig = hmac.new(key.encode(), data, hashlib.sha256).digest()
        if hmac.compare_digest(sig, expected_sig):
            return data.decode()
    except Exception:
        return None


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


def encrypt_message(message, key):
    iv = os.urandom(16)  # Generate a random IV
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(message.encode()) + encryptor.finalize()

    return {
        "ciphertext": base64.b64encode(ciphertext).decode(),
        "iv": base64.b64encode(iv).decode(),
        "tag": base64.b64encode(encryptor.tag).decode(),
    }


def decrypt_message(ciphertext, key, iv, tag):
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
    decryptor = cipher.decryptor()
    message = decryptor.update(ciphertext) + decryptor.finalize()

    return message


def get_user_local(ip):
    # https://ip-api.com/docs/api:json
    response = requests.get(f"http://ip-api.com/json/{ip}")

    if response.status_code == 200:
        data = response.json()
        country = data.get("country")
        if country:
            return country
    else:
        return None


def get_user_by_name(name):
    with open(DATA_PATH, newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row["Name"].lower() == name.lower():
                return row


def save_to_csv(header, row):
    with open(DATA_PATH, mode="a", newline="") as file:
        writer = csv.writer(file)

        if file.tell() == 0:
            writer.writerow(header)

        writer.writerow(row)
