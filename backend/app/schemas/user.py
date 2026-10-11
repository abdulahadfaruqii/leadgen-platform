"""
User schemas.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.schemas.base import BaseSchema, TimestampSchema


class UserCreate(BaseSchema):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1, max_length=255)


class UserLogin(BaseSchema):
    email: EmailStr
    password: str


class UserUpdate(BaseSchema):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    subscription_tier: Optional[str] = None


class UserResponse(TimestampSchema):
    email: EmailStr
    full_name: str
    avatar_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    subscription_tier: str
    monthly_lead_quota: int
    monthly_leads_used: int
    last_login_at: Optional[datetime] = None


class TokenResponse(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenPayload(BaseSchema):
    sub: Optional[str] = None
    type: Optional[str] = None
