from sqlalchemy.orm import Session
from src.python.models.user import User
from fastapi import HTTPException
from src.python.utils.logger_utils import get_logger

logger = get_logger("services.user_sync")


def sync_user(user_id: str, username: str, db: Session) -> None:
    """
    Сохраняет пользователя в базу.
    Предполагается, что auth-сервис уже проверил уникальность.
    Повторный вызов безопасен.
    """
    try:
        existing = db.query(User).filter_by(id=user_id).first()
        if existing:
            logger.info(f"[SYNC USER] User already exists: id={user_id}, username='{existing.username}'")
            return

        user = User(id=user_id, username=username)
        db.add(user)
        db.commit()
        logger.info(f"[SYNC USER] New user synced: id={user_id}, username='{username}'")
    except Exception as e:
        db.rollback()
        logger.error(f"[SYNC USER ERROR] id={user_id}, username='{username}' | Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Ошибка при синхронизации пользователя")
