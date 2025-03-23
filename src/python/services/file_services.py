import os
from fastapi import UploadFile
from src.python.database.database import SessionLocal
from src.python.models.operation import Operation
from fastapi.responses import FileResponse

UPLOAD_FOLDER = "uploaded_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def save_file(file: UploadFile, user_id: int) -> tuple[str, int]:
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as f:
        content = file.file.read()
        f.write(content)

    with SessionLocal() as db:
        operation = Operation(file_name=file.filename, user_id=user_id, status="uploaded")
        db.add(operation)
        db.commit()
        db.refresh(operation)
        return file.filename, operation.id

def get_file_response(file_name: str) -> FileResponse:
    file_path = os.path.join("uploaded_files", file_name)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл {file_name} не найден")
    return FileResponse(path=file_path, filename=file_name, media_type='application/octet-stream')

def get_operations_by_user(user_id: int) -> list[dict]:
    with SessionLocal() as db:
        operations = db.query(Operation).filter_by(user_id=user_id).all()
        return [{
            "id": op.id,
            "file_name": op.file_name,
            "status": op.status
        } for op in operations]
