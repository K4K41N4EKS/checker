from fastapi import FastAPI
from src.python.database import init_db
from src.python.routers import all_routers
from src.python.middlewares.rate_limiter import RateLimiterMiddleware


app = FastAPI()
app.add_middleware(RateLimiterMiddleware)

for router in all_routers:
    app.include_router(router)

@app.on_event("startup")
def on_startup():
    init_db()
