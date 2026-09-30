from app.services.ats_slugs import build_company_slugs


def test_builds_common_company_slug_variants() -> None:
    slugs = build_company_slugs("Acme AI")

    assert "acmeai" in slugs
    assert "acme-ai" in slugs
    assert "acme" in slugs


def test_normalizes_punctuation_and_whitespace() -> None:
    slugs = build_company_slugs("  Example, Inc.  ")

    assert "exampleinc" in slugs
    assert "example-inc" in slugs
    assert "example" in slugs


def test_does_not_return_duplicate_slugs() -> None:
    slugs = build_company_slugs("Example")

    assert slugs == ["example"]
