"""
Business service - CRUD and search operations.
"""
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business import Business
from app.schemas.business import BusinessCreate, BusinessUpdate, BusinessFilter


class BusinessService:
    """Business logic for business entities."""

    async def create(self, db: AsyncSession, obj_in: BusinessCreate) -> Business:
        db_obj = Business(**obj_in.model_dump())
        db.add(db_obj)
        await db.flush()
        return db_obj

    async def get(self, db: AsyncSession, id: str) -> Optional[Business]:
        result = await db.execute(select(Business).where(Business.id == id))
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        filters: Optional[BusinessFilter] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Business], int]:
        query = select(Business)
        count_query = select(func.count(Business.id))

        if filters:
            if filters.country:
                query = query.where(Business.country == filters.country)
                count_query = count_query.where(Business.country == filters.country)
            if filters.state:
                query = query.where(Business.state == filters.state)
                count_query = count_query.where(Business.state == filters.state)
            if filters.city:
                query = query.where(Business.city == filters.city)
                count_query = count_query.where(Business.city == filters.city)
            if filters.category:
                query = query.where(Business.category == filters.category)
                count_query = count_query.where(Business.category == filters.category)
            if filters.status:
                query = query.where(Business.status == filters.status)
                count_query = count_query.where(Business.status == filters.status)
            if filters.min_score is not None:
                query = query.where(Business.lead_score >= filters.min_score)
                count_query = count_query.where(Business.lead_score >= filters.min_score)
            if filters.search:
                search_term = f"%{filters.search.lower()}%"
                query = query.where(func.lower(Business.name).like(search_term))
                count_query = count_query.where(func.lower(Business.name).like(search_term))

        query = query.order_by(Business.lead_score.desc()).offset(skip).limit(limit)

        result = await db.execute(query)
        count_result = await db.execute(count_query)

        return result.scalars().all(), count_result.scalar()

    async def update(self, db: AsyncSession, db_obj: Business, obj_in: BusinessUpdate) -> Business:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        await db.flush()
        return db_obj

    async def delete(self, db: AsyncSession, id: str) -> bool:
        result = await db.execute(select(Business).where(Business.id == id))
        obj = result.scalar_one_or_none()
        if obj:
            await db.delete(obj)
            return True
        return False


business_service_instance = BusinessService()
