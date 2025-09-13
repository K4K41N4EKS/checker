from sqlalchemy.orm import Session
from src.python.models.template import Template
from src.python.schemas.template_schema import TemplateCreate, TemplateUpdate
from fastapi import HTTPException
from src.python.utils.logger_utils import get_logger
from src.python.utils.template_compiler import compile_ui_to_rules

logger = get_logger("services.template_services")


def _ensure_compiled_column(db: Session) -> None:
    """Best-effort DB migration to add Template.compiled column if missing.
    Supports SQLite and Postgres; silently ignores failures.
    """
    try:
        bind = db.get_bind()
        if bind is None:
            return
        dialect = bind.dialect.name
        exists = False
        if dialect == "sqlite":
            rows = bind.execute("PRAGMA table_info(templates)").fetchall()
            exists = any((r[1] == "compiled" for r in rows))
            if not exists:
                bind.execute("ALTER TABLE templates ADD COLUMN compiled TEXT")
        elif dialect in ("postgresql", "postgres"):
            res = bind.execute(
                "SELECT 1 FROM information_schema.columns WHERE table_name='templates' AND column_name='compiled'"
            ).fetchone()
            exists = res is not None
            if not exists:
                bind.execute("ALTER TABLE templates ADD COLUMN compiled JSON")
        else:
            # try generic information_schema
            res = bind.execute(
                "SELECT 1 FROM information_schema.columns WHERE table_name='templates' AND column_name='compiled'"
            ).fetchone()
            if res is None:
                bind.execute("ALTER TABLE templates ADD COLUMN compiled JSON")
    except Exception:
        # Do not block main flow if migration fails
        pass


def create_template(db: Session, user_id: str, template: TemplateCreate):
    try:
        _ensure_compiled_column(db)
        compiled = compile_ui_to_rules(template.filters or {}) if template.filters is not None else None
        new_template = Template(user_id=user_id, name=template.name, filters=template.filters, compiled=compiled)
        db.add(new_template)
        db.commit()
        db.refresh(new_template)
        logger.info(f"[CREATE] user_id={user_id} | template='{template.name}' created")
        return new_template
    except Exception as e:
        logger.error(f"[CREATE ERROR] user_id={user_id} | {e}")
        raise


def get_templates(db: Session, user_id: str):
    try:
        templates = db.query(Template).filter(Template.user_id == user_id).all()
        logger.info(f"[LIST] user_id={user_id} | count={len(templates)}")
        return templates
    except Exception as e:
        logger.error(f"[LIST ERROR] user_id={user_id} | {e}")
        raise


def get_template_by_id(db: Session, template_id: str, user_id: str):
    try:
        template = db.query(Template).filter_by(id=template_id, user_id=user_id).first()
        if not template:
            logger.warning(f"[GET] user_id={user_id} | template_id={template_id} not found")
            raise HTTPException(status_code=404, detail="Template not found")
        logger.info(f"[GET] user_id={user_id} | template_id={template_id} ok")
        return template
    except Exception as e:
        logger.error(f"[GET ERROR] user_id={user_id} | template_id={template_id} | {e}")
        raise


def update_template(db: Session, template_id: str, user_id: str, template: TemplateUpdate):
    try:
        db_template = db.query(Template).filter_by(id=template_id, user_id=user_id).first()
        if not db_template:
            logger.warning(f"[UPDATE] user_id={user_id} | template_id={template_id} not found")
            raise HTTPException(status_code=404, detail="Template not found")

        if template.name is not None:
            db_template.name = template.name
        if template.filters is not None:
            _ensure_compiled_column(db)
            db_template.filters = template.filters
            db_template.compiled = compile_ui_to_rules(template.filters or {})

        db.commit()
        db.refresh(db_template)
        logger.info(f"[UPDATE] user_id={user_id} | template_id={template_id} ok")
        return db_template
    except Exception as e:
        logger.error(f"[UPDATE ERROR] user_id={user_id} | template_id={template_id} | {e}")
        raise


def delete_template(db: Session, template_id: str, user_id: str):
    try:
        template = db.query(Template).filter_by(id=template_id, user_id=user_id).first()
        if not template:
            logger.warning(f"[DELETE] user_id={user_id} | template_id={template_id} not found")
            raise HTTPException(status_code=404, detail="Template not found")

        db.delete(template)
        db.commit()
        logger.info(f"[DELETE] user_id={user_id} | template_id={template_id} ok")
    except Exception as e:
        logger.error(f"[DELETE ERROR] user_id={user_id} | template_id={template_id} | {e}")
        raise
