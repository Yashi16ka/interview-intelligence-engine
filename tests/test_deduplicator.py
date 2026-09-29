from app.models.source import SourceResult
from app.services.deduplicator import (
    canonicalize_url,
    deduplicate_sources,
    title_key,
)


def make_result(
    source: str,
    title: str,
    url: str,
) -> SourceResult:
    return SourceResult(
        source=source,
        title=title,
        url=url,
        content=f"Content for {title}",
    )


def test_canonicalize_url_removes_tracking_parameters() -> None:
    url = (
        "https://Example.com/article/"
        "?utm_source=reddit&utm_campaign=test&id=123"
        "#comments"
    )

    assert canonicalize_url(url) == (
        "https://example.com/article?id=123"
    )


def test_title_key_normalizes_title() -> None:
    assert title_key(
        "Salesforce SWE Interview: Tips!"
    ) == "salesforce swe interview tips"


def test_deduplicate_sources_by_url() -> None:
    results = [
        make_result(
            "reddit",
            "Salesforce Interview",
            "https://example.com/interview?utm_source=reddit",
        ),
        make_result(
            "hackernews",
            "Different title",
            "https://example.com/interview",
        ),
    ]

    deduplicated = deduplicate_sources(results)

    assert len(deduplicated) == 1
    assert deduplicated[0].source == "reddit"


def test_deduplicate_sources_by_title() -> None:
    results = [
        make_result(
            "reddit",
            "Salesforce SWE Interview Tips",
            "https://example.com/reddit",
        ),
        make_result(
            "hackernews",
            "Salesforce SWE Interview Tips!",
            "https://example.com/hn",
        ),
    ]

    deduplicated = deduplicate_sources(results)

    assert len(deduplicated) == 1


def test_deduplicate_sources_preserves_unique_results() -> None:
    results = [
        make_result(
            "reddit",
            "Salesforce Interview Experience",
            "https://example.com/one",
        ),
        make_result(
            "hackernews",
            "Salesforce Engineering Culture",
            "https://example.com/two",
        ),
    ]

    deduplicated = deduplicate_sources(results)

    assert len(deduplicated) == 2
