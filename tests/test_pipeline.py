from app.models.evidence import EvidenceItem
from app.models.source import SourceResult
from app.services.pipeline import process_evidence, process_sources


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
            title="Salesforce SWE Candidate Experience",
            url="https://example.com/weaker",
            content=(
                "Salesforce Software Engineer interview "
                "experience."
            ),
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


def make_evidence(
    provider: str,
    purpose: str,
    title: str,
    url: str,
    content: str,
) -> EvidenceItem:
    return EvidenceItem(
        result=SourceResult(
            source=provider,
            title=title,
            url=url,
            content=content,
        ),
        purpose=purpose,
        provider=provider,
    )


def test_evidence_pipeline_deduplicates_same_title_and_purpose() -> None:
    evidence = [
        make_evidence(
            provider="lever",
            purpose="role_requirements",
            title="Full Stack Software Engineer",
            url="https://jobs.lever.co/integrate/job-1",
            content=(
                "Integrate is hiring a Full Stack Software Engineer "
                "to build production software systems."
            ),
        ),
        make_evidence(
            provider="ashby",
            purpose="role_requirements",
            title="Full Stack Software Engineer",
            url="https://jobs.ashbyhq.com/integrate/job-2",
            content=(
                "Integrate is hiring a Full Stack Software Engineer "
                "to build production software systems."
            ),
        ),
    ]

    processed = process_evidence(
        evidence=evidence,
        company="Integrate",
        role="Software Engineer",
    )

    assert processed.stats.raw_count == 2
    assert processed.stats.normalized_count == 2
    assert processed.stats.unique_count == 1
    assert processed.stats.relevant_count == 1
    assert len(processed.evidence) == 1


def test_evidence_pipeline_preserves_same_title_for_different_purposes() -> None:
    evidence = [
        make_evidence(
            provider="test",
            purpose="interview_experience",
            title="Microsoft Software Engineer Interview",
            url="https://example.com/interview",
            content=(
                "I interviewed at Microsoft for a Software Engineer role. "
                "The technical interview included a coding challenge."
            ),
        ),
        make_evidence(
            provider="test",
            purpose="interview_questions",
            title="Microsoft Software Engineer Interview",
            url="https://example.com/interview",
            content=(
                "Microsoft candidates reported technical interview "
                "questions about software engineering."
            ),
        ),
    ]

    processed = process_evidence(
        evidence=evidence,
        company="Microsoft",
        role="Software Engineer",
    )

    assert processed.stats.raw_count == 2
    assert processed.stats.normalized_count == 2
    assert processed.stats.unique_count == 2
    assert len(processed.evidence) == 2
