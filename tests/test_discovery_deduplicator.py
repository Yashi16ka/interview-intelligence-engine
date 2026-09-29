from app.models.discovery import DiscoveredSource
from app.services.discovery_deduplicator import (
    deduplicate_discovered_sources,
)


def test_deduplicates_same_url_across_providers() -> None:
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
    assert result[0].provider == "provider_a"


def test_deduplicates_tracking_variants() -> None:
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
            purpose="interview_experience",
            provider="provider_b",
        ),
    ]

    result = deduplicate_discovered_sources(sources)

    assert len(result) == 1


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
