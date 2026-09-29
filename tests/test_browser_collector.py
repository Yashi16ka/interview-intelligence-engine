import pytest

from app.services.collectors.browser import BrowserPageCollector


@pytest.mark.anyio
async def test_browser_collector_with_empty_urls() -> None:
    collector = BrowserPageCollector(urls=[])

    results = await collector.collect(
        company="Salesforce",
        role="Software Engineer Intern",
    )

    assert results == []


def test_browser_collector_name() -> None:
    collector = BrowserPageCollector(urls=[])

    assert collector.name == "browser"
