from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from enum import Enum


class PromptStateEnum(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class UserValidator(BaseModel):
    email: EmailStr
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = True


class PromptValidator(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    prompt_text: str = Field(..., min_length=10)
    tags: Optional[List[str]] = None
    model_whitelist: Optional[List[str]] = None
    user_id: int
    state: PromptStateEnum = PromptStateEnum.DRAFT

    @validator('tags', 'model_whitelist')
    def validate_lists(cls, v):
        if v is not None:
            if not v:  # Empty list
                return None
            # Remove duplicates and empty strings
            return list(filter(None, set(v)))
        return None


class ExecutionValidator(BaseModel):
    prompt_id: int
    user_id: int
    model: str = Field(..., min_length=2, max_length=100)
    provider: str = Field(..., min_length=2, max_length=50)
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    cost: Optional[float] = None
    response_text: Optional[str] = None
    is_successful: bool = True
    error_message: Optional[str] = None
    execution_time_ms: Optional[int] = None


class ApiKeyValidator(BaseModel):
    user_id: int
    provider: str = Field(..., min_length=2, max_length=50)
    key: str = Field(..., min_length=10)  # Will be hashed before storage
    is_active: bool = True 