import csv
import hashlib
import os
import requests

class RegisterUser:
    def __init__(self, name, cellphone, password, ip):
        self._name = name
        self._cellphone = cellphone
        self._password = password
        self._ip = ip   
    
    def _get_user_local(self,ip):
        # https://ip-api.com/docs/api:json
        response = requests.get(f"http://ip-api.com/json/{ip}")  
        if response.status_code == 200:
            data = response.json()
            _country = data.get("country")
            if _country:
                print(_country)
                self._country = _country
                return _country
        else:
            print('None')
            return None
        
    def _password_key_derivation(self, password):        
        salt = os.urandom(16)
        
        key = hashlib.scrypt(
            password.encode(),  # Convert password to bytes
            salt=salt,          # Use the generated salt
            n=16384,            # CPU/memory cost factor
            r=8,                # Block size
            p=1,                # Parallelization factor
            maxmem=0,          # Maximum memory usage (0 for no limit)
            dklen=64            # Length of the derived 
        )
        
        print('salt ->', salt.hex())
        print('key ->', key.hex())
        self._key = key
        self._salt = salt
        return salt + key

    def _save_to_csv(self, filename):
        with open(filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            if file.tell() == 0:
                writer.writerow(['Name', 'Cellphone', 'Country', 'Salt', 'Key'])
            writer.writerow([
                self._name,
                self._cellphone,
                self._country,
                self._salt.hex(),
                self._key.hex()
            ])


    
    def execute(self):
        self._get_user_local(self._ip)
        self._password_key_derivation(self._password)
        self._save_to_csv(filename='data/user_data.csv')
        
        
