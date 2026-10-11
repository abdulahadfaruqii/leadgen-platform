"""
Outreach schemas.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field

from app.schemas.base import BaseSchema, TimestampSchema, PaginatedResponse


class OutreachCreate(BaseSchema):
    business_id: str
    lead_id: Optional[str] = None
    contact_id: Optional[str] = None
    campaign_id: Optional[str] = None
    channel: str = Field(..., pattern="^(email|linkedin|facebook|instagram|twitter|contact_form|phone)$")
    message_type: str = Field(..., pattern="^(cold|follow_up|reminder|proposal|custom)$")
    subject: Optional[str] = None
    body: str
    scheduled_at: Optional[datetime] = None
    sequence_position: int = 1


class OutreachUpdate(BaseSchema):
    subject: Optional[str] = None
    body: Optional[str] = None
    status: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    requires_approval: Optional[bool] = None


class OutreachApprove(BaseSchema):
    approved: bool = True
    notes: Optional[str] = None


class OutreachResponse(TimestampSchema):
    business_id: str
    lead_id: Optional[str] = None
    contact_id: Optional[str] = None
    campaign_id: Optional[str] = None
    channel: str
    message_type: str
    subject: Optional[str] = None
    body: str
    body_html: Optional[str] = None
    personalization_data: Optional[Dict[str, Any]] = None
    status: str
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None
    open_count: int
    click_count: int
    requires_approval: bool
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    sequence_position: int
    is_automated: bool


class OutreachListResponse(PaginatedResponse):
    items: List[OutreachResponse]


class OutreachFilter(BaseSchema):
    campaign_id: Optional[str] = None
    status: Optional[str] = None
    channel: Optional[str] = None
    requires_approval: Optional[bool] = None
    search: Optional[str] = None
