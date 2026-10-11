"""
Lead API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.lead import LeadResponse, LeadListResponse, LeadFilter, LeadUpdate
from app.services.lead import lead_service_instance

router = APIRouter()


@router.get("", response_model=LeadListResponse)
async def list_leads(
    skip: int = 0,
    limit: int = 20,
    filters: LeadFilter = Depends(),
    db: AsyncSession = Depends(get_db),
):
    items, total = await lead_service_instance.get_multi(db, filters, skip, limit)
    return LeadListResponse(
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        pages=(total + limit - 1) // limit,
        items=items,
    )


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(lead_id: str, db: AsyncSession = Depends(get_db)):
    lead = await lead_service_instance.get(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.patch("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: str,
    obj_in: LeadUpdate,
    db: AsyncSession = Depends(get_db),
):
    lead = await lead_service_instance.get(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    updated = await lead_service_instance.update(db, lead, obj_in)
    return updated
