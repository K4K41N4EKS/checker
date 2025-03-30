import jwt
from jwt import PyJWTError
from datetime import datetime
from fastapi import HTTPException
import os

from src.python.utils.logger_utils import get_logger

SECRET_KEY = os.getenv("AUTH_SECRET_KEY")
ALGORITHM = "HS256"
logger = get_logger("utils.auth")

def decode_token(token: str) -> dict:
    logger.debug(f"[DECODE START] token_preview={token[:10]}...")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username")

        if username is None:
            logger.warning(f"[DECODE FAIL] Token без username: {token[:10]}...")
            raise HTTPException(status_code=401, detail="Invalid token: no username")

        logger.info(f"[DECODE SUCCESS] username={username}")
        return payload

    except PyJWTError as e:
        logger.error(f"[DECODE ERROR] Token={token[:10]}... | Error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")
