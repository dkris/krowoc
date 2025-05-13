from sqlalchemy import Column, Integer, String, Text, ARRAY, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from .base import Base

class PromptState(enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    prompt_text = Column(Text, nullable=False)
    tags = Column(ARRAY(String), nullable=True)
    model_whitelist = Column(ARRAY(String), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    state = Column(Enum(PromptState), default=PromptState.DRAFT, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="prompts")
    executions = relationship("Execution", back_populates="prompt")

    def __repr__(self):
        return f"<Prompt id={self.id} title={self.title} user_id={self.user_id}>" 