import jwt
from jwt import PyJWTError
from datetime import datetime
from fastapi import HTTPException, status
import os

SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "changeme")
ALGORITHM = "HS256"

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token: no username")

        return payload

    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
