"""
Database seed script for local development.
"""
import asyncio
import re
from datetime import datetime, timezone

from sqlalchemy import select

from app.core.security import get_password_hash
from app.db.session import AsyncSessionLocal
from app.models.business import Business
from app.models.campaign import Campaign
from app.models.lead import Lead
from app.models.outreach import Outreach
from app.models.user import User


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


async def seed():
    async with AsyncSessionLocal() as db:
        existing = await db.execute(select(User).where(User.email == "admin@leadgen.ai"))
        user = existing.scalar_one_or_none()
        if not user:
            user = User(
                email="admin@leadgen.ai",
                hashed_password=get_password_hash("admin12345"),
                full_name="Admin User",
                is_superuser=True,
                is_verified=True,
                subscription_tier="enterprise",
                monthly_lead_quota=5000,
            )
            db.add(user)
            await db.flush()
            print("Created admin@leadgen.ai / admin12345")
        else:
            print("Admin user already exists")

        campaign_result = await db.execute(
            select(Campaign).where(Campaign.name == "Texas Healthcare Blitz")
        )
        campaign = campaign_result.scalar_one_or_none()
        if not campaign:
            campaign = Campaign(
                owner_id=user.id,
                name="Texas Healthcare Blitz",
                description="Dentists and clinics across Houston",
                target_country="United States",
                target_state="Texas",
                target_city="Houston",
                target_categories=["Dentists", "Medical Clinics"],
                services=["Website Redesign", "Booking System", "CRM"],
                status="running",
                progress_percent=67,
                businesses_found=6,
                leads_qualified=5,
                outreach_sent=3,
                responses_received=1,
                started_at=datetime.now(timezone.utc),
            )
            db.add(campaign)
            await db.flush()

            draft = Campaign(
                owner_id=user.id,
                name="Dallas Fitness Prospects",
                description="Gyms and yoga studios in Dallas",
                target_country="United States",
                target_state="Texas",
                target_city="Dallas",
                target_categories=["Gyms", "Yoga Studios"],
                services=["Mobile App", "Booking System"],
                status="draft",
                progress_percent=0,
            )
            db.add(draft)
            await db.flush()

        biz_specs = [
            ("Smile Dental Houston", "Dentists", "Houston", "qualified", 94, 4.8, 156, "smiledental.com"),
            ("Taste of Texas BBQ", "Restaurants", "Austin", "discovered", 91, 4.5, 89, "tasteoftexas.com"),
            ("Elite Law Partners", "Law Firms", "Houston", "qualified", 88, 4.7, 134, "elitelaw.com"),
            ("Bella Beauty Salon", "Beauty Salons", "Dallas", "contacted", 85, 4.3, 45, "bellabeauty.com"),
            ("Gold's Fitness Center", "Gyms", "Dallas", "qualified", 78, 4.2, 67, "goldfitness.com"),
            ("Sunrise Medical Clinic", "Medical Clinics", "San Antonio", "discovered", 62, 4.1, 52, "sunrisemed.com"),
        ]

        businesses = []
        for name, category, city, status, score, rating, reviews, website in biz_specs:
            existing_biz = await db.execute(select(Business).where(Business.name == name))
            biz = existing_biz.scalar_one_or_none()
            if not biz:
                biz = Business(
                    name=name,
                    slug=slugify(name),
                    category=category,
                    country="United States",
                    state="Texas",
                    city=city,
                    website=website,
                    google_rating=rating,
                    google_review_count=reviews,
                    lead_score=score,
                    status=status,
                    source_campaign_id=campaign.id,
                )
                db.add(biz)
                await db.flush()
            businesses.append(biz)

        lead_specs = [
            (0, 94, "high", "pending", ["Strong reviews", "Weak booking flow"]),
            (1, 91, "high", "pending", ["High traffic potential"]),
            (2, 88, "high", "contacted", ["Enterprise opportunity"]),
            (3, 85, "medium", "pending", ["Social presence gap"]),
            (4, 78, "medium", "pending", ["Mobile app opportunity"]),
        ]

        leads = []
        for idx, score, priority, status, reasons in lead_specs:
            biz = businesses[idx]
            existing_lead = await db.execute(select(Lead).where(Lead.business_id == biz.id))
            lead = existing_lead.scalar_one_or_none()
            if not lead:
                lead = Lead(
                    business_id=biz.id,
                    campaign_id=campaign.id,
                    overall_score=score,
                    priority=priority,
                    outreach_status=status,
                    qualification_reasons=reasons,
                    contact_attempts=1 if status == "contacted" else 0,
                )
                db.add(lead)
                await db.flush()
            leads.append(lead)

        outreach_specs = [
            (0, 0, "email", "cold", "Quick question about Smile Dental's online presence",
             "Hi, I came across Smile Dental Houston and noticed an opportunity to improve online booking.", True, "draft"),
            (1, 1, "linkedin", "cold", None,
             "Hi, I came across Taste of Texas BBQ and would love to share ideas for a mobile ordering app.", False, "approved"),
            (2, 2, "email", "follow_up", "Re: Elite Law Partners - Quick follow-up",
             "Following up on helping Elite Law Partners with website redesign and CRM integration.", True, "draft"),
        ]

        for biz_idx, lead_idx, channel, msg_type, subject, body, needs_approval, status in outreach_specs:
            existing_msg = await db.execute(
                select(Outreach).where(
                    Outreach.business_id == businesses[biz_idx].id,
                    Outreach.channel == channel,
                    Outreach.message_type == msg_type,
                )
            )
            if existing_msg.scalar_one_or_none():
                continue
            db.add(
                Outreach(
                    business_id=businesses[biz_idx].id,
                    lead_id=leads[lead_idx].id,
                    campaign_id=campaign.id,
                    channel=channel,
                    message_type=msg_type,
                    subject=subject,
                    body=body,
                    requires_approval=needs_approval,
                    status=status,
                    sequence_position=1 if msg_type == "cold" else 2,
                    approved_at=datetime.now(timezone.utc) if status == "approved" else None,
                )
            )

        await db.commit()
        print("Seed data ready")


if __name__ == "__main__":
    asyncio.run(seed())
