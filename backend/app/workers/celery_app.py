"""
Celery configuration and task definitions.
"""
from celery import Celery
from celery.signals import task_failure, task_success

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "leadgen",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_routes={
        "app.workers.tasks.run_campaign_workflow": {"queue": "research"},
        "app.workers.tasks.scrape_website": {"queue": "scraping"},
        "app.workers.tasks.analyze_business": {"queue": "analysis"},
        "app.workers.tasks.generate_outreach": {"queue": "outreach"},
    },
)


@celery_app.task(bind=True, max_retries=3)
def run_campaign_workflow_task(self, **kwargs):
    """Main campaign workflow task."""
    import asyncio
    from app.services.workflow import get_orchestrator

    async def _run():
        orchestrator = get_orchestrator()
        return await orchestrator.run_campaign_workflow(**kwargs)

    return asyncio.run(_run())
