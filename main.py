from register_user import RegisterUser
import requests


def get_user_information():
    print('---- Welcome!!! ----')
    print('Register!')
    name = input('Name:')
    cellphone = input('CellPhone:')
    password = input('Password:')
    ip = requests.get('https://api.ipify.org').text    
    return name, cellphone, password, ip

def register_user():
    name, cellphone, password, ip = get_user_information()
    RegisterUser(name=name, cellphone=cellphone, password=password, ip=ip).execute()


register_user()