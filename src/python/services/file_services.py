import os
import shutil
import uuid
import json
from datetime import datetime
from fastapi import UploadFile, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from docx import Document

from src.python.database.database import SessionLocal
from src.python.models.operation import Operation, OperationStatus
from src.python.utils.logger_utils import get_logger
from src.python.services.template_services import get_templates, get_template_by_id
from src.python.utils.template_compiler import compile_ui_to_rules
from src.python.utils.audit.pipeline.orchestrator import analyze_document

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
            created_at=datetime.utcnow(),
        )
        db.add(operation)
        db.commit()
        db.refresh(operation)

        background_tasks.add_task(process_file_task, file_path, operation.id, template_id)

        logger.info(
            f"[SAVE FILE] User {user_id} uploaded {safe_filename} -> {unique_name} (operation_id={operation.id})"
        )
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

        # Template
        if template_id:
            template = get_template_by_id(db, template_id, operation.user_id)
        else:
            templates = get_templates(db, str(operation.user_id))
            template = templates[0] if templates else None

        compiled_rules = None
        if not template:
            logger.warning(f"[NO TEMPLATE FOUND] operation_id={operation_id}")
            errors: list[dict] = []
        else:
            # Prefer precompiled rules stored in DB; fallback to compile-on-the-fly
            compiled_rules = (template.compiled or None)
            if not compiled_rules:
                try:
                    compiled_rules = compile_ui_to_rules(template.filters or {})
                except Exception as err:
                    logger.warning(f"[COMPILE TEMPLATE WARN] operation_id={operation_id} | {err}")
                    compiled_rules = None

            # Save compiled for transparency next to input
            try:
                if compiled_rules:
                    base_in, _ = os.path.splitext(input_path)
                    compiled_json_path = base_in + "_compiled_rules.json"
                    with open(compiled_json_path, "w", encoding="utf-8") as f:
                        json.dump(compiled_rules, f, ensure_ascii=False)
            except Exception as err:
                logger.warning(f"[COMPILED JSON WRITE WARN] operation_id={operation_id} | {err}")

            # Full document analysis is removed during redesign; keep errors empty for now.
            errors: list[dict] = []

        base_path, ext = os.path.splitext(input_path)
        is_pdf = ext.lower() == ".pdf"
        result_path = base_path + ("_result.pdf" if is_pdf else "_result.docx")

        if is_pdf:
            # For PDF: return file as-is, skip DOCX analysis/comments
            try:
                shutil.copyfile(input_path, result_path)
            except Exception as cp_err:
                logger.warning(f"[PDF COPY ERROR] operation_id={operation_id} | {cp_err}")
        else:
            # Create a result copy of the input document
            Document(input_path).save(result_path)

            # Analyze and insert comments using the new audit pipeline
            try:
                issues, _ = analyze_document(result_path, compiled_rules or {}, emit_comments=True, inplace=True)
                errors = [
                    {
                        "paragraph_index": i.paragraph_index,
                        "error": i.message,
                        "code": i.code,
                        "category": "format",
                        "severity": i.severity,
                        "meta": {"rule_id": i.rule_id, "expected": i.expected, "actual": i.actual},
                    }
                    for i in (issues or [])
                ]
            except Exception as comment_err:
                logger.warning(f"[AUDIT PIPELINE WARN] operation_id={operation_id} | {comment_err}")

        # Persist a machine-readable errors JSON sidecar for UI/API
        try:
            errors_json_path = base_path + "_errors.json"
            with open(errors_json_path, "w", encoding="utf-8") as f:
                json.dump(errors or [], f, ensure_ascii=False)
        except Exception as write_err:
            logger.warning(f"[ERRORS JSON WRITE WARN] operation_id={operation_id} | {write_err}")

        # Update operation
        user_folder = os.path.basename(os.path.dirname(result_path))
        file_name = os.path.basename(result_path)
        operation.status = OperationStatus.done
        operation.result_path = os.path.join(user_folder, file_name)
        db.commit()

        logger.info(f"[PROCESS FILE DONE] operation_id={operation_id} | result={file_name}")

    except Exception as err:
        if "operation" in locals() and operation:
            operation.status = OperationStatus.error
            db.commit()
        logger.error(f"[PROCESS FILE ERROR] operation_id={operation_id} | Error: {str(err)}")

    finally:
        db.close()


def get_file_response(operation_id: int, user_id: int, db: Session):
    operation = db.query(Operation).filter_by(id=operation_id, user_id=user_id).first()
    if not operation:
        logger.warning(
            f"[FILE DOWNLOAD BLOCKED] operation_id={operation_id} | user_id={user_id} | Not found"
        )
        raise HTTPException(status_code=404, detail="Операция не найдена")

    if not operation.result_path:
        logger.warning(f"[FILE DOWNLOAD BLOCKED] operation_id={operation_id} | Result not ready")
        raise HTTPException(status_code=404, detail="Результат еще не готов")

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


def get_operation_errors(operation_id: int, user_id: int, db: Session) -> list[dict]:
    operation = db.query(Operation).filter_by(id=operation_id, user_id=user_id).first()
    if not operation:
        logger.warning(
            f"[ERRORS FETCH BLOCKED] operation_id={operation_id} | user_id={user_id} | Not found"
        )
        raise HTTPException(status_code=404, detail="Операция не найдена")

    # Derive sidecar JSON path
    try:
        if operation.result_path:
            abs_result = os.path.join(UPLOAD_FOLDER, operation.result_path)
            base, _ = os.path.splitext(abs_result)
            candidate = base.replace("_result", "") + "_errors.json"
        else:
            abs_input = os.path.join(UPLOAD_FOLDER, str(user_id), operation.file_name)
            base, _ = os.path.splitext(abs_input)
            candidate = base + "_errors.json"

        if os.path.exists(candidate):
            with open(candidate, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
    except Exception as e:
        logger.warning(f"[ERRORS JSON READ WARN] operation_id={operation_id} | {e}")

    return []
