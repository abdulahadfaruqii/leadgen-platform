"""
Business schemas.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, HttpUrl

from app.schemas.base import BaseSchema, TimestampSchema, PaginatedResponse


class BusinessCreate(BaseSchema):
    name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=100)
    country: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    city: str = Field(..., min_length=1, max_length=100)
    address: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    google_place_id: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class BusinessUpdate(BaseSchema):
    name: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = None
    lead_score: Optional[float] = None
    website_quality_score: Optional[float] = None
    mobile_responsive: Optional[bool] = None
    seo_score: Optional[float] = None
    detected_technologies: Optional[List[str]] = None
    missing_features: Optional[List[str]] = None
    has_booking_system: Optional[bool] = None
    has_online_ordering: Optional[bool] = None
    has_crm: Optional[bool] = None
    has_chatbot: Optional[bool] = None
    has_mobile_app: Optional[bool] = None
    has_analytics: Optional[bool] = None
    social_profiles: Optional[Dict[str, str]] = None
    lead_score: Optional[float] = None
    business_size: Optional[str] = None


class BusinessResponse(TimestampSchema):
    name: str
    slug: str
    category: str
    subcategories: Optional[List[str]] = None
    country: str
    state: str
    city: str
    address: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    google_place_id: Optional[str] = None
    google_rating: Optional[float] = None
    google_review_count: Optional[int] = None
    google_hours: Optional[Dict[str, Any]] = None
    google_photos: Optional[List[str]] = None
    google_url: Optional[str] = None
    website_quality_score: Optional[float] = None
    mobile_responsive: Optional[bool] = None
    page_speed_score: Optional[float] = None
    seo_score: Optional[float] = None
    detected_technologies: Optional[List[str]] = None
    missing_features: Optional[List[str]] = None
    website_issues: Optional[List[Dict[str, Any]]] = None
    has_booking_system: Optional[bool] = None
    has_online_ordering: Optional[bool] = None
    has_crm: Optional[bool] = None
    has_chatbot: Optional[bool] = None
    has_mobile_app: Optional[bool] = None
    has_analytics: Optional[bool] = None
    has_customer_portal: Optional[bool] = None
    social_profiles: Optional[Dict[str, str]] = None
    lead_score: Optional[float] = None
    business_size: Optional[str] = None
    estimated_revenue: Optional[str] = None
    employee_count: Optional[str] = None
    hiring_active: Optional[bool] = None
    growth_signals: Optional[List[str]] = None
    status: str
    is_duplicate: bool
    source_campaign_id: Optional[str] = None
    discovered_at: datetime


class BusinessListResponse(PaginatedResponse):
    items: List[BusinessResponse]


class BusinessFilter(BaseSchema):
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    min_score: Optional[float] = None
    max_score: Optional[float] = None
    has_website: Optional[bool] = None
    search: Optional[str] = None
