from app.models.evidence import EvidenceItem
from app.models.source import SourceResult
from app.services.purpose_relevance import ScoredEvidence
from app.services.synthesis_prompt import build_synthesis_prompt


def make_scored_evidence(
    *,
    title: str,
    url: str,
    content: str,
    purpose: str,
    score: int,
) -> ScoredEvidence:
    return ScoredEvidence(
        evidence=EvidenceItem(
            result=SourceResult(
                source="browser",
                title=title,
                url=url,
                content=content,
            ),
            purpose=purpose,
            provider="test",
        ),
        score=score,
        matched_terms=["interview"],
    )


def test_prompt_numbers_and_preserves_evidence() -> None:
    evidence = [
        make_scored_evidence(
            title="Interview experience",
            url="https://example.com/one",
            content="System design was part of the interview.",
            purpose="interview_experience",
            score=15,
        ),
        make_scored_evidence(
            title="Job requirements",
            url="https://example.com/two",
            content="Candidates should know Python and APIs.",
            purpose="role_requirements",
            score=10,
        ),
    ]

    prompt = build_synthesis_prompt(
        company="Example",
        role="Software Engineer",
        evidence=evidence,
    )

    assert "Company: Example" in prompt
    assert "Role: Software Engineer" in prompt
    assert "[E1]" in prompt
    assert "[E2]" in prompt
    assert "Interview experience" in prompt
    assert "https://example.com/one" in prompt
    assert "System design was part of the interview." in prompt
    assert "role_requirements" in prompt


def test_prompt_truncates_long_evidence_content() -> None:
    evidence = [
        make_scored_evidence(
            title="Long source",
            url="https://example.com/long",
            content="x" * 6000,
            purpose="interview_experience",
            score=12,
        ),
    ]

    prompt = build_synthesis_prompt(
        company="Example",
        role="Software Engineer",
        evidence=evidence,
        max_content_chars=1000,
    )

    assert "x" * 1000 in prompt
    assert "x" * 1001 not in prompt
