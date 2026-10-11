"""
User model for authentication and authorization.
"""
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # OAuth
    google_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    microsoft_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Subscription
    subscription_tier: Mapped[str] = mapped_column(String(50), default="free")
    subscription_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    monthly_lead_quota: Mapped[int] = mapped_column(Integer, default=100)
    monthly_leads_used: Mapped[int] = mapped_column(Integer, default=0)

    # Timestamps
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    campaigns: Mapped[List["Campaign"]] = relationship("Campaign", back_populates="owner")
    jobs: Mapped[List["Job"]] = relationship("Job", back_populates="owner")
