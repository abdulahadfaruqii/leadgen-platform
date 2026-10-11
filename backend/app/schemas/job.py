"""
Job schemas.
"""
from datetime import datetime
from typing import Dict, Optional, Any

from pydantic import BaseModel, Field

from app.schemas.base import BaseSchema, TimestampSchema, PaginatedResponse


class JobCreate(BaseSchema):
    job_type: str = Field(..., min_length=1, max_length=100)
    job_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    campaign_id: Optional[str] = None
    max_retries: int = 3


class JobUpdate(BaseSchema):
    status: Optional[str] = None
    progress_percent: Optional[float] = None
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    checkpoint_data: Optional[Dict[str, Any]] = None


class JobResponse(TimestampSchema):
    owner_id: str
    campaign_id: Optional[str] = None
    celery_task_id: Optional[str] = None
    job_type: str
    job_name: str
    description: Optional[str] = None
    status: str
    progress_percent: float
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    retry_count: int
    max_retries: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    checkpoint_data: Optional[Dict[str, Any]] = None


class JobListResponse(PaginatedResponse):
    items: List[JobResponse]
