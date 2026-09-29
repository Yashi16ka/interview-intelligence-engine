import re
from dataclasses import dataclass

from app.models.source import SourceResult


INTERVIEW_TERMS = {
    "interview",
    "interviews",
    "interviewing",
    "assessment",
    "assessments",
}

STRONG_INTERVIEW_TERMS = {
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


def has_contextual_match(
    text: str,
    company: str,
    interview_terms: set[str],
    window: int = 160,
) -> bool:
    text = text.lower()
    company = company.lower().strip()

    if not company:
        return False

    company_positions = [
        match.start()
        for match in re.finditer(
            re.escape(company),
            text,
        )
    ]

    for position in company_positions:
        start = max(0, position - window)
        end = min(
            len(text),
            position + len(company) + window,
        )
        context = text[start:end]

        if any(
            term in context
            for term in interview_terms
        ):
            return True

    return False


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

    if (
        company_normalized
        and company_normalized in combined
    ):
        score += 3
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

    combined_tokens = tokenize(combined)

    matched_role_tokens = sorted(
        token
        for token in meaningful_role_tokens
        if token in combined_tokens
    )

    score += len(matched_role_tokens)
    matched_terms.extend(matched_role_tokens)

    matched_interview_terms = [
        term
        for term in sorted(INTERVIEW_TERMS)
        if term in combined
    ]

    score += len(matched_interview_terms)
    matched_terms.extend(matched_interview_terms)

    matched_strong_terms = [
        term
        for term in sorted(STRONG_INTERVIEW_TERMS)
        if term in combined
    ]

    score += len(matched_strong_terms) * 2
    matched_terms.extend(matched_strong_terms)

    all_interview_terms = (
        INTERVIEW_TERMS
        | STRONG_INTERVIEW_TERMS
    )

    if has_contextual_match(
        text=combined,
        company=company_normalized,
        interview_terms=all_interview_terms,
    ):
        score += 6
        matched_terms.append("company_interview_context")

    if (
        company_normalized
        and company_normalized in title
    ):
        score += 2

    if any(
        term in title
        for term in all_interview_terms
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
    minimum_score: int = 8,
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
        and "company_interview_context" in item.matched_terms
    ]

    return sorted(
        relevant,
        key=lambda item: item.score,
        reverse=True,
    )
