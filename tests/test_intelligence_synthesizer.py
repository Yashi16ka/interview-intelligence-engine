import pytest

from app.models.evidence import EvidenceItem
from app.models.intelligence import (
    InterviewIntelligence,
    KeyTopic,
)
from app.models.source import SourceResult
from app.services.intelligence_synthesizer import (
    IntelligenceSynthesizer,
)
from app.services.purpose_relevance import ScoredEvidence


class FakeSynthesizer:
    async def synthesize(
        self,
        company: str,
        role: str,
        evidence: list[ScoredEvidence],
    ) -> InterviewIntelligence:
        item = evidence[0]

        return InterviewIntelligence(
            key_topics=[
                KeyTopic(
                    topic="System design",
                    reason=(
                        f"Grounded in evidence for "
                        f"{company} {role}."
                    ),
                    evidence_urls=[
                        item.evidence.result.url
                    ],
                ),
            ],
        )


@pytest.mark.anyio
async def test_synthesizer_receives_ranked_evidence() -> None:
    synthesizer: IntelligenceSynthesizer = FakeSynthesizer()

    evidence = [
        ScoredEvidence(
            evidence=EvidenceItem(
                result=SourceResult(
                    source="browser",
                    title="Interview experience",
                    url="https://example.com/interview",
                    content=(
                        "The interview included "
                        "a system design round."
                    ),
                ),
                purpose="interview_experience",
                provider="test",
            ),
            score=15,
            matched_terms=[
                "interview",
                "system design",
            ],
        ),
    ]

    result = await synthesizer.synthesize(
        company="Example",
        role="Software Engineer",
        evidence=evidence,
    )

    assert result.key_topics[0].topic == "System design"
    assert (
        str(result.key_topics[0].evidence_urls[0])
        == "https://example.com/interview"
    )
