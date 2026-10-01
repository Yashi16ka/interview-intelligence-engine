from app.services.search_queries import build_interview_queries


def test_builds_multiple_research_purposes() -> None:
    queries = build_interview_queries(
        company="Example Corp",
        role="Backend Engineer",
    )

    purposes = {
        query.purpose
        for query in queries
    }

    assert purposes == {
        "interview_experience",
        "interview_questions",
        "technical_interview",
        "role_requirements",
        "company_engineering",
    }


def test_queries_include_company_and_relevant_role() -> None:
    queries = build_interview_queries(
        company="NVIDIA",
        role="Machine Learning Intern",
    )

    interview_queries = [
        query.query
        for query in queries
        if query.purpose != "company_engineering"
    ]

    assert all(
        "NVIDIA" in query
        for query in interview_queries
    )

    assert all(
        "Machine Learning Intern" in query
        for query in interview_queries
    )


def test_does_not_hardcode_software_engineering_role() -> None:
    queries = build_interview_queries(
        company="Example Corp",
        role="Data Engineer",
    )

    combined = " ".join(
        query.query
        for query in queries
    ).lower()

    assert "data engineer" in combined
    assert "software engineer" not in combined


def test_strips_input_whitespace() -> None:
    queries = build_interview_queries(
        company="  Stripe  ",
        role="  Backend Engineer  ",
    )

    assert '"Stripe"' in queries[0].query
    assert '"Backend Engineer"' in queries[0].query


def test_interview_queries_preserve_structured_context() -> None:
    queries = build_interview_queries(
        company=" Microsoft ",
        role=" Software Engineer Intern ",
    )

    assert len(queries) == 5

    assert all(
        query.company == "Microsoft"
        for query in queries
    )
    assert all(
        query.role == "Software Engineer Intern"
        for query in queries
    )
