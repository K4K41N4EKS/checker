from fastapi import FastAPI
from python.database.database import init_db
from python.routers import all_routers

app = FastAPI()

for router in all_routers:
    app.include_router(router)

@app.on_event("startup")
def on_startup():
    init_db()
