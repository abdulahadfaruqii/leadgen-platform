"""
Advanced web scraper using Playwright with stealth, proxy rotation, and retry logic.
"""
import asyncio
import random
from contextlib import asynccontextmanager
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from bs4 import BeautifulSoup

from app.core.config import get_settings
from app.core.exceptions import ScrapingException
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class WebScraper:
    """Production-grade web scraper with anti-detection measures."""

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    ]

    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self._lock = asyncio.Lock()

    async def _ensure_browser(self):
        if self.browser is None or not self.browser.is_connected():
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=settings.PLAYWRIGHT_HEADLESS,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-web-security",
                    "--disable-features=IsolateOrigins,site-per-process",
                ],
            )

    def _get_proxy(self) -> Optional[Dict]:
        if not settings.PROXY_ROTATION_ENABLED or not settings.PROXIES:
            return None
        proxy_url = random.choice(settings.PROXIES)
        parsed = urlparse(proxy_url)
        return {
            "server": f"{parsed.scheme}://{parsed.hostname}:{parsed.port}",
            "username": parsed.username,
            "password": parsed.password,
        }

    @asynccontextmanager
    async def _new_context(self):
        await self._ensure_browser()
        proxy = self._get_proxy()

        context = await self.browser.new_context(
            user_agent=random.choice(self.USER_AGENTS),
            viewport={"width": 1920, "height": 1080},
            proxy=proxy,
            java_script_enabled=True,
            bypass_csp=True,
        )

        # Inject stealth scripts
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            window.chrome = { runtime: {} };
        """)

        try:
            yield context
        finally:
            await context.close()

    async def scrape_page(
        self,
        url: str,
        wait_for: Optional[str] = None,
        timeout: int = 30000,
        extract_links: bool = False,
        screenshot: bool = False,
    ) -> Dict:
        """Scrape a single page with full content extraction."""

        for attempt in range(settings.MAX_RETRIES):
            try:
                async with self._new_context() as context:
                    page = await context.new_page()

                    response = await page.goto(
                        url,
                        wait_until="networkidle",
                        timeout=timeout,
                    )

                    if wait_for:
                        await page.wait_for_selector(wait_for, timeout=10000)

                    # Wait for dynamic content
                    await page.wait_for_timeout(2000)

                    content = await page.content()
                    soup = BeautifulSoup(content, "lxml")

                    result = {
                        "url": url,
                        "status_code": response.status if response else 0,
                        "title": await page.title(),
                        "meta_description": self._extract_meta(soup, "description"),
                        "headings": self._extract_headings(soup),
                        "text_content": self._extract_text(soup),
                        "links": [],
                        "emails": [],
                        "phones": [],
                        "technologies": [],
                        "screenshot": None,
                        "success": True,
                    }

                    if extract_links:
                        result["links"] = await self._extract_all_links(page, url)

                    if screenshot:
                        result["screenshot"] = await page.screenshot(full_page=True, type="jpeg", quality=80)

                    # Extract contact info from text
                    result["emails"] = self._extract_emails(result["text_content"])
                    result["phones"] = self._extract_phones(result["text_content"])

                    # Detect technologies
                    result["technologies"] = self._detect_technologies(content, await page.evaluate("() => window.location.href"))

                    logger.info("Page scraped successfully", url=url, status=result["status_code"])
                    return result

            except Exception as e:
                logger.warning(f"Scrape attempt {attempt + 1} failed", url=url, error=str(e))
                if attempt < settings.MAX_RETRIES - 1:
                    await asyncio.sleep(2 ** attempt + random.uniform(0, 1))
                else:
                    raise ScrapingException(f"Failed to scrape {url} after {settings.MAX_RETRIES} attempts: {str(e)}")

        return {"url": url, "success": False, "error": "Max retries exceeded"}

    async def scrape_multiple(
        self,
        urls: List[str],
        concurrency: int = 3,
        **kwargs
    ) -> List[Dict]:
        """Scrape multiple pages with controlled concurrency."""
        semaphore = asyncio.Semaphore(concurrency)

        async def _scrape_with_limit(url: str) -> Dict:
            async with semaphore:
                await asyncio.sleep(settings.SCRAPING_DELAY_MS / 1000)
                try:
                    return await self.scrape_page(url, **kwargs)
                except Exception as e:
                    return {"url": url, "success": False, "error": str(e)}

        tasks = [_scrape_with_limit(url) for url in urls]
        return await asyncio.gather(*tasks)

    def _extract_meta(self, soup: BeautifulSoup, name: str) -> Optional[str]:
        tag = soup.find("meta", attrs={"name": name}) or soup.find("meta", attrs={"property": f"og:{name}"})
        return tag.get("content") if tag else None

    def _extract_headings(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        return {
            f"h{i}": [h.get_text(strip=True) for h in soup.find_all(f"h{i}")]
            for i in range(1, 7)
        }

    def _extract_text(self, soup: BeautifulSoup) -> str:
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()
        return soup.get_text(separator="\n", strip=True)

    async def _extract_all_links(self, page: Page, base_url: str) -> List[Dict]:
        links = await page.eval_on_selector_all("a[href]", """
            elements => elements.map(el => ({
                href: el.href,
                text: el.innerText.trim(),
                title: el.title,
            }))
        """)

        # Normalize and filter
        result = []
        seen = set()
        for link in links:
            href = link.get("href", "")
            if href.startswith("http"):
                normalized = href.split("#")[0].rstrip("/")
                if normalized not in seen:
                    seen.add(normalized)
                    result.append(link)
        return result

    def _extract_emails(self, text: str) -> List[str]:
        import re
        pattern = r\'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\'
        return list(set(re.findall(pattern, text)))

    def _extract_phones(self, text: str) -> List[str]:
        import re
        pattern = r\'(?:(?:\+?1\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})\'
        matches = re.findall(pattern, text)
        return ["".join(m) for m in matches if any(m)]

    def _detect_technologies(self, html: str, url: str) -> List[str]:
        techs = []
        indicators = {
            "WordPress": ["wp-content", "wp-includes", "wordpress"],
            "Shopify": ["myshopify.com", "cdn.shopify.com"],
            "React": ["reactroot", "data-reactroot", "__REACT__"],
            "Next.js": ["__NEXT_DATA__"],
            "Vue.js": ["__VUE__", "vue-router"],
            "Angular": ["ng-app", "angular"],
            "Wix": ["wix.com", "static.wixstatic.com"],
            "Squarespace": ["squarespace.com", "static1.squarespace.com"],
            "Webflow": ["webflow.com", "data-wf-page"],
            "Google Analytics": ["gtag", "google-analytics.com/analytics.js", "GA_MEASUREMENT_ID"],
            "Facebook Pixel": ["fbq("],
            "Hotjar": ["hotjar.com"],
            "Stripe": ["stripe.com", "stripe.js"],
            "PayPal": ["paypal.com", "paypalobjects.com"],
        }
        html_lower = html.lower()
        for tech, patterns in indicators.items():
            if any(p.lower() in html_lower for p in patterns):
                techs.append(tech)
        return techs

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


# Singleton
_scraper: Optional[WebScraper] = None


def get_scraper() -> WebScraper:
    global _scraper
    if _scraper is None:
        _scraper = WebScraper()
    return _scraper
