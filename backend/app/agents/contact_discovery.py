"""
Agent 5: Contact Discovery Agent
Collects publicly available contact information.
"""
import asyncio
import json
from typing import Dict, List, Optional

from app.agents.base import BaseAgent, AgentContext
from app.tools.web_scraper import get_scraper


class ContactDiscoveryAgent(BaseAgent):
    """Discovers contact information from websites and public sources."""

    name = "ContactDiscovery"
    description = "Collects publicly available business contact details"

    PAGES_TO_CHECK = ["contact", "about", "team", "careers", "help", "support"]

    async def execute(self, context: AgentContext) -> AgentContext:
        self._log_start(context)

        scraper = get_scraper()
        all_contacts = []

        semaphore = asyncio.Semaphore(3)

        async def _discover_for_business(business: Dict) -> List[Dict]:
            async with semaphore:
                contacts = []

                # Extract from website if available
                if business.get("website"):
                    web_contacts = await self._extract_from_website(scraper, business)
                    contacts.extend(web_contacts)

                # Extract from Google Maps data
                if business.get("phone"):
                    contacts.append({
                        "business_id": business.get("id", "temp"),
                        "phone": business["phone"],
                        "source": "google_maps",
                        "is_primary": True,
                    })

                if business.get("email"):
                    contacts.append({
                        "business_id": business.get("id", "temp"),
                        "email": business["email"],
                        "source": "google_maps",
                        "is_primary": True,
                    })

                # AI enrichment for contact inference
                if not contacts and business.get("name"):
                    inferred = await self._ai_infer_contacts(business)
                    contacts.extend(inferred)

                return contacts

        tasks = [_discover_for_business(b) for b in context.analyzed_businesses]
        results = await asyncio.gather(*tasks)

        for contact_list in results:
            all_contacts.extend(contact_list)

        context.metrics["contacts_discovered"] = len(all_contacts)
        # Store contacts in context for CRM agent
        context.checkpoint["contacts"] = all_contacts

        self._log_complete(context, len(all_contacts))
        return context

    async def _extract_from_website(self, scraper, business: Dict) -> List[Dict]:
        """Extract contact info from business website pages."""
        contacts = []
        base_url = business["website"]
        if not base_url.startswith("http"):
            base_url = f"https://{base_url}"

        urls = [f"{base_url.rstrip('/')}/{page}" for page in self.PAGES_TO_CHECK]
        urls.insert(0, base_url)  # Home page first

        results = await scraper.scrape_multiple(urls=urls[:3], concurrency=2)

        all_emails = set()
        all_phones = set()

        for result in results:
            if result.get("success"):
                all_emails.update(result.get("emails", []))
                all_phones.update(result.get("phones", []))

        # Categorize emails
        for email in all_emails:
            email_lower = email.lower()
            role = "general"
            if any(x in email_lower for x in ["sales", "biz"]):
                role = "sales"
            elif any(x in email_lower for x in ["support", "help"]):
                role = "support"
            elif any(x in email_lower for x in ["info", "contact", "hello"]):
                role = "info"
            elif any(x in email_lower for x in ["marketing", "promo"]):
                role = "marketing"

            contacts.append({
                "business_id": business.get("id", "temp"),
                "email": email,
                "role": role,
                "source": "website",
                "confidence_score": 0.8,
            })

        for phone in all_phones:
            contacts.append({
                "business_id": business.get("id", "temp"),
                "phone": phone,
                "source": "website",
                "confidence_score": 0.9,
            })

        return contacts

    async def _ai_infer_contacts(self, business: Dict) -> List[Dict]:
        """Use AI to infer likely contact patterns."""
        # This is a placeholder - in production, you'd use pattern matching
        # Never fabricate emails, but you can suggest likely patterns
        return []
