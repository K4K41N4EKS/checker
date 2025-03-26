from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from src.python.database.database import get_db
from src.python.services.user_sync_services import sync_user

router = APIRouter()

@router.post("/create_user")
def create_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.headers.get("user_id")
    username = request.headers.get("username")

    if not user_id or not username:
        raise HTTPException(status_code=400, detail="Missing user_id or username")

    try:
        sync_user(user_id=user_id, username=username, db=db)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")

    return JSONResponse(
        content={"detail": "User created"},
        status_code=status.HTTP_201_CREATED
    )
