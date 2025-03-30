from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from src.python.database.database import get_db
from src.python.models.user import User
from src.python.utils.token_utils import decode_token
from src.python.utils.logger_utils import get_logger

security = HTTPBearer()
logger = get_logger("auth", "auth.log")

def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = creds.credentials

    try:
        payload = decode_token(token)
        username = payload.get("username")

        if not username:
            logger.warning(f"[AUTH FAILED] Токен без username: {token[:20]}...")
            raise HTTPException(status_code=401, detail="Username not found in token")

        user = db.query(User).filter_by(username=username).first()
        if not user:
            logger.warning(f"[AUTH FAILED] Пользователь '{username}' не найден")
            raise HTTPException(status_code=404, detail="User not found")

        logger.info(f"[AUTH SUCCESS] Пользователь '{username}' прошел проверку")
        return {"user_id": user.id, "username": user.username}

    except Exception as e:
        logger.error(f"[AUTH ERROR] Ошибка при проверке токена: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid authentication")
