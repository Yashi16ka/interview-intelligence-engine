from app.services.link_extractor import (
    is_same_domain,
    normalize_link,
)


def test_normalize_relative_link() -> None:
    result = normalize_link(
        "https://example.com/careers/",
        "/jobs/software-engineer",
    )

    assert result == (
        "https://example.com/jobs/software-engineer"
    )


def test_normalize_absolute_link() -> None:
    result = normalize_link(
        "https://example.com",
        "https://engineering.example.com/blog",
    )

    assert result == "https://engineering.example.com/blog"


def test_normalize_link_rejects_non_web_links() -> None:
    assert normalize_link(
        "https://example.com",
        "mailto:jobs@example.com",
    ) is None

    assert normalize_link(
        "https://example.com",
        "#about",
    ) is None


def test_is_same_domain_ignores_www() -> None:
    assert is_same_domain(
        "https://www.example.com/careers",
        "https://example.com/jobs",
    )


def test_is_same_domain_rejects_different_domain() -> None:
    assert not is_same_domain(
        "https://example.com",
        "https://other.com",
    )
