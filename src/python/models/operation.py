from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.python.database.database import Base

class Operation(Base):
    __tablename__ = "operations"
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="pending")
    file_name = Column(String)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="operations")
