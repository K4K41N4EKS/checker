from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks, Query, HTTPException, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from src.python.schemas.file_schema import FileUploadResponse, OperationItem, OperationStatus
from src.python.services import file_services
from python.dependencies.auth import get_current_user
from src.python.database import get_db
from src.python.utils.logger_utils import get_logger
import os

logger = get_logger("routers.file_actions")

router = APIRouter(prefix="/files", tags=["Files"])

MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_EXTENSIONS = {".docx", ".pdf"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
}

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    template_id: str = Query(default=None, description="ID шаблона оформления (опционально)"),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    ext = os.path.splitext(file.filename)[1].lower()
    mime = file.content_type
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "Unknown")

    if ext not in ALLOWED_EXTENSIONS or mime not in ALLOWED_MIME_TYPES:
        logger.warning(f"[UPLOAD BLOCKED] {user['username']} | {client_ip} | {file.filename} ({mime}) | User-Agent: {user_agent}")
        raise HTTPException(
            status_code=400,
            detail="Недопустимый файл: разрешены только .docx и .pdf с корректным типом."
        )

    try:
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            logger.warning(f"[UPLOAD BLOCKED - SIZE] {user['username']} | {client_ip} | {file.filename} ({len(contents)} bytes) | User-Agent: {user_agent}")
            raise HTTPException(
                status_code=413,
                detail=f"Файл слишком большой. Максимум: {MAX_FILE_SIZE_MB} МБ."
            )
        file.file.seek(0)

        filename, operation_id = file_services.save_file(
            file=file,
            user_id=user["user_id"],
            db=db,
            background_tasks=background_tasks,
            template_id=template_id
        )

        logger.info(f"[UPLOAD SUCCESS] {user['username']} | {client_ip} | {file.filename} => {filename} | operation_id={operation_id} | User-Agent: {user_agent}")
        return FileUploadResponse(
            filename=filename,
            download_url=f"/file/download/{operation_id}",
            user_id=user["user_id"],
            operation_id=operation_id
        )
    except Exception as e:
        logger.error(f"[UPLOAD ERROR] {user['username']} | {client_ip} | {file.filename} | Error: {str(e)} | User-Agent: {user_agent}")
        raise HTTPException(status_code=500, detail="Ошибка сервера при обработке файла.")

@router.get("/download/{operation_id}")
async def download_file(
    operation_id: int,
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    client_ip = request.client.host
    try:
        response = file_services.get_file_response(operation_id, user_id=user["user_id"], db=db)
        logger.info(f"[DOWNLOAD SUCCESS] {user['username']} | {client_ip} | operation_id={operation_id}")
        return response
    except Exception as e:
        logger.error(f"[DOWNLOAD ERROR] {user['username']} | {client_ip} | operation_id={operation_id} | Error: {str(e)}")
        raise

@router.get("/operations", response_model=list[OperationItem])
async def get_operations(
    request: Request,
    status: OperationStatus | None = Query(default=None),
    sort_by: str | None = Query(default=None),
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    client_ip = request.client.host
    try:
        operations = file_services.get_operations_by_user(
            user_id=user["user_id"],
            db=db,
            status_filter=status,
            sort_by=sort_by
        )
        logger.info(f"[OPERATIONS LIST] {user['username']} | {client_ip} | {len(operations)} операций возвращено")
        return operations
    except Exception as e:
        logger.error(f"[OPERATIONS ERROR] {user['username']} | {client_ip} | Error: {str(e)}")
        raise
