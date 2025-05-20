import csv
import requests
import hmac
import hashlib
import base64

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
