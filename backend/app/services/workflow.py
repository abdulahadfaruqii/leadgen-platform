"""
Workflow Orchestrator - coordinates all 10 agents.
"""
import asyncio
from typing import Dict, List, Optional

from app.agents import (
    AgentContext,
    LocationResearchAgent,
    GoogleMapsAgent,
    WebsiteResearchAgent,
    SocialMediaDiscoveryAgent,
    ContactDiscoveryAgent,
    LeadQualificationAgent,
    ServiceRecommendationAgent,
    PersonalisedOutreachAgent,
    CRMAgent,
    AnalyticsAgent,
)
from app.core.logging import get_logger
from app.db.session import AsyncSessionLocal
from app.models.job import Job

logger = get_logger(__name__)


class WorkflowOrchestrator:
    """Orchestrates the complete 10-agent lead generation workflow."""

    AGENT_PIPELINE = [
        ("research", LocationResearchAgent),
        ("discovery", GoogleMapsAgent),
        ("website_analysis", WebsiteResearchAgent),
        ("social_discovery", SocialMediaDiscoveryAgent),
        ("contact_discovery", ContactDiscoveryAgent),
        ("qualification", LeadQualificationAgent),
        ("recommendation", ServiceRecommendationAgent),
        ("outreach", PersonalisedOutreachAgent),
        ("crm", CRMAgent),
        ("analytics", AnalyticsAgent),
    ]

    async def run_campaign_workflow(
        self,
        campaign_id: str,
        user_id: str,
        country: str,
        state: str,
        city: str,
        categories: List[str],
        services: List[str],
        job_id: Optional[str] = None,
    ) -> Dict:
        """Execute the complete workflow for a campaign."""

        context = AgentContext(
            campaign_id=campaign_id,
            user_id=user_id,
            job_id=job_id,
            country=country,
            state=state,
            city=city,
            categories=categories,
            services=services,
        )

        logger.info(
            "Starting campaign workflow",
            campaign_id=campaign_id,
            city=city,
            categories=categories,
        )

        total_agents = len(self.AGENT_PIPELINE)

        for idx, (stage_name, agent_class) in enumerate(self.AGENT_PIPELINE):
            progress = (idx / total_agents) * 100
            await self._update_job_progress(job_id, stage_name, progress)

            logger.info(f"Executing agent: {agent_class.name}", stage=stage_name)

            try:
                agent = agent_class()
                context = await agent.execute(context)

                # Save checkpoint after each agent
                await self._save_checkpoint(job_id, stage_name, context)

            except Exception as e:
                logger.error(f"Agent {agent_class.name} failed", error=str(e))
                context.errors.append(f"{stage_name}: {str(e)}")

                # Decide whether to continue or abort
                if stage_name in ["research", "discovery", "crm"]:
                    raise  # Critical stages
                # Non-critical stages can fail gracefully

        await self._update_job_progress(job_id, "completed", 100.0)

        return {
            "success": len(context.errors) == 0,
            "campaign_id": campaign_id,
            "businesses_found": len(context.businesses),
            "leads_qualified": len(context.qualified_leads),
            "outreach_generated": len(context.outreach_messages),
            "metrics": context.metrics,
            "errors": context.errors,
        }

    async def resume_workflow(self, job_id: str) -> Dict:
        """Resume a workflow from its last checkpoint."""
        # Load checkpoint from job record
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Job).where(Job.id == job_id)
            )
            job = result.scalar_one_or_none()

            if not job or not job.checkpoint_data:
                raise ValueError(f"No checkpoint found for job {job_id}")

            checkpoint = job.checkpoint_data
            context = AgentContext(**checkpoint.get("context", {}))
            last_completed = checkpoint.get("last_completed_stage")

            # Find where to resume
            resume_from = False
            for stage_name, agent_class in self.AGENT_PIPELINE:
                if resume_from or last_completed == stage_name:
                    resume_from = True
                    continue
                if resume_from:
                    agent = agent_class()
                    context = await agent.execute(context)
                    await self._save_checkpoint(job_id, stage_name, context)

            return {"success": True, "resumed_from": last_completed}

    async def _update_job_progress(self, job_id: Optional[str], stage: str, progress: float):
        if not job_id:
            return

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Job).where(Job.id == job_id)
            )
            job = result.scalar_one_or_none()

            if job:
                job.status = "running"
                job.progress_percent = progress
                await session.commit()

    async def _save_checkpoint(self, job_id: Optional[str], stage: str, context: AgentContext):
        if not job_id:
            return

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Job).where(Job.id == job_id)
            )
            job = result.scalar_one_or_none()

            if job:
                job.checkpoint_data = {
                    "last_completed_stage": stage,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "context": {
                        "campaign_id": context.campaign_id,
                        "user_id": context.user_id,
                        "metrics": context.metrics,
                        "errors": context.errors,
                    },
                }
                await session.commit()


# Singleton
_orchestrator: Optional[WorkflowOrchestrator] = None


def get_orchestrator() -> WorkflowOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = WorkflowOrchestrator()
    return _orchestrator
