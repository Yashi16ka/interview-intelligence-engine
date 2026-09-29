from app.models.source import SourceResult
from app.services.relevance import (
    rank_sources,
    score_source,
)


def make_result(
    title: str,
    content: str,
    url: str,
) -> SourceResult:
    return SourceResult(
        source="test",
        title=title,
        url=url,
        content=content,
    )


def test_score_source_rewards_company_and_interview_terms() -> None:
    result = make_result(
        title="Salesforce Software Engineer Interview",
        content=(
            "The technical interview included "
            "a coding challenge."
        ),
        url="https://example.com/relevant",
    )

    scored = score_source(
        result,
        company="Salesforce",
        role="Software Engineer Intern",
    )

    assert scored.score > 0
    assert "salesforce" in scored.matched_terms
    assert "software" in scored.matched_terms
    assert "engineer" in scored.matched_terms
    assert "interview" in scored.matched_terms


def test_irrelevant_source_scores_zero() -> None:
    result = make_result(
        title="How to convert JSON to an object",
        content="Java JSON serialization question.",
        url="https://example.com/irrelevant",
    )

    scored = score_source(
        result,
        company="Salesforce",
        role="Software Engineer Intern",
    )

    assert scored.score == 0
    assert scored.matched_terms == []


def test_rank_sources_filters_low_scores() -> None:
    relevant = make_result(
        title="Salesforce SWE Interview Experience",
        content=(
            "Software engineer technical interview "
            "with a coding challenge."
        ),
        url="https://example.com/relevant",
    )

    irrelevant = make_result(
        title="Python word frequency",
        content="Count words in a Python string.",
        url="https://example.com/irrelevant",
    )

    ranked = rank_sources(
        results=[
            irrelevant,
            relevant,
        ],
        company="Salesforce",
        role="Software Engineer Intern",
    )

    assert len(ranked) == 1
    assert ranked[0].result.url == relevant.url


def test_rank_sources_orders_highest_score_first() -> None:
    stronger = make_result(
        title="Salesforce Software Engineer Interview",
        content=(
            "Salesforce technical interview "
            "and coding challenge."
        ),
        url="https://example.com/strong",
    )

    weaker = make_result(
        title="Salesforce Engineering",
        content="Software engineer discussion.",
        url="https://example.com/weak",
    )

    ranked = rank_sources(
        results=[
            weaker,
            stronger,
        ],
        company="Salesforce",
        role="Software Engineer Intern",
    )

    assert len(ranked) == 2
    assert ranked[0].result.url == stronger.url
    assert ranked[0].score > ranked[1].score
