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
        title="Salesforce Software Engineer Interview",
        content=(
            "Salesforce Software Engineer interview "
            "experience."
        ),
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


def test_rewards_company_and_interview_in_same_context() -> None:
    result = SourceResult(
        source="discussion",
        title="Interview experience",
        url="https://example.com/strong",
        content=(
            "My Microsoft Software Engineer interview "
            "included a technical interview and coding challenge."
        ),
    )

    scored = score_source(
        result=result,
        company="Microsoft",
        role="Software Engineer",
    )

    assert "company_interview_context" in scored.matched_terms
    assert scored.score >= 8


def test_does_not_reward_disconnected_company_and_interview_mentions() -> None:
    filler = "unrelated engineering discussion " * 20

    result = SourceResult(
        source="discussion",
        title="General hiring discussion",
        url="https://example.com/weak",
        content=(
            "We work with Microsoft on security research. "
            f"{filler}"
            "Software engineers often prepare for interviews."
        ),
    )

    scored = score_source(
        result=result,
        company="Microsoft",
        role="Software Engineer",
    )

    assert "company_interview_context" not in scored.matched_terms


def test_strong_interview_terms_receive_extra_weight() -> None:
    generic = SourceResult(
        source="discussion",
        title="Microsoft hiring",
        url="https://example.com/generic",
        content=(
            "Microsoft Software Engineer interview."
        ),
    )

    specific = SourceResult(
        source="discussion",
        title="Microsoft hiring",
        url="https://example.com/specific",
        content=(
            "Microsoft Software Engineer interview "
            "included a coding challenge."
        ),
    )

    generic_score = score_source(
        result=generic,
        company="Microsoft",
        role="Software Engineer",
    ).score

    specific_score = score_source(
        result=specific,
        company="Microsoft",
        role="Software Engineer",
    ).score

    assert specific_score > generic_score


def test_rank_sources_rejects_disconnected_keyword_matches() -> None:
    filler = "unrelated hiring discussion " * 30

    false_positive = SourceResult(
        source="discussion",
        title="General technology hiring",
        url="https://example.com/false-positive",
        content=(
            "Microsoft provides technology services. "
            f"{filler}"
            "Software engineer interviews may include "
            "technical interviews and assessments."
        ),
    )

    ranked = rank_sources(
        results=[false_positive],
        company="Microsoft",
        role="Software Engineer Intern",
    )

    assert ranked == []


def test_does_not_create_company_context_from_ordinary_word_usage() -> None:
    result = SourceResult(
        source="discussion",
        title="Tech Interview Experience",
        url="https://example.com/tech-interview-experience",
        content=(
            "This site collects interview experiences from candidates. "
            "Job portals could integrate this into their site to help "
            "people prepare for interviews."
        ),
    )

    scored = score_source(
        result=result,
        company="Integrate",
        role="Software Engineer",
    )

    assert "company_interview_context" not in scored.matched_terms


def test_keeps_company_context_for_ambiguous_name_used_as_entity() -> None:
    result = SourceResult(
        source="discussion",
        title="Software engineering interview experience",
        url="https://example.com/integrate-interview",
        content=(
            "I interviewed at Integrate for a Software Engineer role. "
            "My interview included a coding round and technical questions."
        ),
    )

    scored = score_source(
        result=result,
        company="Integrate",
        role="Software Engineer",
    )

    assert "company_interview_context" in scored.matched_terms
