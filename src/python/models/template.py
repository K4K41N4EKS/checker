from sqlalchemy import Column, String, Integer, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from src.python.database import Base
from datetime import datetime
import uuid

class Template(Base):
    __tablename__ = 'templates'
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id'), index=True)
    name = Column(String, nullable=False)
    # Raw UI filters as entered by user (for editing in UI)
    filters = Column(JSON, nullable=False)
    # Compiled, normalized rules for fast checking (kept in sync on create/update)
    compiled = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="templates")
