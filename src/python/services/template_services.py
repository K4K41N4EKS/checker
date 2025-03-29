from sqlalchemy.orm import Session
from src.python.models.template import Template
from src.python.schemas.template_schema import TemplateCreate, TemplateUpdate
from fastapi import HTTPException

def create_template(db: Session, user_id: str, template: TemplateCreate):
    new_template = Template(user_id=user_id, name=template.name, filters=template.filters)
    db.add(new_template)
    db.commit()
    db.refresh(new_template)
    return new_template

def get_templates(db: Session, user_id: str):
    return db.query(Template).filter(Template.user_id == user_id).all()

def get_template_by_id(db: Session, template_id: str, user_id: str):
    template = db.query(Template).filter_by(id=template_id, user_id=user_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

def update_template(db: Session, template_id: str, user_id: str, template: TemplateUpdate):
    db_template = db.query(Template).filter_by(id=template_id, user_id=user_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")

    if template.name is not None:
        db_template.name = template.name
    if template.filters is not None:
        db_template.filters = template.filters

    db.commit()
    db.refresh(db_template)
    return db_template

def delete_template(db: Session, template_id: str, user_id: str):
    template = db.query(Template).filter_by(id=template_id, user_id=user_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    db.delete(template)
    db.commit()
