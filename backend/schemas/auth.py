"""Authentication schemas."""
from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field

from ..models import UserRole


class UserLogin(BaseModel):
    """User login request schema."""

    email: EmailStr
    password: str = Field(..., min_length=8)


class UserCreate(BaseModel):
    """User creation schema."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.RECRUITER


class Token(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data schema."""

    user_id: int
    email: str
    role: UserRole


class UserResponse(BaseModel):
    """User response schema."""

    id: int
    email: str
    username: str
    role: UserRole
    is_active: bool

    class Config:
        from_attributes = True
