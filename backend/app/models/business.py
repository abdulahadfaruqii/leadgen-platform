"""
Business model - core entity representing a discovered business.
"""
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from sqlalchemy import (
    Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text, 
    UniqueConstraint, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Business(Base):
    __tablename__ = "businesses"

    # Basic Info
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    subcategories: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    # Location
    country: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Contact
    website: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Google Maps Data
    google_place_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    google_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    google_review_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    google_hours: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    google_photos: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    google_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # Website Analysis
    website_analyzed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    website_quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    mobile_responsive: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    page_speed_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    seo_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    detected_technologies: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    missing_features: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    website_issues: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    has_booking_system: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    has_online_ordering: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    has_crm: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    has_chatbot: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    has_mobile_app: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    has_analytics: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    has_customer_portal: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    # Social Profiles
    social_profiles: Mapped[Optional[Dict[str, str]]] = mapped_column(JSON, nullable=True)

    # Qualification
    lead_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True, index=True)
    business_size: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    estimated_revenue: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    employee_count: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    hiring_active: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    growth_signals: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    # Status
    status: Mapped[str] = mapped_column(String(50), default="discovered", index=True)
    is_duplicate: Mapped[bool] = mapped_column(Boolean, default=False)
    duplicate_of_id: Mapped[Optional[str]] = mapped_column(ForeignKey("businesses.id"), nullable=True)

    # Source
    source_campaign_id: Mapped[Optional[str]] = mapped_column(ForeignKey("campaigns.id"), nullable=True)
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    leads: Mapped[List["Lead"]] = relationship("Lead", back_populates="business")
    contacts: Mapped[List["Contact"]] = relationship("Contact", back_populates="business")
    outreach_messages: Mapped[List["Outreach"]] = relationship("Outreach", back_populates="business")
    campaign: Mapped[Optional["Campaign"]] = relationship("Campaign", back_populates="businesses")

    __table_args__ = (
        UniqueConstraint("name", "city", "country", name="uq_business_location"),
        Index("ix_businesses_score_status", "lead_score", "status"),
        Index("ix_businesses_category_location", "category", "country", "state", "city"),
    )
