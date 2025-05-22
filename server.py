import secrets
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

import server_utils as utils


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

    session_cookie = utils.verify_data(session_cookie, SESSION_KEY)
    if not session_cookie:
        return JSONResponse({"message": "Access denied"}, status_code=403)

    username = session_cookie.split(":")[0]
    user = utils.get_user_by_name(username)
    if not user:  # Verifica se o usuário existe
        return JSONResponse({"message": "Access denied"}, status_code=403)

    # Verifica código TOTP
    encrypted_secret = user["TOTPSecret"]
    decrypted_secret = fernet.decrypt(encrypted_secret.encode()).decode()

    totp = pyotp.TOTP(decrypted_secret)
    if not (data["totp_token"] and totp.verify(data["totp_token"])):
        return JSONResponse({"message": "Invalid TOTP token"}, status_code=400)

    ciphertext = base64.b64decode(data["ciphertext"])
    tag = base64.b64decode(data["tag"])
    salt = base64.b64decode(data["salt"])

    # Deriva chave e IV a partir do código TOTP e salt
    key = utils.derive_key_scrypt(data["totp_token"], salt)
    iv = utils.derive_key_pbkdf2(data["totp_token"], salt)

    try:
        message = utils.decrypt_message(ciphertext, key, iv, tag).decode()
        logger.info(f"Received message: {message}")
        return JSONResponse({"message": f"Received message: {message}"})
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        return JSONResponse({"message": "Bad Request"}, status_code=400)


@app.post("/register")
async def register(request: Request):
    data = await request.json()

    name = data["name"]
    phone = data["phone"]
    password = data["password"]
    country = utils.get_user_local(data["ip"])

    salt = secrets.token_bytes(16)
    key = utils.derive_key_scrypt(password, salt)

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
    derived_key = utils.derive_key_scrypt(password, stored_salt)

    if derived_key.hex() != stored_key:
        return JSONResponse({"message": "Access denied"}, status_code=403)

    encrypted_secret = user["TOTPSecret"]
    decrypted_secret = fernet.decrypt(encrypted_secret.encode()).decode()

    totp = pyotp.TOTP(decrypted_secret)
    if not (totp_token and totp.verify(totp_token)):
        return JSONResponse({"message": "Invalid TOTP Token"}, status_code=400)

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
