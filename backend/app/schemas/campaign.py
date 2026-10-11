"""
Campaign schemas.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field

from app.schemas.base import BaseSchema, TimestampSchema, PaginatedResponse


class CampaignCreate(BaseSchema):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    target_country: str = Field(..., min_length=1)
    target_state: Optional[str] = None
    target_city: Optional[str] = None
    target_categories: List[str] = Field(..., min_length=1)
    services: List[str] = Field(..., min_length=1)
    min_rating: Optional[float] = Field(None, ge=0, le=5)
    max_results_per_category: int = Field(100, ge=1, le=1000)
    scheduled_start: Optional[datetime] = None
    config: Optional[Dict[str, Any]] = None


class CampaignUpdate(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    scheduled_start: Optional[datetime] = None
    config: Optional[Dict[str, Any]] = None


class CampaignResponse(TimestampSchema):
    owner_id: str
    name: str
    description: Optional[str] = None
    target_country: str
    target_state: Optional[str] = None
    target_city: Optional[str] = None
    target_categories: List[str]
    min_rating: Optional[float] = None
    max_results_per_category: int
    services: List[str]
    status: str
    progress_percent: float
    businesses_found: int
    leads_qualified: int
    outreach_sent: int
    responses_received: int
    scheduled_start: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    config: Optional[Dict[str, Any]] = None


class CampaignListResponse(PaginatedResponse):
    items: List[CampaignResponse]


class CampaignFilter(BaseSchema):
    status: Optional[str] = None
    search: Optional[str] = None
