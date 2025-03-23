from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import FileResponse
from src.python.services import file_services
from src.python.schemas.file_schema import FileUploadResponse, OperationItem
from src.python.dependencies.auth_stub import get_current_user

router = APIRouter()

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    user=Depends(get_current_user)
):
    filename, operation_id = file_services.save_file(file, user_id=user["user_id"])
    return FileUploadResponse(
        filename=filename,
        download_url=f"/file/{filename}",
        user_id=user["user_id"],
        operation_id=operation_id
    )
    
@router.get("/operations", response_model=list[OperationItem])
async def get_operations(user=Depends(get_current_user)):
    return file_services.get_operations_by_user(user_id=user["user_id"])

@router.get("/{file_name}", response_class=FileResponse)
async def get_file(file_name: str):
    return file_services.get_file_response(file_name)


