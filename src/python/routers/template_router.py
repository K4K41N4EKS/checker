from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from src.python.schemas.template_schema import TemplateCreate, TemplateResponse, TemplateUpdate
from src.python.services import template_services
from python.dependencies.auth import get_current_user
from src.python.database import get_db
from src.python.utils.logger_utils import get_logger

logger = get_logger("routers.template_actions")

router = APIRouter(prefix="/templates", tags=["Templates"])

@router.post("/", response_model=TemplateResponse)
async def create_template(
    template: TemplateCreate,
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        result = template_services.create_template(db, user_id=user["user_id"], template=template)
        logger.info(f"[CREATE TEMPLATE] {user['username']} | {request.client.host} | '{template.name}' создан")
        return result
    except Exception as e:
        logger.error(f"[TEMPLATE ERROR] {user['username']} | {request.client.host} | Ошибка при создании шаблона: {str(e)}")
        raise

@router.get("/", response_model=list[TemplateResponse])
async def get_templates(
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        templates = template_services.get_templates(db, user_id=user["user_id"])
        logger.info(f"[LIST TEMPLATES] {user['username']} | {request.client.host} | {len(templates)} шаблонов")
        return templates
    except Exception as e:
        logger.error(f"[TEMPLATE ERROR] {user['username']} | {request.client.host} | Ошибка при получении шаблонов: {str(e)}")
        raise

@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: str,
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        template = template_services.get_template_by_id(db, template_id=template_id, user_id=user["user_id"])
        logger.info(f"[GET TEMPLATE] {user['username']} | {request.client.host} | ID={template_id}")
        return template
    except Exception as e:
        logger.error(f"[TEMPLATE ERROR] {user['username']} | {request.client.host} | ID={template_id} | Ошибка: {str(e)}")
        raise

@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: str,
    template: TemplateUpdate,
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        result = template_services.update_template(db, template_id=template_id, user_id=user["user_id"], template=template)
        logger.info(f"[UPDATE TEMPLATE] {user['username']} | {request.client.host} | ID={template_id}")
        return result
    except Exception as e:
        logger.error(f"[TEMPLATE ERROR] {user['username']} | {request.client.host} | ID={template_id} | Ошибка при обновлении: {str(e)}")
        raise

@router.delete("/{template_id}", response_model=dict)
async def delete_template(
    template_id: str,
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        template_services.delete_template(db, template_id=template_id, user_id=user["user_id"])
        logger.info(f"[DELETE TEMPLATE] {user['username']} | {request.client.host} | ID={template_id}")
        return {"detail": "Template deleted"}
    except Exception as e:
        logger.error(f"[TEMPLATE ERROR] {user['username']} | {request.client.host} | ID={template_id} | Ошибка при удалении: {str(e)}")
        raise
