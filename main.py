from fastapi import FastAPI
from src.python.database.database import init_db
from src.python.routers import file_router

app = FastAPI()

app.include_router(file_router.router, prefix="/file", tags=["file"])

@app.on_event("startup")
def on_startup():
    init_db()
