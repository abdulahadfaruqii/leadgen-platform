"""
Lead schemas.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field

from app.schemas.base import BaseSchema, TimestampSchema, PaginatedResponse


class LeadCreate(BaseSchema):
    business_id: str
    campaign_id: Optional[str] = None
    overall_score: float = Field(..., ge=0, le=100)
    priority: str = "medium"
    recommended_services: Optional[List[Dict[str, Any]]] = None


class LeadUpdate(BaseSchema):
    overall_score: Optional[float] = None
    priority: Optional[str] = None
    outreach_status: Optional[str] = None
    notes: Optional[str] = None
    next_follow_up_date: Optional[datetime] = None


class LeadBusinessSummary(BaseSchema):
    id: str
    name: str
    slug: str
    category: str
    country: str
    state: str
    city: str
    website: Optional[str] = None
    status: str
    lead_score: Optional[float] = None


class LeadResponse(TimestampSchema):
    business_id: str
    campaign_id: Optional[str] = None
    overall_score: float
    website_quality_score: Optional[float] = None
    digital_presence_score: Optional[float] = None
    technology_score: Optional[float] = None
    social_activity_score: Optional[float] = None
    review_score: Optional[float] = None
    growth_score: Optional[float] = None
    opportunity_score: Optional[float] = None
    qualification_reasons: Optional[List[str]] = None
    priority: str
    recommended_services: Optional[List[Dict[str, Any]]] = None
    outreach_status: str
    last_contact_date: Optional[datetime] = None
    next_follow_up_date: Optional[datetime] = None
    contact_attempts: int
    notes: Optional[str] = None
    ai_summary: Optional[str] = None
    qualified_at: datetime
    converted_at: Optional[datetime] = None
    business: Optional[LeadBusinessSummary] = None


class LeadListResponse(PaginatedResponse):
    items: List[LeadResponse]


class LeadFilter(BaseSchema):
    campaign_id: Optional[str] = None
    min_score: Optional[float] = None
    max_score: Optional[float] = None
    priority: Optional[str] = None
    outreach_status: Optional[str] = None
    search: Optional[str] = None
