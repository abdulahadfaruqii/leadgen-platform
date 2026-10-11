"""
Agent 3: Website Research Agent
Analyzes business websites for opportunities.
"""
import asyncio
import json
from typing import Dict, List, Optional

from app.agents.base import BaseAgent, AgentContext
from app.tools.web_scraper import get_scraper


class WebsiteResearchAgent(BaseAgent):
    """Analyzes business websites for quality, tech stack, and opportunities."""

    name = "WebsiteResearch"
    description = "Analyzes websites for quality, technology, and improvement opportunities"

    # Pages to analyze
    PAGES_TO_CHECK = ["", "about", "services", "pricing", "contact", "blog", "portfolio", "team", "careers"]

    async def execute(self, context: AgentContext) -> AgentContext:
        self._log_start(context)

        scraper = get_scraper()
        analyzed = []

        # Filter businesses with websites
        businesses_with_websites = [
            b for b in context.businesses
            if b.get("website")
        ]

        # Analyze in controlled batches
        semaphore = asyncio.Semaphore(3)

        async def _analyze_business(business: Dict) -> Dict:
            async with semaphore:
                try:
                    return await self._analyze_single_business(scraper, business)
                except Exception as e:
                    self._log_error(context, e)
                    business["_website_error"] = str(e)
                    return business

        tasks = [_analyze_business(b) for b in businesses_with_websites]
        results = await asyncio.gather(*tasks)

        # Merge with businesses that don't have websites
        analyzed.extend(results)
        for b in context.businesses:
            if not b.get("website"):
                b["_website_analyzed"] = False
                analyzed.append(b)

        context.analyzed_businesses = analyzed
        context.metrics["websites_analyzed"] = len(businesses_with_websites)

        self._log_complete(context, len(analyzed))
        return context

    async def _analyze_single_business(self, scraper, business: Dict) -> Dict:
        """Analyze a single business website."""
        base_url = business["website"]
        if not base_url.startswith("http"):
            base_url = f"https://{base_url}"

        # Scrape main pages
        urls_to_scrape = [base_url]
        for page in self.PAGES_TO_CHECK[1:]:
            urls_to_scrape.append(f"{base_url.rstrip('/')}/{page}")

        scrape_results = await scraper.scrape_multiple(
            urls=urls_to_scrape[:4],  # Limit to avoid overload
            extract_links=False,
            concurrency=2,
        )

        main_page = scrape_results[0] if scrape_results else {}

        if not main_page.get("success"):
            business["_website_analyzed"] = False
            business["_website_error"] = main_page.get("error", "Unknown error")
            return business

        # AI-powered analysis
        analysis = await self._ai_website_analysis(main_page, scrape_results)

        # Merge analysis into business
        business.update({
            "_website_analyzed": True,
            "website_quality_score": analysis.get("quality_score"),
            "mobile_responsive": analysis.get("mobile_responsive"),
            "page_speed_score": analysis.get("page_speed_score"),
            "seo_score": analysis.get("seo_score"),
            "detected_technologies": main_page.get("technologies", []),
            "missing_features": analysis.get("missing_features", []),
            "website_issues": analysis.get("issues", []),
            "has_booking_system": analysis.get("has_booking_system"),
            "has_online_ordering": analysis.get("has_online_ordering"),
            "has_crm": analysis.get("has_crm"),
            "has_chatbot": analysis.get("has_chatbot"),
            "has_mobile_app": analysis.get("has_mobile_app"),
            "has_analytics": analysis.get("has_analytics"),
            "has_customer_portal": analysis.get("has_customer_portal"),
            "_website_analysis": analysis,
        })

        return business

    async def _ai_website_analysis(self, main_page: Dict, all_pages: List[Dict]) -> Dict:
        """Use AI to analyze website quality and identify opportunities."""

        system_prompt = """You are a senior web development consultant analyzing business websites.
        Analyze the provided website data and return a JSON object with specific fields.
        Be objective and thorough."""

        # Build analysis content
        content_summary = main_page.get("text_content", "")[:8000]
        headings = json.dumps(main_page.get("headings", {}))
        techs = json.dumps(main_page.get("technologies", []))

        user_prompt = f"""Analyze this business website:

        URL: {main_page.get('url')}
        Title: {main_page.get('title')}
        Meta Description: {main_page.get('meta_description')}

        Headings: {headings}

        Technologies Detected: {techs}

        Content Sample:
        {content_summary}

        Return a JSON object with these exact fields:
        {{
            "quality_score": <float 0-100>,
            "mobile_responsive": <boolean>,
            "page_speed_score": <float 0-100>,
            "seo_score": <float 0-100>,
            "has_booking_system": <boolean>,
            "has_online_ordering": <boolean>,
            "has_crm": <boolean>,
            "has_chatbot": <boolean>,
            "has_mobile_app": <boolean>,
            "has_analytics": <boolean>,
            "has_customer_portal": <boolean>,
            "missing_features": [<list of missing features that would benefit the business>],
            "issues": [<list of specific website issues found>],
            "opportunities": [<list of improvement opportunities>],
            "business_type": <inferred business type>,
            "design_quality": <"poor"|"fair"|"good"|"excellent">,
            "content_quality": <"poor"|"fair"|"good"|"excellent">
        }}"""

        try:
            response = await self._ai_chat(system_prompt, user_prompt, json_mode=True, temperature=0.3)
            return json.loads(response)
        except Exception as e:
            self.logger.warning(f"AI website analysis failed: {e}")
            return {
                "quality_score": 50.0,
                "mobile_responsive": None,
                "page_speed_score": None,
                "seo_score": None,
                "missing_features": [],
                "issues": [],
                "opportunities": [],
            }
