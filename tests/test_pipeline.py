from app.models.source import SourceResult
from app.services.pipeline import process_sources


def make_result(
    source: str,
    title: str,
    url: str,
    content: str,
) -> SourceResult:
    return SourceResult(
        source=source,
        title=title,
        url=url,
        content=content,
    )


def test_pipeline_normalizes_deduplicates_and_ranks() -> None:
    results = [
        make_result(
            source="HackerNews ",
            title="<b>Salesforce Software Engineer Interview</b>",
            url="https://example.com/interview?utm_source=hn",
            content=(
                "<p>Salesforce technical interview "
                "with a coding challenge.</p>"
            ),
        ),
        make_result(
            source="Reddit",
            title="Salesforce Software Engineer Interview!",
            url="https://example.com/interview",
            content="Duplicate interview discussion.",
        ),
        make_result(
            source="StackOverflow",
            title="Convert JSON to Object",
            url="https://example.com/json",
            content="Generic Java serialization question.",
        ),
    ]

    processed = process_sources(
        results=results,
        company="Salesforce",
        role="Software Engineer Intern",
    )

    assert processed.stats.raw_count == 3
    assert processed.stats.normalized_count == 3
    assert processed.stats.unique_count == 2
    assert processed.stats.relevant_count == 1

    assert len(processed.evidence) == 1

    evidence = processed.evidence[0]

    assert evidence.result.source == "hackernews"
    assert evidence.result.title == (
        "Salesforce Software Engineer Interview"
    )
    assert evidence.score > 0


def test_pipeline_preserves_relevance_order() -> None:
    results = [
        make_result(
            source="test",
            title="Salesforce Engineering",
            url="https://example.com/weaker",
            content="Software engineer discussion.",
        ),
        make_result(
            source="test",
            title="Salesforce Software Engineer Interview",
            url="https://example.com/stronger",
            content=(
                "Salesforce technical interview "
                "with coding challenge."
            ),
        ),
    ]

    processed = process_sources(
        results=results,
        company="Salesforce",
        role="Software Engineer Intern",
    )

    assert len(processed.evidence) == 2
    assert str(processed.evidence[0].result.url) == (
        "https://example.com/stronger"
    )
    assert (
        processed.evidence[0].score
        > processed.evidence[1].score
    )


def test_pipeline_respects_minimum_score() -> None:
    results = [
        make_result(
            source="test",
            title="Salesforce Engineering",
            url="https://example.com/result",
            content="Software engineer discussion.",
        )
    ]

    processed = process_sources(
        results=results,
        company="Salesforce",
        role="Software Engineer Intern",
        minimum_score=100,
    )

    assert processed.stats.raw_count == 1
    assert processed.stats.unique_count == 1
    assert processed.stats.relevant_count == 0
    assert processed.evidence == []
