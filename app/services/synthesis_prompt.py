from app.services.purpose_relevance import ScoredEvidence


def build_synthesis_prompt(
    company: str,
    role: str,
    evidence: list[ScoredEvidence],
    max_content_chars: int = 4000,
) -> str:
    evidence_sections: list[str] = []

    for index, item in enumerate(evidence, start=1):
        source = item.evidence.result
        content = source.content[:max_content_chars]

        evidence_sections.append(
            "\n".join(
                [
                    f"[E{index}]",
                    f"Purpose: {item.evidence.purpose}",
                    f"Provider: {item.evidence.provider}",
                    f"Score: {item.score}",
                    (
                        "Matched terms: "
                        + ", ".join(item.matched_terms)
                    ),
                    f"Title: {source.title}",
                    f"URL: {source.url}",
                    f"Content: {content}",
                ]
            )
        )

    evidence_text = "\n\n".join(evidence_sections)

    return f"""You are synthesizing interview preparation intelligence
from retrieved evidence.

Company: {company}
Role: {role}

Use only the evidence below. Do not invent company-specific facts,
interview stages, requirements, or questions that are not supported
by the evidence.

Create:
1. Key topics the candidate should prepare.
2. Evidence-grounded practice questions.
3. Preparation priorities with reasons.
4. Concrete study-plan actions.

Every claim must cite one or more evidence IDs such as E1 or E2.
Do not cite an evidence ID unless that evidence supports the claim.
Treat practice questions as preparation material, not predictions of
exact questions the interviewer will ask.

Return structured JSON only.

Evidence:
{evidence_text}
"""
