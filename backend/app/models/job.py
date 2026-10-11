"""
Job model - tracks async task execution.
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from sqlalchemy import (
    Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Job(Base):
    __tablename__ = "jobs"

    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    campaign_id: Mapped[Optional[str]] = mapped_column(ForeignKey("campaigns.id"), nullable=True)
    celery_task_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Job Details
    job_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    job_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Status
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    progress_percent: Mapped[float] = mapped_column(Float, default=0.0)

    # Results
    result_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Retry
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)

    # Timestamps
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Checkpoint for resumable jobs
    checkpoint_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="jobs")
    campaign: Mapped[Optional["Campaign"]] = relationship("Campaign", back_populates="jobs")
