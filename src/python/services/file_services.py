import os
import shutil
import uuid
from datetime import datetime
from fastapi import UploadFile, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from src.python.database.database import SessionLocal
from src.python.models.operation import Operation, OperationStatus

# Папка для хранения загруженных файлов
UPLOAD_FOLDER = "uploaded_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def save_file(file: UploadFile, user_id: int, db: Session, background_tasks: BackgroundTasks):
    """
    Сохраняет файл на диск и создает запись об операции в базе данных.
    Запускает фоновую задачу обработки файла.
    """
    unique_name = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    operation = Operation(
        file_name=unique_name,
        user_id=user_id,
        status=OperationStatus.uploaded,
        created_at=datetime.utcnow(),
    )

    db.add(operation)
    db.commit()
    db.refresh(operation)

    background_tasks.add_task(process_file_task, operation.id)

    return unique_name, operation.id


def process_file_task(operation_id: int):
    """
    Фоновая задача обработки файла — обновляет статус операции.
    """
    db = SessionLocal()
    try:
        operation = db.query(Operation).filter(Operation.id == operation_id).first()
        if operation:
            operation.status = OperationStatus.processing
            db.commit()

            import time
            time.sleep(3)

            operation.status = OperationStatus.done
            db.commit()
    except Exception:
        if operation:
            operation.status = OperationStatus.error
            db.commit()
    finally:
        db.close()


def get_file_response(operation_id: int, user_id: int, db: Session):
    """
    Возвращает файл, связанный с операцией по ID.
    """
    operation = db.query(Operation).filter_by(id=operation_id, user_id=user_id).first()
    if not operation:
        raise HTTPException(status_code=404, detail="Операция не найдена")

    file_path = os.path.join(UPLOAD_FOLDER, operation.file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден")

    return FileResponse(file_path, filename=operation.file_name)


def get_operations_by_user(user_id: int, db: Session, status_filter=None, sort_by=None):
    """
    Возвращает список операций пользователя с возможностью фильтрации и сортировки.
    """
    query = db.query(Operation).filter(Operation.user_id == user_id)

    if status_filter:
        query = query.filter(Operation.status == status_filter)

    if sort_by == "date":
        query = query.order_by(Operation.created_at.desc())

    return query.all()
