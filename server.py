import hashlib
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import pyotp
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import base64
import io
import qrcode

import utils

app = FastAPI()

load_dotenv()

FERNET_KEY = os.getenv("FERNET_KEY")
fernet = Fernet(FERNET_KEY)

@app.post("/register")
async def register(request: Request):
    data = await request.json()

    name = data["name"]
    phone = data["phone"]
    password = data["password"]
    country = utils.get_user_local(data["ip"])

    salt = os.urandom(16) # Inteiro aleatório de 16 digitos
    key = hashlib.scrypt(
        password.encode(),
        salt=salt,
        n=16384,            # CPU/memory cost factor
        r=8,                # Tamanho do bloco
        p=1,                # Parallelization factor
        maxmem=0,
        dklen=64            # Tamanho da chave derivada
    )

    # Cria o secret TOTP    
    totp_secret = pyotp.random_base32()

    encrypted_secret = fernet.encrypt(totp_secret.encode()).decode()

    utils.save_to_csv(
        header=["Name", "Cellphone", "Country", "Salt", "Key", "TOTPSecret"],
        row=[name, phone, country, salt.hex(), key.hex(), encrypted_secret]
    )

    totp_uri = pyotp.totp.TOTP(totp_secret).provisioning_uri(name, issuer_name="Trab3FA")

    # Gera QR Code em imagem PNG
    qr = qrcode.make(totp_uri)
    buffered = io.BytesIO()
    qr.save(buffered, format="PNG")
    qr_b64 = base64.b64encode(buffered.getvalue()).decode()

    return JSONResponse({
        "message": "User registered",
        "data": data,
        "totp_qr_code": qr_b64,
        "totp_uri": totp_uri
    })

@app.post("/login")
async def login(request: Request):
    data = await request.json()

    name = data["name"]
    password = data["password"]
    totp_token = data.get("totp_token")  # O token TOTP que o cliente vai enviar
    country = utils.get_user_local(data["ip"])

    user = utils.get_user_by_name(name)
    if not user:
        return JSONResponse({"message": "Unknown user"}, status_code=404)

    if country != user["Country"]:
        return JSONResponse({"message": "Access denied"}, status_code=403)

    stored_salt = bytes.fromhex(user["Salt"])
    stored_key = user["Key"]

    # Derive chave a partir da senha enviada e do salt guardado
    derived_key = hashlib.scrypt(
        password.encode(),
        salt=stored_salt,
        n=16384,
        r=8,
        p=1,
        maxmem=0,
        dklen=64
    )

    if derived_key.hex() != stored_key:
        return JSONResponse({"message": "Access denied"}, status_code=403)
    
    encrypted_secret = user["TOTPSecret"]
    decrypted_secret = fernet.decrypt(encrypted_secret.encode()).decode()

    totp = pyotp.TOTP(decrypted_secret)
    if not totp_token:
        return JSONResponse({"message": "Missing TOTP token"}, status_code=403)
    elif totp.verify(totp_token):
        return JSONResponse({"message": "Invalid TOTP token"}, status_code=403)


    return JSONResponse({"message": f"User {name} registered"})

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8888)


