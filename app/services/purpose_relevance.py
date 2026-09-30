import re
from dataclasses import dataclass

from app.models.evidence import EvidenceItem
from app.services.relevance import (
    ScoredSource,
    rank_sources,
    tokenize,
)


INTERVIEW_PURPOSES = {
    "interview_experience",
    "interview_questions",
    "technical_interview",
}

ENGINEERING_TERMS = {
    "engineering",
    "engineer",
    "technology",
    "technical",
    "platform",
    "infrastructure",
    "architecture",
    "systems",
}

IGNORED_ROLE_TERMS = {
    "intern",
    "internship",
    "junior",
    "senior",
}

REQUIREMENT_TERMS = {
    "requirement",
    "requirements",
    "qualification",
    "qualifications",
    "required",
    "preferred",
    "candidate",
    "candidates",
    "hiring",
    "job",
    "position",
    "role",
}


@dataclass
class ScoredEvidence:
    evidence: EvidenceItem
    score: int
    matched_terms: list[str]


def has_company_term_context(
    text: str,
    company: str,
    terms: set[str],
    window: int = 200,
) -> bool:
    text = text.lower()
    company = company.lower().strip()

    if not company or not terms:
        return False

    for match in re.finditer(
        re.escape(company),
        text,
    ):
        start = max(0, match.start() - window)
        end = min(
            len(text),
            match.end() + window,
        )
        context = text[start:end]

        if any(term in context for term in terms):
            return True

    return False


def score_role_requirements(
    evidence: EvidenceItem,
    company: str,
    role: str,
) -> ScoredEvidence | None:
    result = evidence.result
    combined = f"{result.title} {result.content}".lower()

    role_terms = (
        tokenize(role)
        - IGNORED_ROLE_TERMS
    )

    if not has_company_term_context(
        text=combined,
        company=company,
        terms=role_terms,
    ):
        return None

    if not has_company_term_context(
        text=combined,
        company=company,
        terms=REQUIREMENT_TERMS,
    ):
        return None

    matched_role_terms = sorted(
        term
        for term in role_terms
        if term in tokenize(combined)
    )

    score = 6 + len(matched_role_terms)

    return ScoredEvidence(
        evidence=evidence,
        score=score,
        matched_terms=[
            company.lower().strip(),
            *matched_role_terms,
            "company_role_context",
            "company_requirement_context",
        ],
    )


def score_company_engineering(
    evidence: EvidenceItem,
    company: str,
) -> ScoredEvidence | None:
    result = evidence.result
    combined = f"{result.title} {result.content}".lower()

    if not has_company_term_context(
        text=combined,
        company=company,
        terms=ENGINEERING_TERMS,
    ):
        return None

    matched_terms = sorted(
        term
        for term in ENGINEERING_TERMS
        if term in combined
    )

    score = 6 + len(matched_terms)

    return ScoredEvidence(
        evidence=evidence,
        score=score,
        matched_terms=[
            company.lower().strip(),
            *matched_terms,
            "company_engineering_context",
        ],
    )


def rank_evidence(
    evidence: list[EvidenceItem],
    company: str,
    role: str,
) -> list[ScoredEvidence]:
    ranked: list[ScoredEvidence] = []

    for item in evidence:
        if item.purpose in INTERVIEW_PURPOSES:
            interview_results: list[ScoredSource] = rank_sources(
                results=[item.result],
                company=company,
                role=role,
            )

            if not interview_results:
                continue

            scored = interview_results[0]

            ranked.append(
                ScoredEvidence(
                    evidence=item,
                    score=scored.score,
                    matched_terms=scored.matched_terms,
                )
            )

        elif item.purpose == "role_requirements":
            scored = score_role_requirements(
                evidence=item,
                company=company,
                role=role,
            )

            if scored is not None:
                ranked.append(scored)

        elif item.purpose == "company_engineering":
            scored = score_company_engineering(
                evidence=item,
                company=company,
            )

            if scored is not None:
                ranked.append(scored)

    return sorted(
        ranked,
        key=lambda item: item.score,
        reverse=True,
    )
