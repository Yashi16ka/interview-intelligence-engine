from app.services.research_cache import (
    build_research_cache_key,
    normalize_cache_component,
)


def test_normalizes_cache_component() -> None:
    assert (
        normalize_cache_component(
            "  Software   Engineer  "
        )
        == "software engineer"
    )


def test_cache_key_is_stable_across_formatting() -> None:
    first = build_research_cache_key(
        company=" OpenAI ",
        role="Software   Engineer",
    )

    second = build_research_cache_key(
        company="openai",
        role=" software engineer ",
    )

    assert first == second


def test_different_roles_have_different_keys() -> None:
    software_engineer = build_research_cache_key(
        company="Example",
        role="Software Engineer",
    )

    product_manager = build_research_cache_key(
        company="Example",
        role="Product Manager",
    )

    assert software_engineer != product_manager
