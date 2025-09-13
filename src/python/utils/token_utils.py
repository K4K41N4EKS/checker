import os
from datetime import datetime

import jwt
from fastapi import HTTPException
from jwt import PyJWTError

from src.python.utils.logger_utils import get_logger

SECRET_KEY = os.getenv("AUTH_SECRET_KEY")
ALGORITHM = "HS256"
logger = get_logger("utils.auth_token")


def decode_token(token: str) -> dict:
    """Decode JWT and validate essential claims.

    Returns payload dict or raises HTTPException 401.
    """
    logger.debug(f"[DECODE START] token_preview={token[:10]}...")

    if not SECRET_KEY:
        logger.error("[DECODE ERROR] AUTH_SECRET_KEY is not configured")
        raise HTTPException(status_code=500, detail="Auth is not configured")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username")

        if not username:
            logger.warning(f"[DECODE FAIL] Token missing username: {token[:10]}...")
            raise HTTPException(status_code=401, detail="Invalid token: no username")

        logger.info(f"[DECODE SUCCESS] username={username}")
        return payload

    except PyJWTError as e:
        logger.error(f"[DECODE ERROR] Token={token[:10]}... | Error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")

