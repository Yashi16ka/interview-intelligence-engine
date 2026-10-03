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


class FakeLocator:
    def __init__(self, content: str) -> None:
        self.content = content

    async def inner_text(self) -> str:
        return self.content


class FakeResponse:
    def __init__(self, status: int) -> None:
        self.status = status


class FakePage:
    def __init__(
        self,
        title: str,
        content: str,
        final_url: str = "https://example.com/final",
        status: int = 200,
    ) -> None:
        self._title = title
        self._content = content
        self._status = status
        self.url = final_url

    async def goto(
        self,
        url: str,
        wait_until: str,
        timeout: int,
    ) -> FakeResponse:
        del url, wait_until, timeout
        return FakeResponse(self._status)

    async def title(self) -> str:
        return self._title

    def locator(self, selector: str) -> FakeLocator:
        assert selector == "body"
        return FakeLocator(self._content)

@pytest.mark.anyio
async def test_browser_collector_keeps_normal_page() -> None:
    collector = BrowserPageCollector(
        urls=["https://example.com/interview"]
    )
    page = FakePage(
        title="Software Engineer Interview Experience",
        content=(
            "I interviewed for a software engineering role. "
            "The technical interview included a coding challenge."
        ),
    )

    fetched = await collector._collect_page(
        page,
        "https://example.com/interview",
    )

    assert fetched is not None
    assert fetched.result.title == (
        "Software Engineer Interview Experience"
    )

@pytest.mark.anyio
async def test_browser_collector_rejects_human_verification_page() -> None:
    collector = BrowserPageCollector(
        urls=["https://example.com/interview"]
    )
    page = FakePage(
        title="Just a moment...",
        content=(
            "Verify you are human by completing the action below. "
            "This verification may take a few seconds."
        ),
    )

    fetched = await collector._collect_page(
        page,
        "https://example.com/interview",
    )

    assert fetched is None

@pytest.mark.anyio
async def test_browser_collector_rejects_access_denied_page() -> None:
    collector = BrowserPageCollector(
        urls=["https://example.com/interview"]
    )
    page = FakePage(
        title="Access Denied",
        content=(
            "Access denied. You don't have permission "
            "to access this resource."
        ),
    )

    fetched = await collector._collect_page(
        page,
        "https://example.com/interview",
    )

    assert fetched is None

@pytest.mark.anyio
async def test_browser_collector_rejects_http_error_response() -> None:
    collector = BrowserPageCollector(
        urls=["https://example.com/interview"]
    )
    page = FakePage(
        title="Service Unavailable",
        content=(
            "The requested service is temporarily unavailable. "
            "Please try again later."
        ),
        status=503,
    )

    fetched = await collector._collect_page(
        page,
        "https://example.com/interview",
    )

    assert fetched is None
