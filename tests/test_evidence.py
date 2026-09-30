from app.models.evidence import EvidenceItem
from app.models.source import SourceResult


def test_evidence_item_preserves_discovery_metadata() -> None:
    result = SourceResult(
        source="browser",
        title="Example Interview",
        url="https://example.com/interview",
        content="Example interview content.",
    )

    evidence = EvidenceItem(
        result=result,
        purpose="interview_experience",
        provider="fake",
    )

    assert evidence.result == result
    assert evidence.purpose == "interview_experience"
    assert evidence.provider == "fake"


def test_evidence_item_supports_non_interview_purpose() -> None:
    result = SourceResult(
        source="browser",
        title="Software Engineer Job",
        url="https://example.com/jobs/software-engineer",
        content="Python and distributed systems experience required.",
    )

    evidence = EvidenceItem(
        result=result,
        purpose="role_requirements",
        provider="company_careers",
    )

    assert evidence.purpose == "role_requirements"
    assert evidence.provider == "company_careers"
