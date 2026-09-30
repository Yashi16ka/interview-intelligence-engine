import asyncio

from playwright.async_api import async_playwright

from app.models.browser import BrowserFetchResult
from app.models.source import SourceResult
from app.services.collectors.base import BaseCollector


class BrowserPageCollector(BaseCollector):
    def __init__(
        self,
        urls: list[str],
        timeout_ms: int = 10_000,
    ) -> None:
        self.urls = urls
        self.timeout_ms = timeout_ms

    @property
    def name(self) -> str:
        return "browser"

    async def _collect_page(
        self,
        page,
        url: str,
    ) -> BrowserFetchResult | None:
        try:
            await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=self.timeout_ms,
            )

            title = await page.title()
            content = await page.locator("body").inner_text()

            if not title or not content.strip():
                return None

            result = SourceResult(
                source=self.name,
                title=title.strip(),
                url=page.url,
                content=content.strip(),
            )

            return BrowserFetchResult(
                requested_url=url,
                result=result,
            )

        except Exception:
            return None

    async def collect_with_metadata(
        self,
    ) -> list[BrowserFetchResult]:
        if not self.urls:
            return []

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(
                headless=True,
            )

            try:
                pages = [
                    await browser.new_page()
                    for _ in self.urls
                ]

                tasks = [
                    self._collect_page(page, url)
                    for page, url in zip(
                        pages,
                        self.urls,
                        strict=True,
                    )
                ]

                outcomes = await asyncio.gather(*tasks)

                return [
                    outcome
                    for outcome in outcomes
                    if outcome is not None
                ]

            finally:
                await browser.close()

    async def collect(
        self,
        company: str,
        role: str,
    ) -> list[SourceResult]:
        del company, role

        fetched = await self.collect_with_metadata()

        return [
            item.result
            for item in fetched
        ]
