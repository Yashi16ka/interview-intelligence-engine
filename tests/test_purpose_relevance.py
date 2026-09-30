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
