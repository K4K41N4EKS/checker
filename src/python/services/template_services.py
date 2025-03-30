from sqlalchemy.orm import Session
from src.python.models.template import Template
from src.python.schemas.template_schema import TemplateCreate, TemplateUpdate
from fastapi import HTTPException
from src.python.utils.logger_utils import get_logger

logger = get_logger("services.template_services")


def create_template(db: Session, user_id: str, template: TemplateCreate):
    try:
        new_template = Template(user_id=user_id, name=template.name, filters=template.filters)
        db.add(new_template)
        db.commit()
        db.refresh(new_template)
        logger.info(f"[CREATE] user_id={user_id} | template='{template.name}' создан")
        return new_template
    except Exception as e:
        logger.error(f"[CREATE ERROR] user_id={user_id} | Ошибка при создании: {str(e)}")
        raise


def get_templates(db: Session, user_id: str):
    try:
        templates = db.query(Template).filter(Template.user_id == user_id).all()
        logger.info(f"[LIST] user_id={user_id} | найдено {len(templates)} шаблонов")
        return templates
    except Exception as e:
        logger.error(f"[LIST ERROR] user_id={user_id} | Ошибка: {str(e)}")
        raise


def get_template_by_id(db: Session, template_id: str, user_id: str):
    try:
        template = db.query(Template).filter_by(id=template_id, user_id=user_id).first()
        if not template:
            logger.warning(f"[GET] user_id={user_id} | template_id={template_id} не найден")
            raise HTTPException(status_code=404, detail="Template not found")
        logger.info(f"[GET] user_id={user_id} | template_id={template_id} успешно получен")
        return template
    except Exception as e:
        logger.error(f"[GET ERROR] user_id={user_id} | template_id={template_id} | Ошибка: {str(e)}")
        raise


def update_template(db: Session, template_id: str, user_id: str, template: TemplateUpdate):
    try:
        db_template = db.query(Template).filter_by(id=template_id, user_id=user_id).first()
        if not db_template:
            logger.warning(f"[UPDATE] user_id={user_id} | template_id={template_id} не найден")
            raise HTTPException(status_code=404, detail="Template not found")

        if template.name is not None:
            db_template.name = template.name
        if template.filters is not None:
            db_template.filters = template.filters

        db.commit()
        db.refresh(db_template)
        logger.info(f"[UPDATE] user_id={user_id} | template_id={template_id} успешно обновлён")
        return db_template
    except Exception as e:
        logger.error(f"[UPDATE ERROR] user_id={user_id} | template_id={template_id} | Ошибка: {str(e)}")
        raise


def delete_template(db: Session, template_id: str, user_id: str):
    try:
        template = db.query(Template).filter_by(id=template_id, user_id=user_id).first()
        if not template:
            logger.warning(f"[DELETE] user_id={user_id} | template_id={template_id} не найден")
            raise HTTPException(status_code=404, detail="Template not found")

        db.delete(template)
        db.commit()
        logger.info(f"[DELETE] user_id={user_id} | template_id={template_id} успешно удалён")
    except Exception as e:
        logger.error(f"[DELETE ERROR] user_id={user_id} | template_id={template_id} | Ошибка: {str(e)}")
        raise
