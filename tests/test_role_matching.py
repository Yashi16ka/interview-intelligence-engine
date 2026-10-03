from app.services.role_matching import (
    extract_role_terms,
    matches_role,
    matches_role_query,
)


def test_extracts_meaningful_role_terms() -> None:
    terms = extract_role_terms(
        '"Acme" "Machine Learning Intern" jobs requirements'
    )

    assert terms == {"machine", "learning"}


def test_matches_software_engineer_title() -> None:
    terms = {"software", "engineer"}

    assert matches_role(
        "Software Engineer, Data Infrastructure",
        terms,
    )
    assert matches_role(
        "Senior Software Engineer",
        terms,
    )


def test_rejects_generic_engineer_title() -> None:
    terms = {"software", "engineer"}

    assert not matches_role(
        "Research Engineer",
        terms,
    )
    assert not matches_role(
        "Data Engineer",
        terms,
    )


def test_matches_machine_learning_role() -> None:
    terms = {"machine", "learning"}

    assert matches_role(
        "Machine Learning Intern",
        terms,
    )
    assert matches_role(
        "Machine Learning Engineer Intern",
        terms,
    )


def test_rejects_unrelated_internship() -> None:
    terms = {"machine", "learning"}

    assert not matches_role(
        "Product Intern",
        terms,
    )


def test_plain_role_rejects_explicit_senior_title() -> None:
    assert matches_role_query(
        title="Full Stack Software Engineer",
        role="Software Engineer",
    )

    assert not matches_role_query(
        title="Senior Full Stack Software Engineer",
        role="Software Engineer",
    )


def test_intern_role_requires_intern_title() -> None:
    assert matches_role_query(
        title="Software Engineer Intern",
        role="Software Engineer Intern",
    )

    assert not matches_role_query(
        title="Senior Software Engineer",
        role="Software Engineer Intern",
    )

    assert not matches_role_query(
        title="Software Engineer",
        role="Software Engineer Intern",
    )


def test_senior_role_requires_senior_title() -> None:
    assert matches_role_query(
        title="Senior Software Engineer",
        role="Senior Software Engineer",
    )

    assert not matches_role_query(
        title="Software Engineer",
        role="Senior Software Engineer",
    )

    assert not matches_role_query(
        title="Software Engineer Intern",
        role="Senior Software Engineer",
    )
