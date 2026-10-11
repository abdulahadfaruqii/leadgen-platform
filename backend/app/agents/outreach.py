"""
Agent 8: Personalised Outreach Agent
Generates highly personalised outreach messages.
"""
import json
from typing import Dict, List, Optional

from app.agents.base import BaseAgent, AgentContext


class PersonalisedOutreachAgent(BaseAgent):
    """Generates personalised cold outreach messages."""

    name = "PersonalisedOutreach"
    description = "Creates personalised outreach emails and messages"

    CHANNELS = ["email", "linkedin", "facebook", "instagram", "contact_form"]
    MESSAGE_TYPES = ["cold", "follow_up", "reminder"]

    async def execute(self, context: AgentContext) -> AgentContext:
        self._log_start(context)

        all_outreach = []

        for lead in context.qualified_leads:
            try:
                outreach = await self._generate_outreach_for_lead(lead, context)
                all_outreach.extend(outreach)
            except Exception as e:
                self._log_error(context, e)

        context.outreach_messages = all_outreach
        context.metrics["outreach_generated"] = len(all_outreach)

        self._log_complete(context, len(all_outreach))
        return context

    async def _generate_outreach_for_lead(self, lead: Dict, context: AgentContext) -> List[Dict]:
        """Generate outreach messages for a single lead."""
        business = lead["business_data"]
        recommendations = lead.get("recommended_services", [])

        if not recommendations:
            return []

        messages = []

        # Primary contact (email)
        primary_service = recommendations[0]

        # Cold Email
        email = await self._generate_email(business, lead, primary_service, context)
        messages.append({
            "business_id": business.get("id"),
            "lead_id": lead.get("id"),
            "channel": "email",
            "message_type": "cold",
            "subject": email.get("subject"),
            "body": email.get("body"),
            "body_html": email.get("body_html"),
            "personalization_data": email.get("personalization"),
            "requires_approval": True,
            "sequence_position": 1,
        })

        # LinkedIn Message
        if business.get("social_profiles", {}).get("linkedin"):
            linkedin_msg = await self._generate_linkedin(business, lead, primary_service)
            messages.append({
                "business_id": business.get("id"),
                "lead_id": lead.get("id"),
                "channel": "linkedin",
                "message_type": "cold",
                "body": linkedin_msg,
                "requires_approval": True,
                "sequence_position": 1,
            })

        # Follow-up sequence (2 more emails)
        for i, follow_up in enumerate(["value_add", "soft_close"], start=2):
            fu_email = await self._generate_follow_up(
                business, lead, primary_service, follow_up, i
            )
            messages.append({
                "business_id": business.get("id"),
                "lead_id": lead.get("id"),
                "channel": "email",
                "message_type": "follow_up",
                "subject": fu_email.get("subject"),
                "body": fu_email.get("body"),
                "requires_approval": True,
                "sequence_position": i,
            })

        return messages

    async def _generate_email(
        self,
        business: Dict,
        lead: Dict,
        service: Dict,
        context: AgentContext,
    ) -> Dict:
        """Generate a personalised cold email."""

        system_prompt = """You are a senior business development consultant writing personalised cold emails.
        Rules:
        - Professional, respectful tone
        - No spammy language, no ALL CAPS, no excessive exclamation marks
        - Specific observations about their business
        - Clear value proposition
        - Soft, respectful call to action
        - Keep under 150 words
        - Return JSON with 'subject', 'body', 'body_html', 'personalization' fields"""

        user_prompt = self._build_outreach_prompt(business, lead, service, "email")

        try:
            response = await self._ai_chat(system_prompt, user_prompt, json_mode=True, temperature=0.7)
            return json.loads(response)
        except Exception as e:
            self.logger.warning(f"Email generation failed: {e}")
            return self._fallback_email(business, service)

    async def _generate_linkedin(self, business: Dict, lead: Dict, service: Dict) -> str:
        """Generate a LinkedIn connection message."""

        system_prompt = """Write a brief, professional LinkedIn connection request or message.
        - Under 300 characters for connection requests
        - Mention specific observation about their business
        - Soft value proposition
        - Return plain text only"""

        user_prompt = self._build_outreach_prompt(business, lead, service, "linkedin")

        try:
            return await self._ai_chat(system_prompt, user_prompt, temperature=0.7)
        except Exception:
            return self._fallback_linkedin(business, service)

    async def _generate_follow_up(
        self,
        business: Dict,
        lead: Dict,
        service: Dict,
        follow_up_type: str,
        position: int,
    ) -> Dict:
        """Generate a follow-up email."""

        system_prompt = """Write a polite follow-up email. Be brief, add value, no pressure.
        Return JSON with 'subject' and 'body' fields."""

        user_prompt = f"""Business: {business.get('name')}
        Service: {service['service_name']}
        Follow-up type: {follow_up_type}
        Sequence position: {position}

        Write a {follow_up_type} follow-up email."""

        try:
            response = await self._ai_chat(system_prompt, user_prompt, json_mode=True, temperature=0.6)
            return json.loads(response)
        except Exception:
            return {
                "subject": f"Re: {business.get('name')} - Quick follow-up",
                "body": f"Hi there,\n\nI wanted to follow up on my previous message about helping {business.get('name')} with {service['service_name']}.\n\nWould you be open to a brief 10-minute call next week?\n\nBest regards",
            }

    def _build_outreach_prompt(self, business: Dict, lead: Dict, service: Dict, channel: str) -> str:
        """Build the prompt for outreach generation."""

        parts = [
            f"Business Name: {business.get('name')}",
            f"Industry: {business.get('_target_category')}",
            f"Location: {business.get('_target_city')}, {business.get('_target_state')}",
            f"Website: {business.get('website', 'No website')}",
        ]

        if business.get("google_rating"):
            parts.append(f"Rating: {business['google_rating']}/5 ({business.get('google_review_count', 0)} reviews)")

        parts.extend([
            f"\nWebsite Issues: {json.dumps(business.get('website_issues', [])[:3])}",
            f"Missing Features: {json.dumps(business.get('missing_features', [])[:3])}",
            f"\nRecommended Service: {service['service_name']}",
            f"Service Fit Score: {service['fit_score']}/100",
            f"\nChannel: {channel}",
            "\nGenerate personalised outreach.",
        ])

        return "\n".join(parts)

    def _fallback_email(self, business: Dict, service: Dict) -> Dict:
        name = business.get("name", "there")
        return {
            "subject": f"Quick question about {name}'s online presence",
            "body": f"Hi,\n\nI came across {name} and was impressed by your reputation. I noticed there might be an opportunity to enhance your digital presence with {service['service_name']}.\n\nWe specialize in helping businesses like yours modernize their technology. Would you be open to a brief conversation?\n\nBest regards",
            "body_html": None,
            "personalization": {},
        }

    def _fallback_linkedin(self, business: Dict, service: Dict) -> str:
        return f"Hi, I came across {business.get('name')} and noticed an opportunity to help with {service['service_name']}. Would love to connect and share some insights."
