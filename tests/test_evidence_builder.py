from app.models.browser import BrowserFetchResult
from app.models.discovery import DiscoveredSource
from app.models.source import SourceResult
from app.services.evidence_builder import build_evidence_items


def test_build_evidence_items_preserves_purpose() -> None:
    discovered = [
        DiscoveredSource(
            title="Software Engineer Job",
            url="https://example.com/job",
            purpose="role_requirements",
            provider="company_careers",
        )
    ]

    fetched = [
        BrowserFetchResult(
            requested_url="https://example.com/job",
            result=SourceResult(
                source="browser",
                title="Software Engineer",
                url="https://example.com/job",
                content="Python experience required.",
            ),
        )
    ]

    evidence = build_evidence_items(
        discovered=discovered,
        fetched=fetched,
    )

    assert len(evidence) == 1
    assert evidence[0].purpose == "role_requirements"
    assert evidence[0].provider == "company_careers"


def test_build_evidence_items_uses_requested_url_after_redirect() -> None:
    discovered = [
        DiscoveredSource(
            title="Interview Experience",
            url="https://example.com/interview",
            purpose="interview_experience",
            provider="discussion",
        )
    ]

    fetched = [
        BrowserFetchResult(
            requested_url="https://example.com/interview",
            result=SourceResult(
                source="browser",
                title="Interview Experience",
                url="https://careers.example.com/interview",
                content="Technical interview experience.",
            ),
        )
    ]

    evidence = build_evidence_items(
        discovered=discovered,
        fetched=fetched,
    )

    assert len(evidence) == 1
    assert evidence[0].purpose == "interview_experience"
    assert str(evidence[0].result.url) == (
        "https://careers.example.com/interview"
    )
