
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response."""
    user_id: UUID
    created_at: datetime
