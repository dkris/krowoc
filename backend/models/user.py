from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    display_name = Column(String(255), nullable=True)
    avatar_url = Column(String(512), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    prompts = relationship("Prompt", back_populates="user")
    api_keys = relationship("ApiKey", back_populates="user")

    def __repr__(self):
        return f"<User id={self.id} email={self.email}>" 