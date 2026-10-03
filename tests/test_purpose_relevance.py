from app.models.evidence import EvidenceItem
from app.models.source import SourceResult
from app.services.purpose_relevance import rank_evidence


def make_evidence(
    *,
    purpose: str,
    title: str,
    content: str,
    url: str,
) -> EvidenceItem:
    return EvidenceItem(
        result=SourceResult(
            source="browser",
            title=title,
            url=url,
            content=content,
        ),
        purpose=purpose,
        provider="test",
    )


def test_interview_evidence_requires_interview_context() -> None:
    evidence = make_evidence(
        purpose="interview_experience",
        title="Microsoft Software Engineer Interview",
        content=(
            "Microsoft Software Engineer candidates "
            "described a technical interview and coding challenge."
        ),
        url="https://example.com/interview",
    )

    ranked = rank_evidence(
        evidence=[evidence],
        company="Microsoft",
        role="Software Engineer Intern",
    )

    assert len(ranked) == 1
    assert ranked[0].evidence.purpose == "interview_experience"


def test_role_requirements_do_not_require_interview_terms() -> None:
    evidence = make_evidence(
        purpose="role_requirements",
        title="NVIDIA Machine Learning Intern",
        content=(
            "NVIDIA is hiring a Machine Learning Intern. "
            "Candidates should have experience with Python, "
            "PyTorch, machine learning, and data structures."
        ),
        url="https://example.com/nvidia-job",
    )

    ranked = rank_evidence(
        evidence=[evidence],
        company="NVIDIA",
        role="Machine Learning Intern",
    )

    assert len(ranked) == 1
    assert ranked[0].evidence.purpose == "role_requirements"


def test_company_engineering_does_not_require_interview_terms() -> None:
    evidence = make_evidence(
        purpose="company_engineering",
        title="NVIDIA Engineering",
        content=(
            "NVIDIA engineering teams build GPU computing "
            "platforms, machine learning systems, and "
            "accelerated computing technology."
        ),
        url="https://example.com/nvidia-engineering",
    )

    ranked = rank_evidence(
        evidence=[evidence],
        company="NVIDIA",
        role="Machine Learning Intern",
    )

    assert len(ranked) == 1
    assert ranked[0].evidence.purpose == "company_engineering"


def test_role_requirements_reject_unrelated_company_mention() -> None:
    evidence = make_evidence(
        purpose="role_requirements",
        title="General Software Jobs",
        content=(
            "This article briefly mentions NVIDIA products. "
            "Another unrelated company is hiring software "
            "engineers and requires Python experience."
        ),
        url="https://example.com/unrelated",
    )

    ranked = rank_evidence(
        evidence=[evidence],
        company="NVIDIA",
        role="Machine Learning Intern",
    )

    assert ranked == []


def test_role_requirements_rejects_company_role_without_hiring_context() -> None:
    evidence = make_evidence(
        purpose="role_requirements",
        title="NVIDIA Machine Learning Engineering",
        content=(
            "NVIDIA machine learning engineers build "
            "accelerated computing systems and GPU platforms."
        ),
        url="https://example.com/nvidia-engineering",
    )

    ranked = rank_evidence(
        evidence=[evidence],
        company="NVIDIA",
        role="Machine Learning Intern",
    )

    assert ranked == []


def test_interview_experience_keeps_first_person_account() -> None:
    evidence = make_evidence(
        purpose="interview_experience",
        title="That time when I failed the Microsoft interview",
        content=(
            "I interviewed at Microsoft for a Software Engineer role. "
            "My interview included a coding round, and I struggled "
            "with one of the technical questions."
        ),
        url="https://example.com/microsoft-experience",
    )

    ranked = rank_evidence(
        evidence=[evidence],
        company="Microsoft",
        role="Software Engineer Intern",
    )

    assert len(ranked) == 1


def test_interview_questions_rejects_incidental_interview_mentions() -> None:
    evidence = make_evidence(
        purpose="interview_questions",
        title="Ask HN: A human nature thought experiment",
        content=(
            "This is a discussion about human behavior and Microsoft. "
            "Elsewhere, someone mentions preparing for a software "
            "interview. The discussion is about workplace behavior "
            "rather than the interview process."
        ),
        url="https://example.com/thought-experiment",
    )

    ranked = rank_evidence(
        evidence=[evidence],
        company="Microsoft",
        role="Software Engineer Intern",
    )

    assert ranked == []


def test_company_engineering_rejects_reverse_engineering_company_product() -> None:
    evidence = make_evidence(
        purpose="company_engineering",
        title="Reverse engineering Microsoft's dev container CLI",
        content=(
            "I spent the weekend reverse engineering Microsoft's "
            "dev container CLI and documenting how the protocol works."
        ),
        url="https://example.com/reverse-engineering",
    )

    ranked = rank_evidence(
        evidence=[evidence],
        company="Microsoft",
        role="Software Engineer Intern",
    )

    assert ranked == []


