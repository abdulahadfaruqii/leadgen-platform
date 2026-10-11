"""
Contact schemas.
"""
from typing import Dict, Optional, Any

from pydantic import BaseModel, EmailStr, Field

from app.schemas.base import BaseSchema, TimestampSchema


class ContactCreate(BaseSchema):
    business_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    title: Optional[str] = None
    role: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    source: str = "discovered"
    is_primary: bool = False


class ContactUpdate(BaseSchema):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    title: Optional[str] = None
    role: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    is_primary: Optional[bool] = None
    do_not_contact: Optional[bool] = None


class ContactResponse(TimestampSchema):
    business_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    title: Optional[str] = None
    role: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    source: str
    is_verified: bool
    verification_method: Optional[str] = None
    confidence_score: Optional[float] = None
    ai_bio: Optional[str] = None
    social_profiles: Optional[Dict[str, str]] = None
    is_primary: bool
    do_not_contact: bool
