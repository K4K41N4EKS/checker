from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.python.schemas.template_schema import TemplateCreate, TemplateResponse, TemplateUpdate
from src.python.services import template_services
from python.dependencies.auth import get_current_user
from src.python.database import get_db

router = APIRouter(prefix="/templates", tags=["Templates"])

@router.post("/", response_model=TemplateResponse)
async def create_template(
    template: TemplateCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return template_services.create_template(db, user_id=user["user_id"], template=template)

@router.get("/", response_model=list[TemplateResponse])
async def get_templates(
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return template_services.get_templates(db, user_id=user["user_id"])

@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return template_services.get_template_by_id(db, template_id=template_id, user_id=user["user_id"])

@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: str,
    template: TemplateUpdate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return template_services.update_template(db, template_id=template_id, user_id=user["user_id"], template=template)

@router.delete("/{template_id}", response_model=dict)
async def delete_template(
    template_id: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    template_services.delete_template(db, template_id=template_id, user_id=user["user_id"])
    return {"detail": "Template deleted"}
