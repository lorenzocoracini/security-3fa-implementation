import requests

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
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")

def main():
    while True:
        print("\n=== Main Menu ===")
        print("1. Register")
        print("0. Exit")
        choice = input("Select an option: ")

        if choice == "1":
            register()
        elif choice == "0":
            break
        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    main()
