from app.models.discovery import DiscoveredSource
from app.services.discovery_deduplicator import (
    deduplicate_discovered_sources,
)


def test_merges_purposes_for_same_url() -> None:
    sources = [
        DiscoveredSource(
            title="First result",
            url="https://example.com/interview",
            purpose="interview_experience",
            provider="provider_a",
        ),
        DiscoveredSource(
            title="Second result",
            url="https://example.com/interview",
            purpose="interview_questions",
            provider="provider_b",
        ),
    ]

    result = deduplicate_discovered_sources(sources)

    assert len(result) == 1
    assert result[0].purposes == [
        "interview_experience",
        "interview_questions",
    ]
    assert result[0].providers == [
        "provider_a",
        "provider_b",
    ]


def test_merges_tracking_variants() -> None:
    sources = [
        DiscoveredSource(
            title="Original",
            url="https://example.com/interview",
            purpose="interview_experience",
            provider="provider_a",
        ),
        DiscoveredSource(
            title="Tracked",
            url=(
                "https://example.com/interview"
                "?utm_source=search"
            ),
            purpose="technical_interview",
            provider="provider_b",
        ),
    ]

    result = deduplicate_discovered_sources(sources)

    assert len(result) == 1
    assert result[0].purposes == [
        "interview_experience",
        "technical_interview",
    ]
    assert result[0].providers == [
        "provider_a",
        "provider_b",
    ]


def test_does_not_duplicate_same_purpose_or_provider() -> None:
    sources = [
        DiscoveredSource(
            title="First",
            url="https://example.com/interview",
            purpose="interview_experience",
            provider="provider_a",
        ),
        DiscoveredSource(
            title="Second",
            url="https://example.com/interview",
            purpose="interview_experience",
            provider="provider_a",
        ),
    ]

    result = deduplicate_discovered_sources(sources)

    assert len(result) == 1
    assert result[0].purposes == [
        "interview_experience",
    ]
    assert result[0].providers == [
        "provider_a",
    ]


def test_preserves_unique_sources() -> None:
    sources = [
        DiscoveredSource(
            title="Interview experience",
            url="https://example.com/interview",
            purpose="interview_experience",
            provider="provider_a",
        ),
        DiscoveredSource(
            title="Job posting",
            url="https://example.com/jobs/123",
            purpose="role_requirements",
            provider="provider_b",
        ),
    ]

    result = deduplicate_discovered_sources(sources)

    assert len(result) == 2
    assert result[0].purposes == [
        "interview_experience",
    ]
    assert result[1].purposes == [
        "role_requirements",
    ]
