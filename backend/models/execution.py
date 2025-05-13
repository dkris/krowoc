from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base

class Execution(Base):
    __tablename__ = "executions"

    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    model = Column(String(100), nullable=False)  # e.g., 'gpt-4', 'claude-2', 'gemini-pro'
    provider = Column(String(50), nullable=False)  # 'openai', 'anthropic', 'google'
    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)
    cost = Column(Float, nullable=True)
    response_text = Column(Text, nullable=True)
    is_successful = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    prompt = relationship("Prompt", back_populates="executions")
    user = relationship("User")

    def __repr__(self):
        return f"<Execution id={self.id} prompt_id={self.prompt_id} model={self.model}>" 