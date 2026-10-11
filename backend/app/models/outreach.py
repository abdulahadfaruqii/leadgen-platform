"""
Outreach model - messages and sequences sent to leads.
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from sqlalchemy import (
    Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Outreach(Base):
    __tablename__ = "outreach"

    business_id: Mapped[str] = mapped_column(ForeignKey("businesses.id"), nullable=False)
    lead_id: Mapped[Optional[str]] = mapped_column(ForeignKey("leads.id"), nullable=True)
    contact_id: Mapped[Optional[str]] = mapped_column(ForeignKey("contacts.id"), nullable=True)
    campaign_id: Mapped[Optional[str]] = mapped_column(ForeignKey("campaigns.id"), nullable=True)

    # Message Details
    channel: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    message_type: Mapped[str] = mapped_column(String(50), nullable=False)
    subject: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    body_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Personalization
    personalization_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    ai_prompt_used: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Status
    status: Mapped[str] = mapped_column(String(50), default="draft", index=True)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    opened_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    clicked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    replied_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    bounced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Metrics
    open_count: Mapped[int] = mapped_column(Integer, default=0)
    click_count: Mapped[int] = mapped_column(Integer, default=0)

    # Human Review
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=True)
    approved_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Sequence
    sequence_position: Mapped[int] = mapped_column(Integer, default=1)
    is_automated: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    business: Mapped["Business"] = relationship("Business", back_populates="outreach_messages")
    lead: Mapped[Optional["Lead"]] = relationship("Lead", back_populates="outreach_messages")
    campaign: Mapped[Optional["Campaign"]] = relationship("Campaign", back_populates="outreach_messages")

    __table_args__ = (
        Index("ix_outreach_status_scheduled", "status", "scheduled_at"),
        Index("ix_outreach_campaign_channel", "campaign_id", "channel"),
    )
