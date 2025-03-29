from pydantic import BaseModel
from enum import Enum
from datetime import datetime


class OperationStatus(str, Enum):
    uploaded = "uploaded"
    processing = "processing"
    done = "done"
    error = "error"


class FileUploadResponse(BaseModel):
    filename: str
    download_url: str
    user_id: str
    operation_id: int


class OperationItem(BaseModel):
    id: int
    file_name: str
    status: OperationStatus
    created_at: datetime

    class Config:
        model_config = {
            "from_attributes": True
        }
