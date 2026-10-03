import asyncio

from playwright.async_api import async_playwright

from app.models.browser import BrowserFetchResult
from app.models.source import SourceResult
from app.services.collectors.base import BaseCollector


def is_blocked_or_error_page(
    title: str,
    content: str,
) -> bool:
    title_text = title.casefold().strip()
    content_text = content.casefold()

    human_verification_titles = (
        "just a moment",
        "verify you are human",
    )
    human_verification_content = (
        "verify you are human",
        "checking your browser",
        "performing security verification",
    )

    if (
        any(
            marker in title_text
            for marker in human_verification_titles
        )
        and any(
            marker in content_text
            for marker in human_verification_content
        )
    ):
        return True

    access_denied_titles = (
        "access denied",
        "forbidden",
    )
    access_denied_content = (
        "access denied",
        "don't have permission",
        "do not have permission",
        "403 forbidden",
    )

    if (
        any(
            marker in title_text
            for marker in access_denied_titles
        )
        and any(
            marker in content_text
            for marker in access_denied_content
        )
    ):
        return True

    return False


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
            response = await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=self.timeout_ms,
            )

            if (
                response is not None
                and response.status >= 400
            ):
                return None

            title = await page.title()
            content = await page.locator("body").inner_text()

            if not title or not content.strip():
                return None

            if is_blocked_or_error_page(
                title=title,
                content=content,
            ):
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
