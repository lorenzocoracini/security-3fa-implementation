import hashlib
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

import utils

app = FastAPI()

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

    utils.save_to_csv(
        header=["Name", "Cellphone", "Country", "Salt", "Key"],
        row=[name, phone, country, salt.hex(), key.hex()]
    )

    return JSONResponse({"message": "User registered", "data": data})

@app.post("/login")
async def login(request: Request):
    data = await request.json()

    name = data["name"]
    password = data["password"]
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

    return JSONResponse({"message": f"User {name} registered"})

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8888)
