from app.models.source import SourceResult
from app.services.normalizer import (
    normalize_source,
    normalize_sources,
    normalize_text,
)


def test_normalize_text_removes_html() -> None:
    text = "<p>Python &amp; FastAPI</p>"

    assert normalize_text(text) == "Python & FastAPI"


def test_normalize_text_collapses_whitespace() -> None:
    text = "Python\n\n   FastAPI\tPostgreSQL"

    assert normalize_text(text) == "Python FastAPI PostgreSQL"


def test_normalize_source() -> None:
    result = SourceResult(
        source="HackerNews ",
        title="  Salesforce &amp; Engineering  ",
        url="https://example.com/article",
        content="<p>Python   API development</p>",
    )

    normalized = normalize_source(result)

    assert normalized.source == "hackernews"
    assert normalized.title == "Salesforce & Engineering"
    assert normalized.content == "Python API development"


def test_normalize_sources() -> None:
    results = [
        SourceResult(
            source="HackerNews",
            title="<b>First result</b>",
            url="https://example.com/1",
            content="Python   APIs",
        ),
        SourceResult(
            source="StackOverflow",
            title="Second &amp; result",
            url="https://example.com/2",
            content="<p>System design</p>",
        ),
    ]

    normalized = normalize_sources(results)

    assert len(normalized) == 2
    assert normalized[0].title == "First result"
    assert normalized[0].content == "Python APIs"
    assert normalized[1].source == "stackoverflow"
    assert normalized[1].title == "Second & result"
    assert normalized[1].content == "System design"
