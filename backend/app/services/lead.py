"""
Lead service - CRUD and qualification operations.
"""
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.lead import Lead
from app.schemas.lead import LeadCreate, LeadUpdate, LeadFilter


class LeadService:
    """Business logic for lead entities."""

    async def create(self, db: AsyncSession, obj_in: LeadCreate) -> Lead:
        db_obj = Lead(**obj_in.model_dump())
        db.add(db_obj)
        await db.flush()
        return db_obj

    async def get(self, db: AsyncSession, id: str) -> Optional[Lead]:
        result = await db.execute(
            select(Lead).options(selectinload(Lead.business)).where(Lead.id == id)
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        filters: Optional[LeadFilter] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Lead], int]:
        query = select(Lead).options(selectinload(Lead.business))
        count_query = select(func.count(Lead.id))

        if filters:
            if filters.campaign_id:
                query = query.where(Lead.campaign_id == filters.campaign_id)
                count_query = count_query.where(Lead.campaign_id == filters.campaign_id)
            if filters.priority:
                query = query.where(Lead.priority == filters.priority)
                count_query = count_query.where(Lead.priority == filters.priority)
            if filters.outreach_status:
                query = query.where(Lead.outreach_status == filters.outreach_status)
                count_query = count_query.where(Lead.outreach_status == filters.outreach_status)
            if filters.min_score is not None:
                query = query.where(Lead.overall_score >= filters.min_score)
                count_query = count_query.where(Lead.overall_score >= filters.min_score)

        query = query.order_by(Lead.overall_score.desc()).offset(skip).limit(limit)

        result = await db.execute(query)
        count_result = await db.execute(count_query)

        return result.scalars().all(), count_result.scalar()

    async def update(self, db: AsyncSession, db_obj: Lead, obj_in: LeadUpdate) -> Lead:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        await db.flush()
        return db_obj

    async def get_by_campaign(self, db: AsyncSession, campaign_id: str) -> List[Lead]:
        result = await db.execute(
            select(Lead).where(Lead.campaign_id == campaign_id).order_by(Lead.overall_score.desc())
        )
        return result.scalars().all()


lead_service_instance = LeadService()
