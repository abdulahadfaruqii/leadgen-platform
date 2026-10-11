"""
Base schemas with common patterns.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TimestampSchema(BaseSchema):
    id: str
    created_at: datetime
    updated_at: datetime


class PaginationParams(BaseSchema):
    page: int = 1
    page_size: int = 20


class PaginatedResponse(BaseSchema):
    total: int
    page: int
    page_size: int
    pages: int
    items: list


class IDResponse(BaseSchema):
    id: str
    success: bool = True
