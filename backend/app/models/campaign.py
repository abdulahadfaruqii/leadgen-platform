"""
Campaign model - orchestrates lead generation jobs.
"""
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from sqlalchemy import (
    Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Basic Info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Target Criteria
    target_country: Mapped[str] = mapped_column(String(100), nullable=False)
    target_state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    target_city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    target_categories: Mapped[List[str]] = mapped_column(JSON, nullable=False)

    # Filters
    min_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_results_per_category: Mapped[int] = mapped_column(Integer, default=100)

    # Services to Offer
    services: Mapped[List[str]] = mapped_column(JSON, nullable=False)

    # Status
    status: Mapped[str] = mapped_column(String(50), default="draft", index=True)
    progress_percent: Mapped[float] = mapped_column(Float, default=0.0)

    # Results
    businesses_found: Mapped[int] = mapped_column(Integer, default=0)
    leads_qualified: Mapped[int] = mapped_column(Integer, default=0)
    outreach_sent: Mapped[int] = mapped_column(Integer, default=0)
    responses_received: Mapped[int] = mapped_column(Integer, default=0)

    # Scheduling
    scheduled_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Configuration
    config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="campaigns")
    businesses: Mapped[List["Business"]] = relationship("Business", back_populates="campaign")
    leads: Mapped[List["Lead"]] = relationship("Lead", back_populates="campaign")
    outreach_messages: Mapped[List["Outreach"]] = relationship("Outreach", back_populates="campaign")
    jobs: Mapped[List["Job"]] = relationship("Job", back_populates="campaign")

    __table_args__ = (
        Index("ix_campaigns_owner_status", "owner_id", "status"),
    )
