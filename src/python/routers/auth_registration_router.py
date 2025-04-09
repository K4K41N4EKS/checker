from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from src.python.database.database import get_db
from src.python.services.user_sync_services import sync_user
from src.python.utils.logger_utils import get_logger
import os

router = APIRouter()

logger = get_logger("routers.auth_sync")

INTERNAL_SECRET = os.getenv("INTERNAL_SERVICE_SECRET")
if not INTERNAL_SECRET:
    raise RuntimeError("INTERNAL_SERVICE_SECRET is not set!")

@router.post("/create_user", include_in_schema=False)
def create_user(request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host
    secret_header = request.headers.get("X-Internal-Secret")
    user_id = request.headers.get("user_id")
    username = request.headers.get("username")

    if secret_header != INTERNAL_SECRET:
        logger.warning(f"[FORBIDDEN] IP={client_ip} | Недопустимый секрет")
        raise HTTPException(status_code=403, detail="Forbidden")

    if not user_id or not username:
        logger.warning(f"[MISSING DATA] IP={client_ip} | user_id={user_id} | username={username}")
        raise HTTPException(status_code=400, detail="Missing user_id or username")

    try:
        sync_user(user_id=user_id, username=username, db=db)
        logger.info(f"[SYNC SUCCESS] IP={client_ip} | user_id={user_id} | username={username}")
    except Exception as e:
        db.rollback()
        logger.error(f"[SYNC ERROR] IP={client_ip} | user_id={user_id} | username={username} | Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")

    return JSONResponse(
        content={"detail": "User created"},
        status_code=status.HTTP_201_CREATED
    )
