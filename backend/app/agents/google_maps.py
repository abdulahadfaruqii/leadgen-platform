"""
Agent 2: Google Maps Agent
Searches Google Maps and collects business information.
"""
import asyncio
from typing import Dict, List

from app.agents.base import BaseAgent, AgentContext
from app.tools.search_engine import get_search_engine


class GoogleMapsAgent(BaseAgent):
    """Discovers businesses via Google Maps APIs."""

    name = "GoogleMaps"
    description = "Searches Google Maps and collects business data"

    async def execute(self, context: AgentContext) -> AgentContext:
        self._log_start(context)

        search = get_search_engine()
        all_businesses = []
        seen_ids = set()

        # Process queries in batches
        batch_size = 5
        for i in range(0, len(context.search_queries), batch_size):
            batch = context.search_queries[i:i + batch_size]

            tasks = [
                self._search_single_query(search, query, context)
                for query in batch
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, Exception):
                    self._log_error(context, result)
                    continue

                for business in result:
                    biz_id = business.get("place_id") or business.get("name")
                    if biz_id and biz_id not in seen_ids:
                        seen_ids.add(biz_id)
                        business["_source_query"] = context.search_queries[i]
                        all_businesses.append(business)

            # Rate limiting between batches
            await asyncio.sleep(1)

        context.businesses = all_businesses
        context.metrics["businesses_found"] = len(all_businesses)

        self._log_complete(context, len(all_businesses))
        return context

    async def _search_single_query(
        self,
        search,
        query: str,
        context: AgentContext,
    ) -> List[Dict]:
        """Execute a single search query."""
        location_str = f"{context.city}, {context.state}, {context.country}"

        results = await search.search_google_maps(
            query=query,
            location=location_str,
            max_results=20,
        )

        # Enrich with location context
        for biz in results:
            biz["_target_country"] = context.country
            biz["_target_state"] = context.state
            biz["_target_city"] = context.city
            biz["_target_category"] = self._infer_category(query, context.categories)

        return results

    def _infer_category(self, query: str, categories: List[str]) -> str:
        """Infer business category from search query."""
        query_lower = query.lower()
        for cat in categories:
            if cat.lower() in query_lower:
                return cat
        return categories[0] if categories else "unknown"
