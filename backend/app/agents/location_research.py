"""
Agent 1: Location Research Agent
Generates intelligent search queries for business discovery.
"""
import json
from typing import List

from app.agents.base import BaseAgent, AgentContext


class LocationResearchAgent(BaseAgent):
    """Generates hundreds of search variations for business discovery."""

    name = "LocationResearch"
    description = "Generates intelligent search queries for target locations and categories"

    # Query templates for different categories
    QUERY_TEMPLATES = {
        "default": [
            "best {category} {city}",
            "top {category} {city} {state}",
            "{category} near me {city}",
            "{category} {city} reviews",
            "affordable {category} {city}",
            "{category} services {city} {state}",
            "professional {category} {city}",
            "{category} {city} directory",
            "{category} in {city} {state}",
            "{category} {state} {city}",
        ],
        "healthcare": [
            "best {category} {city}",
            "{category} clinic {city}",
            "{category} office {city} {state}",
            "top rated {category} {city}",
            "{category} near {city}",
            "{category} {city} appointment",
            "family {category} {city}",
            "emergency {category} {city}",
        ],
        "food": [
            "best {category} {city}",
            "top rated {category} {city}",
            "{category} {city} {state}",
            "popular {category} {city}",
            "{category} near me {city}",
            "{category} delivery {city}",
            "{category} reservations {city}",
            "new {category} {city}",
        ],
        "retail": [
            "best {category} {city}",
            "{category} store {city}",
            "{category} shop {city} {state}",
            "{category} near {city}",
            "{category} {city} hours",
            "{category} {city} deals",
        ],
        "professional": [
            "best {category} {city}",
            "{category} firm {city} {state}",
            "{category} office {city}",
            "top {category} {city}",
            "{category} services {city}",
            "{category} consultation {city}",
        ],
    }

    CATEGORY_MAPPINGS = {
        "dentists": "healthcare",
        "doctors": "healthcare",
        "medical clinics": "healthcare",
        "hospitals": "healthcare",
        "restaurants": "food",
        "cafes": "food",
        "bars": "food",
        "hotels": "retail",
        "gyms": "retail",
        "salons": "retail",
        "beauty salons": "retail",
        "law firms": "professional",
        "accountants": "professional",
        "consultants": "professional",
        "real estate": "professional",
        "construction": "professional",
    }

    async def execute(self, context: AgentContext) -> AgentContext:
        self._log_start(context)

        queries = []

        for category in context.categories:
            category_lower = category.lower()
            template_key = self.CATEGORY_MAPPINGS.get(category_lower, "default")
            templates = self.QUERY_TEMPLATES.get(template_key, self.QUERY_TEMPLATES["default"])

            # Generate base queries
            for template in templates:
                query = template.format(
                    category=category,
                    city=context.city,
                    state=context.state,
                )
                queries.append(query)

            # Generate AI-enhanced variations
            ai_queries = await self._generate_ai_queries(context, category)
            queries.extend(ai_queries)

        # Deduplicate while preserving order
        seen = set()
        context.search_queries = [q for q in queries if not (q in seen or seen.add(q))]

        self._log_complete(context, len(context.search_queries))
        return context

    async def _generate_ai_queries(self, context: AgentContext, category: str) -> List[str]:
        """Use AI to generate additional targeted queries."""
        system_prompt = """You are a local business search expert. Generate 15 diverse Google Maps search queries to find businesses.
        Return ONLY a JSON array of strings. No other text."""

        user_prompt = f"""Generate search queries to find {category} in {context.city}, {context.state}, {context.country}.

        Consider:
        - Different ways people search (best, top, affordable, near me, etc.)
        - Specific neighborhoods in {context.city}
        - Service-specific terms
        - Review-focused searches
        - New business searches

        Return exactly 15 queries as a JSON array."""

        try:
            response = await self._ai_chat(system_prompt, user_prompt, json_mode=True)
            queries = json.loads(response)
            if isinstance(queries, list):
                return [q for q in queries if isinstance(q, str)]
        except Exception as e:
            self.logger.warning(f"AI query generation failed: {e}")

        return []
