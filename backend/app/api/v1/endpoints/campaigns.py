"""
Campaign API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.schemas.campaign import CampaignCreate, CampaignResponse, CampaignListResponse, CampaignUpdate
from app.schemas.base import IDResponse
from app.services.campaign import campaign_service_instance

router = APIRouter()


def _enqueue_campaign_workflow(**kwargs):
    try:
        from app.workers.celery_app import run_campaign_workflow_task

        return run_campaign_workflow_task.delay(**kwargs)
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Background workers unavailable: {exc}",
        ) from exc


@router.post("", response_model=IDResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    obj_in: CampaignCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    campaign = await campaign_service_instance.create(db, obj_in, user_id)
    return IDResponse(id=campaign.id)


@router.get("", response_model=CampaignListResponse)
async def list_campaigns(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    items, total = await campaign_service_instance.get_multi(db, user_id, skip=skip, limit=limit)
    return CampaignListResponse(
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        pages=(total + limit - 1) // limit if limit else 0,
        items=items,
    )


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    campaign = await campaign_service_instance.get(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return campaign


@router.patch("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    obj_in: CampaignUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    campaign = await campaign_service_instance.get(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    updated = await campaign_service_instance.update(db, campaign, obj_in)
    return updated


@router.post("/{campaign_id}/start")
async def start_campaign(
    campaign_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    campaign = await campaign_service_instance.get(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    await campaign_service_instance.start(db, campaign_id)

    try:
        task = _enqueue_campaign_workflow(
            campaign_id=campaign_id,
            user_id=user_id,
            country=campaign.target_country,
            state=campaign.target_state or "",
            city=campaign.target_city or "",
            categories=campaign.target_categories,
            services=campaign.services,
        )
        return {"success": True, "task_id": task.id, "status": "queued"}
    except HTTPException:
        # Local mode without Celery — campaign still marked started
        return {"success": True, "task_id": None, "status": "started"}


@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    campaign = await campaign_service_instance.get(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    success = await campaign_service_instance.delete(db, campaign_id)
    return {"success": success}
