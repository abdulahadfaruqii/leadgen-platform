"""
Analytics event model - stores aggregated metrics in PostgreSQL.
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    event_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Context
    user_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), nullable=True)
    campaign_id: Mapped[Optional[str]] = mapped_column(ForeignKey("campaigns.id"), nullable=True)
    business_id: Mapped[Optional[str]] = mapped_column(ForeignKey("businesses.id"), nullable=True)

    # Metrics
    metric_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    metric_unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Dimensions
    dimensions: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Raw data
    payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Timestamp
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True
    )

    __table_args__ = (
        Index("ix_analytics_user_event", "user_id", "event_type"),
        Index("ix_analytics_campaign_event", "campaign_id", "event_type"),
        Index("ix_analytics_event_time", "event_type", "occurred_at"),
    )
