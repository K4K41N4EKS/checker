from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from src.python.database import Base


class OperationStatus(PyEnum):
    uploaded = "uploaded"
    processing = "processing"
    done = "done"
    error = "error"


class Operation(Base):
    __tablename__ = "operations"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(OperationStatus), default=OperationStatus.uploaded)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="operations")
