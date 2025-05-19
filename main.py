from register_user import RegisterUser

def get_user_information():
    pass

def register_user(nome, celular, senha, ip):
    RegisterUser(nome=nome, celular=celular, senha=senha, ip=ip).execute()
