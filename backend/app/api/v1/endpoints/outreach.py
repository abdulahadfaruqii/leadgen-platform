"""
Outreach API endpoints.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.outreach import Outreach
from app.schemas.outreach import OutreachResponse, OutreachListResponse, OutreachFilter, OutreachUpdate, OutreachApprove

router = APIRouter()


@router.get("", response_model=OutreachListResponse)
async def list_outreach(
    skip: int = 0,
    limit: int = 20,
    filters: OutreachFilter = Depends(),
    db: AsyncSession = Depends(get_db),
):
    query = select(Outreach)
    count_query = select(Outreach)

    if filters.campaign_id:
        query = query.where(Outreach.campaign_id == filters.campaign_id)
    if filters.status:
        query = query.where(Outreach.status == filters.status)
    if filters.channel:
        query = query.where(Outreach.channel == filters.channel)

    from sqlalchemy import func
    count_query = select(func.count(Outreach.id))

    result = await db.execute(query.offset(skip).limit(limit))
    count_result = await db.execute(count_query)

    items = result.scalars().all()
    total = count_result.scalar()

    return OutreachListResponse(
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        pages=(total + limit - 1) // limit,
        items=items,
    )


@router.get("/{outreach_id}", response_model=OutreachResponse)
async def get_outreach(outreach_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Outreach).where(Outreach.id == outreach_id))
    outreach = result.scalar_one_or_none()
    if not outreach:
        raise HTTPException(status_code=404, detail="Outreach not found")
    return outreach


@router.patch("/{outreach_id}", response_model=OutreachResponse)
async def update_outreach(
    outreach_id: str,
    obj_in: OutreachUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Outreach).where(Outreach.id == outreach_id))
    outreach = result.scalar_one_or_none()
    if not outreach:
        raise HTTPException(status_code=404, detail="Outreach not found")

    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(outreach, field, value)
    await db.flush()
    return outreach


@router.post("/{outreach_id}/approve", response_model=OutreachResponse)
async def approve_outreach(
    outreach_id: str,
    obj_in: OutreachApprove,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Outreach).where(Outreach.id == outreach_id))
    outreach = result.scalar_one_or_none()
    if not outreach:
        raise HTTPException(status_code=404, detail="Outreach not found")

    outreach.requires_approval = not obj_in.approved
    outreach.approved_at = datetime.now(timezone.utc) if obj_in.approved else None
    await db.flush()
    return outreach
