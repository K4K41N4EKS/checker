from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from src.python.schemas.file_schema import FileUploadResponse, OperationItem, OperationStatus
from src.python.services import file_services
from src.python.dependencies.auth_stub import get_current_user
from src.python.database import get_db

router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    filename, operation_id = file_services.save_file(file, user_id=user["user_id"], db=db, background_tasks=background_tasks)
    return FileUploadResponse(
        filename=filename,
        download_url=f"/file/download/{operation_id}",
        user_id=user["user_id"],
        operation_id=operation_id
    )


@router.get("/download/{operation_id}")
async def download_file(operation_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    return file_services.get_file_response(operation_id, user_id=user["user_id"], db=db)


@router.get("/operations", response_model=list[OperationItem])
async def get_operations(
    status: OperationStatus | None = Query(default=None),
    sort_by: str | None = Query(default=None),
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return file_services.get_operations_by_user(user_id=user["user_id"], db=db, status_filter=status, sort_by=sort_by)
