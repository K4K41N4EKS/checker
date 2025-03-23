from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from os import getenv

DATABASE_URL = getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def init_db():
    from src.python.models.user import User
    from src.python.models.operation import Operation
    Base.metadata.create_all(bind=engine)
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
