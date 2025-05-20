import csv
import requests

DATA_PATH = "data/user_data.csv"

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
    with open(DATA_PATH, newline='') as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row["Name"].lower() == name.lower():
                return row

def save_to_csv(header, row):
    with open(DATA_PATH, mode='a', newline='') as file:
        writer = csv.writer(file)

        if file.tell() == 0:
            writer.writerow(header)

        writer.writerow(row)
