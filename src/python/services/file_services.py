import os
import shutil
import uuid
from datetime import datetime
from fastapi import UploadFile, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from src.python.database.database import SessionLocal
from src.python.models.operation import Operation, OperationStatus
from src.python.utils.logger_utils import get_logger

logger = get_logger("services.file_services")

UPLOAD_FOLDER = "uploaded_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def save_file(file: UploadFile, user_id: int, db: Session, background_tasks: BackgroundTasks):
    safe_filename = os.path.basename(file.filename)
    unique_name = f"{uuid.uuid4()}_{safe_filename}"

    user_folder = os.path.join(UPLOAD_FOLDER, str(user_id))
    os.makedirs(user_folder, exist_ok=True)

    file_path = os.path.join(user_folder, unique_name)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        operation = Operation(
            file_name=unique_name,
            user_id=user_id,
            status=OperationStatus.uploaded,
            created_at=datetime.utcnow()
        )
        db.add(operation)
        db.commit()
        db.refresh(operation)

        background_tasks.add_task(process_file_task, file_path, operation.id)

        logger.info(f"[SAVE FILE] User {user_id} uploaded {safe_filename} -> {unique_name} (operation_id={operation.id})")
        return unique_name, operation.id

    except Exception as e:
        logger.error(f"[SAVE FILE ERROR] User {user_id} | File: {safe_filename} | Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Ошибка при сохранении файла")


def process_file_task(input_path: str, operation_id: int):
    db = SessionLocal()
    try:
        operation = db.query(Operation).filter(Operation.id == operation_id).first()
        if not operation:
            logger.error(f"[PROCESS FILE] Operation {operation_id} not found")
            return

        operation.status = OperationStatus.processing
        db.commit()

        base_path, ext = os.path.splitext(input_path)
        result_path = base_path + "_result.docx"

        try:
            shutil.copy(input_path, result_path)
        except Exception as e:
            operation.status = OperationStatus.error
            db.commit()
            logger.error(f"[PROCESS FILE COPY ERROR] operation_id={operation_id} | Error: {str(e)}")
            raise

        user_folder = os.path.basename(os.path.dirname(input_path))
        file_name = os.path.basename(result_path)
        operation.status = OperationStatus.done
        operation.result_path = os.path.join(user_folder, file_name)
        db.commit()

        logger.info(f"[PROCESS FILE DONE] operation_id={operation_id} | result={file_name}")

    except Exception as err:
        if 'operation' in locals() and operation:
            operation.status = OperationStatus.error
            db.commit()
        logger.error(f"[PROCESS FILE ERROR] operation_id={operation_id} | Error: {str(err)}")

    finally:
        db.close()


def get_file_response(operation_id: int, user_id: int, db: Session):
    operation = db.query(Operation).filter_by(id=operation_id, user_id=user_id).first()
    if not operation:
        logger.warning(f"[FILE DOWNLOAD BLOCKED] operation_id={operation_id} | user_id={user_id} | Not found")
        raise HTTPException(status_code=404, detail="Операция не найдена")

    if not operation.result_path:
        logger.warning(f"[FILE DOWNLOAD BLOCKED] operation_id={operation_id} | Result not ready")
        raise HTTPException(status_code=404, detail="Итоговый файл не готов или отсутствует")

    result_file_full_path = os.path.join(UPLOAD_FOLDER, operation.result_path)
    if not os.path.exists(result_file_full_path):
        logger.warning(f"[FILE MISSING] operation_id={operation_id} | Path: {result_file_full_path}")
        raise HTTPException(status_code=404, detail="Файл не найден")

    logger.info(f"[FILE DOWNLOAD SUCCESS] operation_id={operation_id} | user_id={user_id}")
    return FileResponse(result_file_full_path, filename=os.path.basename(result_file_full_path))


def get_operations_by_user(user_id: str, db: Session, status_filter=None, sort_by=None):
    query = db.query(Operation).filter(Operation.user_id == user_id)

    if status_filter:
        query = query.filter(Operation.status == status_filter)

    if sort_by == "date":
        query = query.order_by(Operation.created_at.desc())

    operations = query.all()
    logger.info(f"[LIST OPERATIONS] user_id={user_id} | count={len(operations)}")
    return operations
