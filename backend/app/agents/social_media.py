"""
Agent 4: Social Media Discovery Agent
Finds official business social media profiles.
"""
import asyncio
from typing import Dict, List

from app.agents.base import BaseAgent, AgentContext
from app.tools.search_engine import get_search_engine


class SocialMediaDiscoveryAgent(BaseAgent):
    """Discovers social media profiles for businesses."""

    name = "SocialMediaDiscovery"
    description = "Finds official social media profiles for businesses"

    PLATFORMS = [
        "linkedin",
        "facebook",
        "instagram",
        "twitter",
        "youtube",
        "tiktok",
        "pinterest",
        "threads",
        "behance",
        "dribbble",
        "crunchbase",
        "github",
    ]

    async def execute(self, context: AgentContext) -> AgentContext:
        self._log_start(context)

        search = get_search_engine()
        updated_businesses = []

        semaphore = asyncio.Semaphore(5)

        async def _find_profiles(business: Dict) -> Dict:
            async with semaphore:
                if not business.get("name"):
                    return business

                try:
                    profiles = await search.find_social_profiles(
                        business_name=business["name"],
                        website=business.get("website"),
                    )

                    # Only keep verified-looking profiles
                    filtered = self._filter_profiles(profiles, business["name"])

                    business["social_profiles"] = filtered
                    business["_social_discovered"] = True

                except Exception as e:
                    self._log_error(context, e)
                    business["_social_error"] = str(e)

                return business

        tasks = [_find_profiles(b) for b in context.analyzed_businesses]
        updated_businesses = await asyncio.gather(*tasks)

        context.analyzed_businesses = list(updated_businesses)
        context.metrics["social_profiles_found"] = sum(
            1 for b in updated_businesses if b.get("social_profiles")
        )

        self._log_complete(context, len(updated_businesses))
        return context

    def _filter_profiles(self, profiles: Dict[str, str], business_name: str) -> Dict[str, str]:
        """Filter out likely incorrect profiles."""
        filtered = {}
        name_lower = business_name.lower().replace(" ", "")

        for platform, url in profiles.items():
            url_lower = url.lower()
            # Basic heuristic: URL should contain business name or be exact match
            if name_lower in url_lower or any(
                word in url_lower for word in business_name.lower().split() if len(word) > 3
            ):
                filtered[platform] = url

        return filtered
