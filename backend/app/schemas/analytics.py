"""
Analytics schemas.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import BaseModel

from app.schemas.base import BaseSchema


class AnalyticsEventCreate(BaseSchema):
    event_type: str
    event_name: str
    campaign_id: Optional[str] = None
    business_id: Optional[str] = None
    metric_value: Optional[float] = None
    metric_unit: Optional[str] = None
    dimensions: Optional[Dict[str, Any]] = None
    payload: Optional[Dict[str, Any]] = None


class DashboardMetrics(BaseSchema):
    total_businesses_found: int
    total_leads_qualified: int
    total_outreach_sent: int
    total_responses: int
    avg_lead_score: float
    conversion_rate: float
    top_categories: List[Dict[str, Any]]
    top_countries: List[Dict[str, Any]]
    score_distribution: List[Dict[str, Any]]
    weekly_activity: List[Dict[str, Any]]


class CampaignMetrics(BaseSchema):
    campaign_id: str
    campaign_name: str
    businesses_found: int
    leads_qualified: int
    outreach_sent: int
    responses_received: int
    conversion_rate: float
    avg_lead_score: float
    timeline: List[Dict[str, Any]]
