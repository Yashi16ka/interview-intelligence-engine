from pydantic import HttpUrl

from app.models.intelligence import (
    InterviewIntelligence,
    KeyTopic,
    LikelyQuestion,
    PreparationPriority,
    StudyPlanItem,
)
from app.models.synthesis import SynthesisResponse
from app.services.purpose_relevance import ScoredEvidence


def resolve_evidence_ids(
    evidence_ids: list[str],
    evidence: list[ScoredEvidence],
) -> list[HttpUrl]:
    resolved: list[HttpUrl] = []
    seen_urls: set[str] = set()

    for evidence_id in evidence_ids:
        if (
            not evidence_id.startswith("E")
            or not evidence_id[1:].isdigit()
        ):
            raise ValueError(
                f"Unknown evidence ID: {evidence_id}"
            )

        index = int(evidence_id[1:]) - 1

        if index < 0 or index >= len(evidence):
            raise ValueError(
                f"Unknown evidence ID: {evidence_id}"
            )

        url = evidence[index].evidence.result.url
        url_key = str(url)

        if url_key in seen_urls:
            continue

        seen_urls.add(url_key)
        resolved.append(url)

    return resolved

def resolve_synthesis_response(
    synthesis: SynthesisResponse,
    evidence: list[ScoredEvidence],
) -> InterviewIntelligence:
    return InterviewIntelligence(
        key_topics=[
            KeyTopic(
                topic=item.topic,
                reason=item.reason,
                evidence_urls=resolve_evidence_ids(
                    evidence_ids=item.evidence_ids,
                    evidence=evidence,
                ),
            )
            for item in synthesis.key_topics
        ],
        likely_questions=[
            LikelyQuestion(
                question=item.question,
                rationale=item.rationale,
                evidence_urls=resolve_evidence_ids(
                    evidence_ids=item.evidence_ids,
                    evidence=evidence,
                ),
            )
            for item in synthesis.likely_questions
        ],
        preparation_priorities=[
            PreparationPriority(
                priority=item.priority,
                reason=item.reason,
                evidence_urls=resolve_evidence_ids(
                    evidence_ids=item.evidence_ids,
                    evidence=evidence,
                ),
            )
            for item in synthesis.preparation_priorities
        ],
        study_plan=[
            StudyPlanItem(
                action=item.action,
                focus=item.focus,
                evidence_urls=resolve_evidence_ids(
                    evidence_ids=item.evidence_ids,
                    evidence=evidence,
                ),
            )
            for item in synthesis.study_plan
        ],
    )