def test_company_engineering_keeps_company_engineering_practices() -> None:
    evidence = make_evidence(
        purpose="company_engineering",
        title="Microsoft Engineering",
        content=(
            "Microsoft engineering teams describe how they design "
            "platform architecture, infrastructure, and distributed "
            "systems for production services."
        ),
        url="https://example.com/microsoft-engineering",
    )

    ranked = rank_evidence(
        evidence=[evidence],
        company="Microsoft",
        role="Software Engineer Intern",
    )

    assert len(ranked) == 1


def test_interview_questions_rejects_explicitly_negated_question() -> None:
    evidence = make_evidence(
        purpose="interview_questions",
        title="Ask HN: A human nature thought experiment",
        content=(
            "This is not a high school math problem, or a Microsoft "
            "interview question, it's a human nature problem."
        ),
        url="https://example.com/human-nature",
    )

    ranked = rank_evidence(
        evidence=[evidence],
        company="Microsoft",
        role="Software Engineer Intern",
    )

    assert ranked == []


def test_interview_questions_keeps_reported_company_question() -> None:
    evidence = make_evidence(
        purpose="interview_questions",
        title="A classic puzzle",
        content=(
            "Years ago, Microsoft apparently used to ask this puzzle "
            "as an interview question. Here is the problem."
        ),
        url="https://example.com/classic-puzzle",
    )

    ranked = rank_evidence(
        evidence=[evidence],
        company="Microsoft",
        role="Software Engineer Intern",
    )

    assert len(ranked) == 1


def test_interview_experience_rejects_question_collection() -> None:
    evidence = make_evidence(
        purpose="interview_experience",
        title="Microsoft Interview Riddle Questions",
        content=(
            "Microsoft interviews frequently incorporate riddle-style "
            "questions. What kind of interview questions will they ask? "
            "Let's see what Microsoft asked before in this article."
        ),
        url="https://example.com/riddle-questions",
    )

    ranked = rank_evidence(
        evidence=[evidence],
        company="Microsoft",
        role="Software Engineer Intern",
    )

    assert ranked == []


def test_interview_experience_rejects_question_title_with_related_experience_link() -> None:
    evidence = make_evidence(
        purpose="interview_experience",
        title="Microsoft Interview Riddle Questions",
        content=(
            "Microsoft interviews frequently incorporate riddle-style "
            "questions to assess reasoning. What kind of interview "
            "questions will they ask? Let's see what Microsoft asked. "
            "RELATED Java Interview Questions. Rebirth of Microsoft? "
            "A crazy interview experience. What should Microsoft do "
            "after Steve Ballmer steps down?"
        ),
        url="https://example.com/riddle-questions-related-links",
    )

    ranked = rank_evidence(
        evidence=[evidence],
        company="Microsoft",
        role="Software Engineer Intern",
    )

    assert ranked == []


def test_company_engineering_rejects_company_name_used_as_ordinary_word() -> None:
    evidence = make_evidence(
        purpose="company_engineering",
        title=(
            "HN: good interdisciplinary MS/PhD programs "
            "for tech/culture?"
        ),
        content=(
            "I'm looking for programs that integrate cultural "
            "issues with engineering and technology."
        ),
        url="https://example.com/interdisciplinary",
    )

    ranked = rank_evidence(
        evidence=[evidence],
        company="Integrate",
        role="Software Engineer",
    )

    assert ranked == []


def test_company_engineering_keeps_ambiguous_name_with_entity_context() -> None:
    evidence = make_evidence(
        purpose="company_engineering",
        title="Engineering architecture discussion",
        content=(
            "Engineers at Integrate describe how their team "
            "builds platform architecture and production systems."
        ),
        url="https://example.com/integrate-engineering",
    )

    ranked = rank_evidence(
        evidence=[evidence],
        company="Integrate",
        role="Software Engineer",
    )

    assert len(ranked) == 1
    assert ranked[0].evidence.purpose == "company_engineering"


def test_interview_experience_rejects_company_name_used_as_ordinary_word() -> None:
    evidence = make_evidence(
        purpose="interview_experience",
        title="Just paid the May server bill for Tech Interview Experience",
        content=(
            "This site collects interview experiences from candidates. "
            "Job portals could integrate this into their site to help "
            "people prepare for interviews."
        ),
        url="https://example.com/tech-interview-experience",
    )

    ranked = rank_evidence(
        evidence=[evidence],
        company="Integrate",
        role="Software Engineer",
    )

    assert ranked == []


def test_interview_experience_keeps_ambiguous_name_with_entity_context() -> None:
    evidence = make_evidence(
        purpose="interview_experience",
        title="My software engineering interview experience",
        content=(
            "I interviewed at Integrate for a Software Engineer role. "
            "My interview included a coding round and technical questions."
        ),
        url="https://example.com/integrate-interview",
    )

    ranked = rank_evidence(
        evidence=[evidence],
        company="Integrate",
        role="Software Engineer",
    )

    assert len(ranked) == 1
    assert ranked[0].evidence.purpose == "interview_experience"
