"""
Analytics API endpoints.
"""
from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.business import Business
from app.models.lead import Lead
from app.models.outreach import Outreach

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_metrics(db: AsyncSession = Depends(get_db)):
    total_businesses = (await db.execute(select(func.count(Business.id)))).scalar() or 0
    total_leads = (await db.execute(select(func.count(Lead.id)))).scalar() or 0
    total_outreach = (await db.execute(select(func.count(Outreach.id)))).scalar() or 0
    total_sent = (
        await db.execute(select(func.count(Outreach.id)).where(Outreach.status.in_(["sent", "opened", "replied", "clicked"])))
    ).scalar() or 0
    total_replies = (
        await db.execute(select(func.count(Outreach.id)).where(Outreach.replied_at.is_not(None)))
    ).scalar() or 0
    avg_score = (await db.execute(select(func.avg(Lead.overall_score)))).scalar() or 0.0

    category_rows = (
        await db.execute(
            select(Business.category, func.count(Business.id))
            .group_by(Business.category)
            .order_by(func.count(Business.id).desc())
            .limit(8)
        )
    ).all()

    country_rows = (
        await db.execute(
            select(Business.country, func.count(Business.id))
            .group_by(Business.country)
            .order_by(func.count(Business.id).desc())
            .limit(8)
        )
    ).all()

    scores = (await db.execute(select(Lead.overall_score))).scalars().all()
    buckets = Counter()
    for score in scores:
        value = float(score or 0)
        if value <= 20:
            buckets["0-20"] += 1
        elif value <= 40:
            buckets["21-40"] += 1
        elif value <= 60:
            buckets["41-60"] += 1
        elif value <= 80:
            buckets["61-80"] += 1
        else:
            buckets["81-100"] += 1

    conversion_rate = (total_replies / total_sent * 100) if total_sent else 0.0

    return {
        "total_businesses_found": total_businesses,
        "total_leads_qualified": total_leads,
        "total_outreach_sent": total_sent or total_outreach,
        "total_responses": total_replies,
        "avg_lead_score": round(float(avg_score), 1),
        "conversion_rate": round(conversion_rate, 1),
        "top_categories": [{"name": name, "count": count} for name, count in category_rows],
        "top_countries": [{"name": name, "count": count} for name, count in country_rows],
        "score_distribution": [
            {"range": label, "count": buckets.get(label, 0)}
            for label in ["0-20", "21-40", "41-60", "61-80", "81-100"]
        ],
        "weekly_activity": [],
        "outreach_funnel": {
            "sent": total_sent or total_outreach,
            "opened": (
                await db.execute(select(func.count(Outreach.id)).where(Outreach.opened_at.is_not(None)))
            ).scalar()
            or 0,
            "clicked": (
                await db.execute(select(func.count(Outreach.id)).where(Outreach.clicked_at.is_not(None)))
            ).scalar()
            or 0,
            "replied": total_replies,
        },
    }


@router.get("/campaigns/{campaign_id}")
async def get_campaign_metrics(campaign_id: str, db: AsyncSession = Depends(get_db)):
    businesses_found = (
        await db.execute(
            select(func.count(Business.id)).where(Business.source_campaign_id == campaign_id)
        )
    ).scalar() or 0
    leads_qualified = (
        await db.execute(select(func.count(Lead.id)).where(Lead.campaign_id == campaign_id))
    ).scalar() or 0
    outreach_sent = (
        await db.execute(select(func.count(Outreach.id)).where(Outreach.campaign_id == campaign_id))
    ).scalar() or 0

    return {
        "campaign_id": campaign_id,
        "businesses_found": businesses_found,
        "leads_qualified": leads_qualified,
        "outreach_sent": outreach_sent,
    }
