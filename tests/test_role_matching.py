from app.services.role_matching import (
    extract_role_terms,
    matches_role,
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
