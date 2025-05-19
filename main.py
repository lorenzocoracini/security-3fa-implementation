from register_user import RegisterUser
import requests


def get_user_information():
    print('---- BEM VINDO!!!!!')
    print('Se cadaste a seguir!')
    nome = input('Digite seu nome:')
    celular = input('Digite seu celular:')
    senha = input('DIgite sua senha')
    ip = requests.get('https://api.ipify.org').text    
    return nome, celular, senha, ip

def register_user():
    nome, celular, senha, ip = get_user_information()
    RegisterUser(nome=nome, celular=celular, senha=senha, ip=ip).execute()


register_user()