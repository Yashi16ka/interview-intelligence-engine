from typing import Protocol

from app.models.intelligence import InterviewIntelligence
from app.services.purpose_relevance import ScoredEvidence


class IntelligenceSynthesizer(Protocol):
    async def synthesize(
        self,
        company: str,
        role: str,
        evidence: list[ScoredEvidence],
    ) -> InterviewIntelligence:
        ...
