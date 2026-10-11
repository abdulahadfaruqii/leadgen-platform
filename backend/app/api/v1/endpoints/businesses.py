"""
Business API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.business import BusinessResponse, BusinessListResponse, BusinessFilter, BusinessUpdate
from app.services.business import business_service_instance

router = APIRouter()


@router.get("", response_model=BusinessListResponse)
async def list_businesses(
    skip: int = 0,
    limit: int = 20,
    filters: BusinessFilter = Depends(),
    db: AsyncSession = Depends(get_db),
):
    items, total = await business_service_instance.get_multi(db, filters, skip, limit)
    return BusinessListResponse(
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        pages=(total + limit - 1) // limit,
        items=items,
    )


@router.get("/{business_id}", response_model=BusinessResponse)
async def get_business(business_id: str, db: AsyncSession = Depends(get_db)):
    business = await business_service_instance.get(db, business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return business


@router.patch("/{business_id}", response_model=BusinessResponse)
async def update_business(
    business_id: str,
    obj_in: BusinessUpdate,
    db: AsyncSession = Depends(get_db),
):
    business = await business_service_instance.get(db, business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    updated = await business_service_instance.update(db, business, obj_in)
    return updated


@router.delete("/{business_id}")
async def delete_business(business_id: str, db: AsyncSession = Depends(get_db)):
    success = await business_service_instance.delete(db, business_id)
    return {"success": success}
