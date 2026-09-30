from app.services.ats_detector import detect_ats_candidate


def test_detects_lever_board() -> None:
    candidate = detect_ats_candidate(
        "https://jobs.lever.co/integrate"
    )

    assert candidate is not None
    assert candidate.provider == "lever"
    assert candidate.slug == "integrate"
    assert str(candidate.board_url) == (
        "https://jobs.lever.co/integrate"
    )


def test_detects_lever_job_url_as_board() -> None:
    candidate = detect_ats_candidate(
        "https://jobs.lever.co/integrate/"
        "aa55db97-371d-4378-bc88-0c058539190b"
    )

    assert candidate is not None
    assert candidate.provider == "lever"
    assert candidate.slug == "integrate"
    assert str(candidate.board_url) == (
        "https://jobs.lever.co/integrate"
    )


def test_rejects_unrecognized_url() -> None:
    candidate = detect_ats_candidate(
        "https://example.com/careers"
    )

    assert candidate is None
