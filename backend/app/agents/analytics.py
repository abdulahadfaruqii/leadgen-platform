"""
Agent 10: Analytics Agent
Tracks metrics and creates analytics events.
"""
from datetime import datetime, timezone
from typing import Dict, List

from app.agents.base import BaseAgent, AgentContext
from app.db.mongo import get_mongo_db


class AnalyticsAgent(BaseAgent):
    """Tracks workflow metrics and stores analytics events."""

    name = "Analytics"
    description = "Tracks metrics and generates analytics"

    async def execute(self, context: AgentContext) -> AgentContext:
        self._log_start(context)

        try:
            db = get_mongo_db()

            # Store workflow completion event
            await db.analytics_events.insert_one({
                "event_type": "workflow",
                "event_name": "campaign_workflow_completed",
                "campaign_id": context.campaign_id,
                "user_id": context.user_id,
                "metric_value": context.metrics.get("leads_qualified", 0),
                "metric_unit": "leads",
                "dimensions": {
                    "country": context.country,
                    "state": context.state,
                    "city": context.city,
                    "categories": context.categories,
                },
                "payload": {
                    "metrics": context.metrics,
                    "errors": context.errors,
                    "businesses_found": len(context.businesses),
                    "leads_qualified": len(context.qualified_leads),
                    "outreach_generated": len(context.outreach_messages),
                },
                "occurred_at": datetime.now(timezone.utc),
            })

            # Store per-business events
            events = []
            for lead in context.qualified_leads:
                business = lead["business_data"]
                events.append({
                    "event_type": "lead",
                    "event_name": "lead_qualified",
                    "campaign_id": context.campaign_id,
                    "business_id": business.get("id"),
                    "metric_value": lead["overall_score"],
                    "metric_unit": "score",
                    "dimensions": {
                        "category": business.get("_target_category"),
                        "city": business.get("_target_city"),
                        "priority": lead["priority"],
                    },
                    "occurred_at": datetime.now(timezone.utc),
                })

            if events:
                await db.analytics_events.insert_many(events)

            context.metrics["analytics_events_stored"] = len(events) + 1

        except Exception as e:
            self._log_error(context, e)

        self._log_complete(context)
        return context

    async def get_dashboard_metrics(self, user_id: str) -> Dict:
        """Get dashboard metrics for a user."""
        db = get_mongo_db()

        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": "$event_type",
                "count": {"$sum": 1},
                "total_value": {"$sum": "$metric_value"},
            }},
        ]

        results = await db.analytics_events.aggregate(pipeline).to_list(length=100)

        return {
            "events_by_type": {r["_id"]: {"count": r["count"], "total_value": r["total_value"]} for r in results},
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
