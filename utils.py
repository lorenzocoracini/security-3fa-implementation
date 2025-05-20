import csv
import requests
import hashlib
import os

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

def password_key_derivation(password):
    salt = os.urandom(16)

    key = hashlib.scrypt(
        password.encode(),  # Convert password to bytes
        salt=salt,          # Use the generated salt
        n=16384,            # CPU/memory cost factor
        r=8,                # Block size
        p=1,                # Parallelization factor
        maxmem=0,           # Maximum memory usage (0 for no limit)
        dklen=64            # Length of the derived
    )

    return salt, key

def save_to_csv(filename, header, row):
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)

        if file.tell() == 0:
            writer.writerow(header)

        writer.writerow(row)
