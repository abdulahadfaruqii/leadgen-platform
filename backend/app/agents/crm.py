"""
Agent 9: CRM Agent
Stores all collected data in structured database.
"""
from datetime import datetime, timezone
from typing import Dict, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import BaseAgent, AgentContext
from app.db.session import AsyncSessionLocal
from app.models.business import Business
from app.models.contact import Contact
from app.models.lead import Lead
from app.models.outreach import Outreach
from app.models.campaign import Campaign


class CRMAgent(BaseAgent):
    """Persists all discovered data to the database."""

    name = "CRM"
    description = "Stores leads, contacts, and outreach in CRM database"

    async def execute(self, context: AgentContext) -> AgentContext:
        self._log_start(context)

        async with AsyncSessionLocal() as session:
            try:
                # Update campaign progress
                await self._update_campaign(session, context)

                # Save businesses
                business_id_map = await self._save_businesses(session, context)

                # Save contacts
                await self._save_contacts(session, context, business_id_map)

                # Save leads
                lead_id_map = await self._save_leads(session, context, business_id_map)

                # Save outreach
                await self._save_outreach(session, context, business_id_map, lead_id_map)

                await session.commit()

                context.metrics["businesses_saved"] = len(business_id_map)
                context.metrics["leads_saved"] = len(lead_id_map)

            except Exception as e:
                await session.rollback()
                self._log_error(context, e)
                raise

        self._log_complete(context)
        return context

    async def _update_campaign(self, session: AsyncSession, context: AgentContext):
        if not context.campaign_id:
            return

        result = await session.execute(
            select(Campaign).where(Campaign.id == context.campaign_id)
        )
        campaign = result.scalar_one_or_none()

        if campaign:
            campaign.businesses_found = context.metrics.get("businesses_found", 0)
            campaign.leads_qualified = context.metrics.get("leads_qualified", 0)
            campaign.outreach_sent = context.metrics.get("outreach_generated", 0)
            campaign.progress_percent = 100.0
            campaign.status = "completed"
            campaign.completed_at = datetime.now(timezone.utc)

    async def _save_businesses(self, session: AsyncSession, context: AgentContext) -> Dict[str, str]:
        """Save businesses and return temp_id -> real_id mapping."""
        id_map = {}

        for biz_data in context.analyzed_businesses:
            temp_id = biz_data.get("id") or biz_data.get("place_id") or biz_data.get("name")

            # Check for duplicates
            existing = await session.execute(
                select(Business).where(
                    (Business.google_place_id == biz_data.get("place_id")) |
                    (
                        (Business.name == biz_data.get("name")) &
                        (Business.city == biz_data.get("_target_city")) &
                        (Business.country == biz_data.get("_target_country"))
                    )
                )
            )

            if existing.scalar_one_or_none():
                continue

            business = Business(
                name=biz_data.get("name", "Unknown"),
                slug=self._slugify(biz_data.get("name", "unknown")),
                category=biz_data.get("_target_category", "unknown"),
                subcategories=biz_data.get("subcategories"),
                country=biz_data.get("_target_country", ""),
                state=biz_data.get("_target_state", ""),
                city=biz_data.get("_target_city", ""),
                address=biz_data.get("address"),
                latitude=biz_data.get("latitude"),
                longitude=biz_data.get("longitude"),
                website=biz_data.get("website"),
                phone=biz_data.get("phone"),
                email=biz_data.get("email"),
                google_place_id=biz_data.get("place_id"),
                google_rating=biz_data.get("rating"),
                google_review_count=biz_data.get("review_count"),
                google_hours=biz_data.get("hours"),
                google_photos=biz_data.get("photos"),
                google_url=biz_data.get("google_url"),
                website_quality_score=biz_data.get("website_quality_score"),
                mobile_responsive=biz_data.get("mobile_responsive"),
                page_speed_score=biz_data.get("page_speed_score"),
                seo_score=biz_data.get("seo_score"),
                detected_technologies=biz_data.get("detected_technologies"),
                missing_features=biz_data.get("missing_features"),
                website_issues=biz_data.get("website_issues"),
                has_booking_system=biz_data.get("has_booking_system"),
                has_online_ordering=biz_data.get("has_online_ordering"),
                has_crm=biz_data.get("has_crm"),
                has_chatbot=biz_data.get("has_chatbot"),
                has_mobile_app=biz_data.get("has_mobile_app"),
                has_analytics=biz_data.get("has_analytics"),
                has_customer_portal=biz_data.get("has_customer_portal"),
                social_profiles=biz_data.get("social_profiles"),
                lead_score=biz_data.get("website_quality_score"),  # Initial score
                status="discovered",
                source_campaign_id=context.campaign_id,
            )

            session.add(business)
            await session.flush()
            id_map[temp_id] = business.id

        return id_map

    async def _save_contacts(self, session: AsyncSession, context: AgentContext, id_map: Dict):
        contacts = context.checkpoint.get("contacts", [])

        for contact_data in contacts:
            temp_biz_id = contact_data.get("business_id")
            real_biz_id = id_map.get(temp_biz_id)

            if not real_biz_id:
                continue

            contact = Contact(
                business_id=real_biz_id,
                first_name=contact_data.get("first_name"),
                last_name=contact_data.get("last_name"),
                full_name=contact_data.get("full_name"),
                title=contact_data.get("title"),
                role=contact_data.get("role"),
                email=contact_data.get("email"),
                phone=contact_data.get("phone"),
                source=contact_data.get("source", "discovered"),
                is_primary=contact_data.get("is_primary", False),
                confidence_score=contact_data.get("confidence_score"),
            )
            session.add(contact)

    async def _save_leads(self, session: AsyncSession, context: AgentContext, id_map: Dict) -> Dict[str, str]:
        lead_id_map = {}

        for lead_data in context.qualified_leads:
            temp_biz_id = lead_data["business_data"].get("id")
            real_biz_id = id_map.get(temp_biz_id)

            if not real_biz_id:
                continue

            lead = Lead(
                business_id=real_biz_id,
                campaign_id=context.campaign_id,
                overall_score=lead_data["overall_score"],
                website_quality_score=lead_data.get("website_quality_score"),
                digital_presence_score=lead_data.get("digital_presence_score"),
                technology_score=lead_data.get("technology_score"),
                social_activity_score=lead_data.get("social_activity_score"),
                review_score=lead_data.get("review_score"),
                growth_score=lead_data.get("growth_score"),
                opportunity_score=lead_data.get("opportunity_score"),
                qualification_reasons=lead_data.get("qualification_reasons"),
                priority=lead_data["priority"],
                recommended_services=lead_data.get("recommended_services"),
                outreach_status="pending",
            )

            session.add(lead)
            await session.flush()
            lead_id_map[id(lead_data)] = lead.id

        return lead_id_map

    async def _save_outreach(
        self,
        session: AsyncSession,
        context: AgentContext,
        business_id_map: Dict,
        lead_id_map: Dict,
    ):
        for msg_data in context.outreach_messages:
            temp_biz_id = msg_data.get("business_id")
            real_biz_id = business_id_map.get(temp_biz_id)

            if not real_biz_id:
                continue

            outreach = Outreach(
                business_id=real_biz_id,
                lead_id=msg_data.get("lead_id"),
                campaign_id=context.campaign_id,
                channel=msg_data["channel"],
                message_type=msg_data["message_type"],
                subject=msg_data.get("subject"),
                body=msg_data["body"],
                body_html=msg_data.get("body_html"),
                personalization_data=msg_data.get("personalization_data"),
                status="draft",
                requires_approval=msg_data.get("requires_approval", True),
                sequence_position=msg_data.get("sequence_position", 1),
                is_automated=False,
            )
            session.add(outreach)

    def _slugify(self, text: str) -> str:
        import re
        return re.sub(r"[^\w\s-]", "", text).strip().lower().replace(" ", "-")[:100]
