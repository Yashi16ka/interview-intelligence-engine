from app.models.browser import BrowserFetchResult
from app.models.source import SourceResult


def test_browser_fetch_result_preserves_requested_url() -> None:
    result = SourceResult(
        source="browser",
        title="Example",
        url="https://example.com/final",
        content="Example content.",
    )

    fetched = BrowserFetchResult(
        requested_url="https://example.com/original",
        result=result,
    )

    assert str(fetched.requested_url) == "https://example.com/original"
    assert str(fetched.result.url) == "https://example.com/final"
