import re
from dataclasses import dataclass

from app.models.source import SourceResult


INTERVIEW_TERMS = {
    "interview",
    "interviews",
    "interviewing",
    "assessment",
    "assessments",
    "technical screen",
    "technical interview",
    "coding challenge",
    "coding interview",
    "online assessment",
}


@dataclass
class ScoredSource:
    result: SourceResult
    score: int
    matched_terms: list[str]


def tokenize(text: str) -> set[str]:
    return set(
        re.findall(
            r"[a-z0-9+#.]+",
            text.lower(),
        )
    )


def score_source(
    result: SourceResult,
    company: str,
    role: str,
) -> ScoredSource:
    title = result.title.lower()
    content = result.content.lower()
    combined = f"{title} {content}"

    score = 0
    matched_terms: list[str] = []

    company_normalized = company.lower().strip()

    if company_normalized and company_normalized in combined:
        score += 5
        matched_terms.append(company_normalized)

    role_tokens = tokenize(role)

    ignored_role_terms = {
        "intern",
        "internship",
        "junior",
        "senior",
    }

    meaningful_role_tokens = (
        role_tokens - ignored_role_terms
    )

    matched_role_tokens = sorted(
        token
        for token in meaningful_role_tokens
        if token in tokenize(combined)
    )

    score += len(matched_role_tokens) * 2
    matched_terms.extend(matched_role_tokens)

    for term in sorted(INTERVIEW_TERMS):
        if term in combined:
            score += 3
            matched_terms.append(term)

    if company_normalized in title:
        score += 2

    if any(
        term in title
        for term in INTERVIEW_TERMS
    ):
        score += 2

    return ScoredSource(
        result=result,
        score=score,
        matched_terms=matched_terms,
    )


def rank_sources(
    results: list[SourceResult],
    company: str,
    role: str,
    minimum_score: int = 5,
) -> list[ScoredSource]:
    scored = [
        score_source(
            result=result,
            company=company,
            role=role,
        )
        for result in results
    ]

    relevant = [
        item
        for item in scored
        if item.score >= minimum_score
    ]

    return sorted(
        relevant,
        key=lambda item: item.score,
        reverse=True,
    )
