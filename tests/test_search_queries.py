from app.services.search_queries import build_interview_queries


def test_build_interview_queries() -> None:
    queries = build_interview_queries(
        company="Salesforce",
        role="Software Engineer Intern",
    )

    assert len(queries) == 3

    assert queries[0].purpose == "interview_experience"
    assert queries[0].query == (
        '"Salesforce" "Software Engineer Intern" '
        "interview experience"
    )

    assert queries[1].purpose == "interview_questions"

    assert queries[2].purpose == "technical_interview"


def test_build_interview_queries_strips_input() -> None:
    queries = build_interview_queries(
        company="  Salesforce  ",
        role="  Software Engineer Intern  ",
    )

    assert queries[0].query.startswith(
        '"Salesforce" "Software Engineer Intern"'
    )
