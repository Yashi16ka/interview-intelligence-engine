import pytest

from app.models.evidence import EvidenceItem
from app.models.source import SourceResult
from app.services.intelligence_resolver import resolve_evidence_ids
from app.services.purpose_relevance import ScoredEvidence


def make_evidence(url: str) -> ScoredEvidence:
    return ScoredEvidence(
        evidence=EvidenceItem(
            result=SourceResult(
                source="browser",
                title="Interview evidence",
                url=url,
                content="Relevant interview evidence.",
            ),
            purpose="interview_experience",
            provider="test",
        ),
        score=15,
        matched_terms=["interview"],
    )


def test_resolve_evidence_ids_to_source_urls() -> None:
    evidence = [
        make_evidence("https://example.com/one"),
        make_evidence("https://example.com/two"),
    ]

    urls = resolve_evidence_ids(
        evidence_ids=["E2", "E1"],
        evidence=evidence,
    )

    assert [str(url) for url in urls] == [
        "https://example.com/two",
        "https://example.com/one",
    ]


def test_resolve_evidence_ids_deduplicates_urls() -> None:
    evidence = [
        make_evidence("https://example.com/one"),
    ]

    urls = resolve_evidence_ids(
        evidence_ids=["E1", "E1"],
        evidence=evidence,
    )

    assert [str(url) for url in urls] == [
        "https://example.com/one",
    ]


def test_resolve_evidence_ids_rejects_unknown_id() -> None:
    evidence = [
        make_evidence("https://example.com/one"),
    ]

    with pytest.raises(
        ValueError,
        match="Unknown evidence ID: E99",
    ):
        resolve_evidence_ids(
            evidence_ids=["E99"],
            evidence=evidence,
        )

from app.models.synthesis import SynthesisResponse
from app.services.intelligence_resolver import (
    resolve_synthesis_response,
)


def test_resolve_synthesis_response_to_intelligence() -> None:
    evidence = [
        make_evidence("https://example.com/one"),
        make_evidence("https://example.com/two"),
    ]

    synthesis = SynthesisResponse.model_validate(
        {
            "key_topics": [
                {
                    "topic": "System design",
                    "reason": "Appears across evidence.",
                    "evidence_ids": ["E1", "E2"],
                }
            ],
            "likely_questions": [
                {
                    "question": "How would you design an API?",
                    "rationale": "Supported by design evidence.",
                    "evidence_ids": ["E1"],
                }
            ],
            "preparation_priorities": [
                {
                    "priority": "Practice system design",
                    "reason": "It is repeatedly emphasized.",
                    "evidence_ids": ["E2"],
                }
            ],
            "study_plan": [
                {
                    "action": "Complete one design exercise.",
                    "focus": "System design",
                    "evidence_ids": ["E1"],
                }
            ],
        }
    )

    result = resolve_synthesis_response(
        synthesis=synthesis,
        evidence=evidence,
    )

    assert result.key_topics[0].topic == "System design"
    assert [
        str(url)
        for url in result.key_topics[0].evidence_urls
    ] == [
        "https://example.com/one",
        "https://example.com/two",
    ]
    assert [
        str(url)
        for url in result.likely_questions[0].evidence_urls
    ] == ["https://example.com/one"]
    assert [
        str(url)
        for url in (
            result.preparation_priorities[0].evidence_urls
        )
    ] == ["https://example.com/two"]
    assert [
        str(url)
        for url in result.study_plan[0].evidence_urls
    ] == ["https://example.com/one"]
