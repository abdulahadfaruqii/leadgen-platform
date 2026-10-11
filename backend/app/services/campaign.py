"""
Campaign service - orchestrates campaign lifecycle.
"""
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.campaign import Campaign
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignFilter


class CampaignService:
    """Business logic for campaign entities."""

    async def create(self, db: AsyncSession, obj_in: CampaignCreate, owner_id: str) -> Campaign:
        db_obj = Campaign(
            **obj_in.model_dump(),
            owner_id=owner_id,
            status="draft",
        )
        db.add(db_obj)
        await db.flush()
        return db_obj

    async def get(self, db: AsyncSession, id: str) -> Optional[Campaign]:
        result = await db.execute(select(Campaign).where(Campaign.id == id))
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        owner_id: str,
        filters: Optional[CampaignFilter] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Campaign], int]:
        query = select(Campaign).where(Campaign.owner_id == owner_id)
        count_query = select(func.count(Campaign.id)).where(Campaign.owner_id == owner_id)

        if filters:
            if filters.status:
                query = query.where(Campaign.status == filters.status)
                count_query = count_query.where(Campaign.status == filters.status)
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.where(Campaign.name.ilike(search_term))
                count_query = count_query.where(Campaign.name.ilike(search_term))

        query = query.offset(skip).limit(limit).order_by(Campaign.created_at.desc())

        result = await db.execute(query)
        count_result = await db.execute(count_query)

        return result.scalars().all(), count_result.scalar()

    async def update(self, db: AsyncSession, db_obj: Campaign, obj_in: CampaignUpdate) -> Campaign:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        await db.flush()
        return db_obj

    async def delete(self, db: AsyncSession, id: str) -> bool:
        result = await db.execute(select(Campaign).where(Campaign.id == id))
        obj = result.scalar_one_or_none()
        if obj:
            await db.delete(obj)
            return True
        return False

    async def start(self, db: AsyncSession, campaign_id: str) -> Campaign:
        result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
        campaign = result.scalar_one_or_none()

        if campaign:
            campaign.status = "running"
            campaign.started_at = datetime.now(timezone.utc)
            await db.flush()

        return campaign


campaign_service_instance = CampaignService()
