"""
API router aggregation.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, businesses, campaigns, leads, outreach, analytics, jobs

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["Campaigns"])
api_router.include_router(businesses.router, prefix="/businesses", tags=["Businesses"])
api_router.include_router(leads.router, prefix="/leads", tags=["Leads"])
api_router.include_router(outreach.router, prefix="/outreach", tags=["Outreach"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
