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
    country = utils.get_user_local(data["ip"])
    salt, key = utils.password_key_derivation(data["password"])

    utils.save_to_csv(
        "data/user_data.csv",
        header=["Name", "Cellphone", "Country", "Salt", "Key"],
        row=[name, phone, country, salt.hex(), key.hex()]
    )

    return JSONResponse({"message": "User registered", "data": data})

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8888)
