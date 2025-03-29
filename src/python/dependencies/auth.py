from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from src.python.database.database import get_db
from src.python.models.user import User
from src.python.utils.token_utils import decode_token

security = HTTPBearer()

def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = creds.credentials
    payload = decode_token(token)

    username = payload.get("username")
    if not username:
        raise HTTPException(status_code=401, detail="Username not found in token")

    user = db.query(User).filter_by(username=username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"user_id": user.id, "username": user.username}
