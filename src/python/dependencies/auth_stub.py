from fastapi import Depends, Header, HTTPException

def get_current_user(authorization: str = Header(default="Bearer testtoken")):
    """
    Заглушка для получения user_id по токену.
    Позже будет запрос в auth-сервис.
    """
    if authorization != "Bearer testtoken":
        raise HTTPException(status_code=401, detail="Невалидный токен")

    return {"user_id": 1}  # заглушка
