import requests

class RegisterUser:
    def __init__(self, nome, celular, senha, ip):
        self._nome = nome
        self._celular = celular
        self._senha = senha
        self._ip = ip
    
    def _get_user_local(self):
        response = requests.get(f"http://ip-api.com/json/{self._ip}")
        if response.status_code == 200:
            data = response.json()
            _country = data.get("country")
            if _country:
                self._country = _country

        else:
            return None
        
    def _password_key_derivation(self):
        pass
    
    def execute(self):
        self._get_user_local()
        
meu_ip = '189.4.104.246'
ip_franca = '91.160.93.4'
r = RegisterUser('Lorenzo', 222,123,ip=ip_franca)
print(r._get_user_local())
