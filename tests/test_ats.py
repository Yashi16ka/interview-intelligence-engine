from app.models.ats import ATSCandidate


def test_ats_candidate_preserves_provider_and_slug() -> None:
    candidate = ATSCandidate(
        provider="lever",
        board_url="https://jobs.lever.co/example",
        slug="example",
    )

    assert candidate.provider == "lever"
    assert candidate.slug == "example"


def test_ats_candidate_supports_different_providers() -> None:
    candidate = ATSCandidate(
        provider="greenhouse",
        board_url="https://boards.greenhouse.io/example",
        slug="example",
    )

    assert candidate.provider == "greenhouse"
