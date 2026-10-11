"""
Contact model - people associated with businesses.
"""
from typing import Optional, Dict, Any

from sqlalchemy import Boolean, Float, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Contact(Base):
    __tablename__ = "contacts"

    business_id: Mapped[str] = mapped_column(ForeignKey("businesses.id"), nullable=False)

    # Personal Info
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    role: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Contact Details
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    twitter_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # Source & Verification
    source: Mapped[str] = mapped_column(String(50), default="discovered")
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verification_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # AI Enrichment
    ai_bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Social
    social_profiles: Mapped[Optional[Dict[str, str]]] = mapped_column(JSON, nullable=True)

    # Preferences
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    do_not_contact: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    business: Mapped["Business"] = relationship("Business", back_populates="contacts")
