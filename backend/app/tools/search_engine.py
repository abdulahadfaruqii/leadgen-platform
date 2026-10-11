"""
Search engine integrations - Google Maps, SERP API, Bing.
"""
import asyncio
from typing import Dict, List, Optional

import httpx

from app.core.config import get_settings
from app.core.exceptions import ScrapingException
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class SearchEngine:
    """Multi-source search engine for business discovery."""

    def __init__(self):
        self.http = httpx.AsyncClient(timeout=30.0, follow_redirects=True)

    async def search_google_maps(
        self,
        query: str,
        location: Optional[str] = None,
        radius: int = 50000,
        max_results: int = 20,
    ) -> List[Dict]:
        """Search Google Maps via SERP API or direct scraping."""

        if settings.SERPAPI_KEY:
            return await self._search_via_serpapi(query, location, max_results)
        elif settings.GOOGLE_MAPS_API_KEY:
            return await self._search_via_google_places(query, location, radius, max_results)
        else:
            logger.warning("No search API configured, returning empty results")
            return []

    async def _search_via_serpapi(
        self,
        query: str,
        location: Optional[str],
        max_results: int,
    ) -> List[Dict]:
        """Search using SERP API."""
        results = []
        start = 0

        while len(results) < max_results:
            params = {
                "engine": "google_maps",
                "q": query,
                "api_key": settings.SERPAPI_KEY,
                "start": start,
                "num": min(20, max_results - len(results)),
            }
            if location:
                params["ll"] = f"@{location},{radius}"

            try:
                response = await self.http.get("https://serpapi.com/search", params=params)
                response.raise_for_status()
                data = response.json()

                local_results = data.get("local_results", [])
                if not local_results:
                    break

                for place in local_results:
                    results.append(self._normalize_place_data(place))

                start += len(local_results)

                if not data.get("serpapi_pagination", {}).get("next"):
                    break

                await asyncio.sleep(1)

            except Exception as e:
                logger.error("SERP API search failed", error=str(e))
                break

        return results[:max_results]

    async def _search_via_google_places(
        self,
        query: str,
        location: Optional[str],
        radius: int,
        max_results: int,
    ) -> List[Dict]:
        """Search using Google Places API (New)."""
        results = []
        next_page_token = None

        while len(results) < max_results:
            payload = {
                "textQuery": query,
                "pageSize": min(20, max_results - len(results)),
            }
            if next_page_token:
                payload["pageToken"] = next_page_token

            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": settings.GOOGLE_MAPS_API_KEY,
                "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location,places.rating,places.userRatingCount,places.websiteUri,places.nationalPhoneNumber,places.primaryType,places.types,places.photos,places.regularOpeningHours,places.editorialSummary",
            }

            try:
                response = await self.http.post(
                    "https://places.googleapis.com/v1/places:searchText",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()

                places = data.get("places", [])
                for place in places:
                    results.append(self._normalize_google_place(place))

                next_page_token = data.get("nextPageToken")
                if not next_page_token:
                    break

                await asyncio.sleep(2)

            except Exception as e:
                logger.error("Google Places API search failed", error=str(e))
                break

        return results[:max_results]

    def _normalize_place_data(self, place: Dict) -> Dict:
        """Normalize SERP API place data."""
        return {
            "place_id": place.get("place_id"),
            "name": place.get("title"),
            "address": place.get("address"),
            "phone": place.get("phone"),
            "website": place.get("website"),
            "rating": place.get("rating"),
            "review_count": place.get("reviews"),
            "latitude": place.get("gps_coordinates", {}).get("latitude"),
            "longitude": place.get("gps_coordinates", {}).get("longitude"),
            "category": place.get("type"),
            "hours": place.get("hours"),
            "photos": [p.get("image") for p in place.get("photos", []) if p.get("image")],
            "description": place.get("description"),
        }

    def _normalize_google_place(self, place: Dict) -> Dict:
        """Normalize Google Places API (New) data."""
        location = place.get("location", {})
        return {
            "place_id": place.get("id"),
            "name": place.get("displayName", {}).get("text"),
            "address": place.get("formattedAddress"),
            "phone": place.get("nationalPhoneNumber"),
            "website": place.get("websiteUri"),
            "rating": place.get("rating"),
            "review_count": place.get("userRatingCount"),
            "latitude": location.get("latitude"),
            "longitude": location.get("longitude"),
            "category": place.get("primaryType"),
            "subcategories": place.get("types", []),
            "hours": place.get("regularOpeningHours", {}).get("weekdayDescriptions"),
            "photos": [p.get("name") for p in place.get("photos", [])],
            "description": place.get("editorialSummary", {}).get("text"),
        }

    async def search_web(
        self,
        query: str,
        max_results: int = 10,
    ) -> List[Dict]:
        """General web search via Bing or SERP API."""
        if settings.BING_SEARCH_API_KEY:
            return await self._search_bing(query, max_results)
        elif settings.SERPAPI_KEY:
            return await self._search_serpapi_web(query, max_results)
        return []

    async def _search_bing(self, query: str, max_results: int) -> List[Dict]:
        headers = {"Ocp-Apim-Subscription-Key": settings.BING_SEARCH_API_KEY}
        params = {"q": query, "count": max_results, "responseFilter": "Webpages"}

        try:
            response = await self.http.get(
                "https://api.bing.microsoft.com/v7.0/search",
                headers=headers,
                params=params,
            )
            response.raise_for_status()
            data = response.json()

            return [
                {
                    "title": item.get("name"),
                    "url": item.get("url"),
                    "snippet": item.get("snippet"),
                }
                for item in data.get("webPages", {}).get("value", [])
            ]
        except Exception as e:
            logger.error("Bing search failed", error=str(e))
            return []

    async def _search_serpapi_web(self, query: str, max_results: int) -> List[Dict]:
        params = {
            "engine": "google",
            "q": query,
            "api_key": settings.SERPAPI_KEY,
            "num": max_results,
        }

        try:
            response = await self.http.get("https://serpapi.com/search", params=params)
            response.raise_for_status()
            data = response.json()

            return [
                {
                    "title": item.get("title"),
                    "url": item.get("link"),
                    "snippet": item.get("snippet"),
                }
                for item in data.get("organic_results", [])
            ]
        except Exception as e:
            logger.error("SERP API web search failed", error=str(e))
            return []

    async def find_social_profiles(self, business_name: str, website: Optional[str] = None) -> Dict[str, str]:
        """Find social media profiles for a business."""
        profiles = {}

        # LinkedIn
        linkedin_query = f"site:linkedin.com/company {business_name}"
        linkedin_results = await self.search_web(linkedin_query, 3)
        for result in linkedin_results:
            url = result.get("url", "")
            if "linkedin.com/company" in url:
                profiles["linkedin"] = url.split("?")[0]
                break

        # Facebook
        fb_query = f"site:facebook.com {business_name}"
        fb_results = await self.search_web(fb_query, 3)
        for result in fb_results:
            url = result.get("url", "")
            if "facebook.com" in url and "pages" not in url:
                profiles["facebook"] = url.split("?")[0]
                break

        # Instagram
        ig_query = f"site:instagram.com {business_name}"
        ig_results = await self.search_web(ig_query, 3)
        for result in ig_results:
            url = result.get("url", "")
            if "instagram.com" in url:
                profiles["instagram"] = url.split("?")[0]
                break

        # Twitter/X
        x_query = f"site:x.com {business_name} OR site:twitter.com {business_name}"
        x_results = await self.search_web(x_query, 3)
        for result in x_results:
            url = result.get("url", "")
            if "x.com/" in url or "twitter.com/" in url:
                profiles["twitter"] = url.split("?")[0]
                break

        return profiles

    async def close(self):
        await self.http.aclose()


# Singleton
_search_engine: Optional[SearchEngine] = None


def get_search_engine() -> SearchEngine:
    global _search_engine
    if _search_engine is None:
        _search_engine = SearchEngine()
    return _search_engine
