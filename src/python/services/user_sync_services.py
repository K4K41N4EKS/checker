from sqlalchemy.orm import Session
from src.python.models.user import User

def sync_user(user_id: str, username: str, db: Session) -> None:
    """
    Сохраняет пользователя в базу.
    Предполагается, что auth-сервис уже проверил уникальность.
    """
    user = User(id=user_id, username=username)
    db.add(user)
    db.commit()
