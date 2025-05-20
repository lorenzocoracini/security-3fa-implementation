import requests
import base64
import qrcode
from io import BytesIO

SERVER_URL = "http://localhost:8888"

def register():
    print("\n=== Register User ===")

    username = input("Username: ")
    phone = input("Phone: ")
    password = input("Password: ")
    ip = requests.get("https://api.ipify.org").text

    data = {
        "name": username,
        "phone": phone,
        "password": password,
        "ip": ip
    }

    try:
        response = requests.post(f"{SERVER_URL}/register", json=data)
        if response.status_code == 200:
            print("✅ Registration successful!")

            totp_uri = response.json().get("totp_uri")
            if totp_uri:
                qr = qrcode.QRCode()
                qr.add_data(totp_uri)
                qr.make(fit=True)
                print("\nScan this QR code with your authenticator app:\n")
                qr.print_ascii(invert=True)
            else:
                print("No TOTP URI received.")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")

def login():
    print("\n=== Login ===")

    username = input("Username: ")
    password = input("Password: ")
    totp_token = input("Código de acesso: ")
    ip = requests.get("https://api.ipify.org").text

    data = {
        "name": username,
        "password": password,
        "totp_token": totp_token,
        "ip": ip
    }

    try:
        response = requests.post(f"{SERVER_URL}/login", json=data)
        if response.status_code == 200:
            print("✅ Login successful!")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")

def main():
    while True:
        print("\n=== Main Menu ===")
        print("1. Register")
        print("2. Login")
        print("0. Exit")
        choice = input("Select an option: ")

        if choice == "1":
            register()
        elif choice == "2":
            login()
        elif choice == "0":
            break
        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    main()
