from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.python.database import init_db
from src.python.routers import all_routers
from src.python.middlewares.rate_limiter import RateLimiterMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RateLimiterMiddleware)

for router in all_routers:
    app.include_router(router)

@app.on_event("startup")
def on_startup():
    init_db()
