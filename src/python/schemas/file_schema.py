from pydantic import BaseModel

class FileUploadResponse(BaseModel):
    filename: str
    download_url: str
    user_id: int
    operation_id: int

class OperationItem(BaseModel):
    id: int
    file_name: str
    status: str
