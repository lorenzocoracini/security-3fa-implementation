import hashlib
import os
import base64
import io
import qrcode
import logging
from datetime import datetime

import uvicorn
import pyotp
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

import utils


SESSION_KEY = "125868d23fb8b03613e3ee79d5486d77da47340a457c7da2c82dd4eed1599271"
FERNET_KEY = b"ZmDfcTF7_60GrrY167zsiPd67pEvs0aGOv2oasOM1Pg="

app = FastAPI()
fernet = Fernet(FERNET_KEY)
load_dotenv()
logger = logging.getLogger("uvicorn.error")


@app.post("/")
async def root(request: Request):
    data = await request.json()

    # Valida cookie da sessão
    session_cookie = request.cookies.get("session")
    if not session_cookie:
        return JSONResponse({"message": "Access denied"}, status_code=401)

    session_valid = utils.verify_data(session_cookie, SESSION_KEY)
    if not session_valid:
        return JSONResponse({"message": "Access denied"}, status_code=403)

    message = data["msg"]
    logger.info(f'Received message: "{message}"')

    return JSONResponse({"message": f"Received message: {message}"})


@app.post("/register")
async def register(request: Request):
    data = await request.json()

    name = data["name"]
    phone = data["phone"]
    password = data["password"]
    country = utils.get_user_local(data["ip"])

    salt = os.urandom(16)  # Inteiro aleatório de 16 digitos
    key = hashlib.scrypt(
        password.encode(),
        salt=salt,
        n=16384,  # CPU/memory cost factor
        r=8,  # Tamanho do bloco
        p=1,  # Parallelization factor
        maxmem=0,
        dklen=64,  # Tamanho da chave derivada
    )

    # Cria o secret TOTP
    totp_secret = pyotp.random_base32()

    encrypted_secret = fernet.encrypt(totp_secret.encode()).decode()

    utils.save_to_csv(
        header=["Name", "Cellphone", "Country", "Salt", "Key", "TOTPSecret"],
        row=[name, phone, country, salt.hex(), key.hex(), encrypted_secret],
    )

    totp_uri = pyotp.totp.TOTP(totp_secret).provisioning_uri(
        name, issuer_name="Trab3FA"
    )

    # Gera QR Code em imagem PNG
    qr = qrcode.make(totp_uri)
    buffered = io.BytesIO()
    qr.save(buffered, format="PNG")
    qr_b64 = base64.b64encode(buffered.getvalue()).decode()

    return JSONResponse(
        {
            "message": "User registered",
            "data": data,
            "totp_qr_code": qr_b64,
            "totp_uri": totp_uri,
        }
    )


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
        dklen=64,
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

    # Gera cookie assinado e seta na sessão do usuário
    cookie = f"{user['Name']}:{int(datetime.now().timestamp())}"
    signed_cookie = utils.sign_data(cookie, SESSION_KEY)

    response = JSONResponse({"message": f"User {name} registered"})
    response.set_cookie(key="session", value=signed_cookie, httponly=True)

    return response


@app.post("/logout")
async def logout(request: Request):
    response = JSONResponse({"message": "Logged out successfully."})
    response.delete_cookie("session")

    return response


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8888)
