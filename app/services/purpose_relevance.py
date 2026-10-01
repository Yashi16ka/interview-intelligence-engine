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

INTERVIEW_QUESTION_TERMS = {
    "question",
    "questions",
    "asked",
    "coding challenge",
    "coding problem",
    "technical question",
    "technical questions",
}

INTERVIEW_EXPERIENCE_TERMS = {
    "experience",
    "interviewed",
    "my interview",
    "failed",
    "passed",
    "passing",
    "candidate described",
    "candidates described",
    "interview round",
    "interview rounds",
    "interview process",
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


def get_company_contexts(
    text: str,
    company: str,
    window: int = 200,
) -> list[str]:
    text = text.lower()
    company = company.lower().strip()

    if not company:
        return []

    contexts: list[str] = []

    for match in re.finditer(
        re.escape(company),
        text,
    ):
        start = max(0, match.start() - window)
        end = min(
            len(text),
            match.end() + window,
        )
        contexts.append(text[start:end])

    return contexts


def has_company_term_context(
    text: str,
    company: str,
    terms: set[str],
    window: int = 200,
) -> bool:
    if not terms:
        return False

    return any(
        any(term in context for term in terms)
        for context in get_company_contexts(
            text=text,
            company=company,
            window=window,
        )
    )


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
    company_name = company.lower().strip()

    reverse_engineering_pattern = (
        rf"reverse\s+engineering\s+"
        rf"{re.escape(company_name)}(?:['’]s)?"
    )

    if re.search(reverse_engineering_pattern, combined):
        return None

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

            combined = (
                f"{item.result.title} "
                f"{item.result.content}"
            ).lower()

            company_contexts = get_company_contexts(
                text=combined,
                company=company,
            )

            if item.purpose == "interview_questions":
                company_name = company.lower().strip()

                positive_question_contexts = [
                    context
                    for context in company_contexts
                    if any(
                        term in context
                        for term in INTERVIEW_QUESTION_TERMS
                    )
                ]

                if not positive_question_contexts:
                    continue

                negated_question_pattern = (
                    rf"\bnot\b[^.!?]{{0,160}}"
                    rf"{re.escape(company_name)}"
                    rf"\s+interview\s+questions?\b"
                )

                if all(
                    re.search(
                        negated_question_pattern,
                        context,
                    )
                    for context in positive_question_contexts
                ):
                    continue

            if item.purpose == "interview_experience":
                title = item.result.title.lower()

                has_title_experience = any(
                    term in title
                    for term in INTERVIEW_EXPERIENCE_TERMS
                )

                has_first_person_title = bool(
                    re.search(
                        r"\b(?:my|i)\b",
                        title,
                    )
                )

                has_question_title = any(
                    term in title
                    for term in INTERVIEW_QUESTION_TERMS
                )

                if (
                    has_question_title
                    and not has_title_experience
                    and not has_first_person_title
                ):
                    continue

                has_context_experience = any(
                    any(
                        term in context
                        for term in INTERVIEW_EXPERIENCE_TERMS
                    )
                    for context in company_contexts
                )

                if not (
                    has_title_experience
                    or has_first_person_title
                    or has_context_experience
                ):
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
