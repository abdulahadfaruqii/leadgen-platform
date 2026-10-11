"""
Lead model - qualified business with scoring and recommendations.
"""
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from sqlalchemy import (
    Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Lead(Base):
    __tablename__ = "leads"

    business_id: Mapped[str] = mapped_column(ForeignKey("businesses.id"), nullable=False)
    campaign_id: Mapped[Optional[str]] = mapped_column(ForeignKey("campaigns.id"), nullable=True)

    # Scoring
    overall_score: Mapped[float] = mapped_column(Float, default=0.0, index=True)
    website_quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    digital_presence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    technology_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    social_activity_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    review_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    growth_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    opportunity_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Qualification Details
    qualification_reasons: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default="medium", index=True)

    # Service Recommendations
    recommended_services: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)

    # Outreach Status
    outreach_status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    last_contact_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    next_follow_up_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    contact_attempts: Mapped[int] = mapped_column(Integer, default=0)

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    qualified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    converted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    business: Mapped["Business"] = relationship("Business", back_populates="leads")
    campaign: Mapped[Optional["Campaign"]] = relationship("Campaign", back_populates="leads")
    outreach_messages: Mapped[List["Outreach"]] = relationship("Outreach", back_populates="lead")

    __table_args__ = (
        Index("ix_leads_score_priority", "overall_score", "priority"),
        Index("ix_leads_outreach_followup", "outreach_status", "next_follow_up_date"),
    )
