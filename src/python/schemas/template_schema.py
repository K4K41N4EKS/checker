from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TemplateBase(BaseModel):
    name: str
    filters: dict

class TemplateCreate(TemplateBase):
    pass

class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    filters: Optional[dict] = None

class TemplateResponse(TemplateBase):
    id: str
    user_id: str
    created_at: datetime
    compiled: dict | None = None

    class Config:
        model_config = {
            "from_attributes": True
        }
