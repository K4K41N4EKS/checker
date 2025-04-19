import os
import shutil
import uuid
from datetime import datetime
from fastapi import UploadFile, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from docx import Document

from src.python.utils.docx_zip_comments import add_comments_to_docx_batch
from src.python.database.database import SessionLocal
from src.python.models.operation import Operation, OperationStatus
from src.python.utils.logger_utils import get_logger
from src.python.services.template_services import get_templates, get_template_by_id
from python.utils.document_analyzer.core import check_document_format

logger = get_logger("services.file_services")

UPLOAD_FOLDER = "uploaded_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def save_file(file: UploadFile, user_id: int, db: Session, background_tasks: BackgroundTasks, template_id: str | None = None):
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

        background_tasks.add_task(process_file_task, file_path, operation.id, template_id)

        logger.info(f"[SAVE FILE] User {user_id} uploaded {safe_filename} -> {unique_name} (operation_id={operation.id})")
        return unique_name, operation.id

    except Exception as e:
        logger.error(f"[SAVE FILE ERROR] User {user_id} | File: {safe_filename} | Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Ошибка при сохранении файла")


def process_file_task(input_path: str, operation_id: int, template_id: str | None = None):
    db = SessionLocal()
    try:
        operation = db.query(Operation).filter(Operation.id == operation_id).first()
        if not operation:
            logger.error(f"[PROCESS FILE] Operation {operation_id} not found")
            return

        operation.status = OperationStatus.processing
        db.commit()

        # Шаблон
        if template_id:
            template = get_template_by_id(db, template_id, operation.user_id)
        else:
            templates = get_templates(db, str(operation.user_id))
            template = templates[0] if templates else None

        if not template:
            logger.warning(f"[NO TEMPLATE FOUND] operation_id={operation_id}")
            errors = []
        else:
            template_filters = template.filters or {}
            errors = check_document_format(input_path, template_filters)

        base_path, ext = os.path.splitext(input_path)
        result_path = base_path + "_result.docx"

        # Копия оригинала
        Document(input_path).save(result_path)

        # Вставка всех комментариев за один проход
        if errors:
            try:
                add_comments_to_docx_batch(result_path, errors)
            except Exception as comment_err:
                logger.warning(f"[COMMENT ERROR] operation_id={operation_id} | {comment_err}")

        # Запись в БД
        user_folder = os.path.basename(os.path.dirname(result_path))
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
