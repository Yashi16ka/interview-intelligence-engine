from app.models.ats import ATSCandidate
from app.services.ats_detector import detect_ats_candidate


def discover_ats_candidates(
    links: list[str],
) -> list[ATSCandidate]:
    candidates: list[ATSCandidate] = []
    seen: set[tuple[str, str]] = set()

    for link in links:
        candidate = detect_ats_candidate(link)

        if candidate is None:
            continue

        key = (
            candidate.provider,
            candidate.slug,
        )

        if key in seen:
            continue

        seen.add(key)
        candidates.append(candidate)

    return candidates

from html.parser import HTMLParser

from app.services.link_extractor import normalize_link


class _LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        if tag != "a":
            return

        for name, value in attrs:
            if name == "href" and value:
                self.hrefs.append(value)


async def discover_ats_from_page(
    page_url: str,
    html: str,
) -> list[ATSCandidate]:
    parser = _LinkParser()
    parser.feed(html)

    links: list[str] = []

    for href in parser.hrefs:
        normalized = normalize_link(
            base_url=page_url,
            href=href,
        )

        if normalized is not None:
            links.append(normalized)

    return discover_ats_candidates(links)

from playwright.async_api import async_playwright


async def discover_ats_from_url(
    page_url: str,
    timeout_ms: int = 10_000,
) -> list[ATSCandidate]:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=True,
        )

        try:
            page = await browser.new_page()

            await page.goto(
                page_url,
                wait_until="domcontentloaded",
                timeout=timeout_ms,
            )

            html = await page.content()

            return await discover_ats_from_page(
                page_url=page.url,
                html=html,
            )
        finally:
            await browser.close()
