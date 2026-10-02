import httpx

from app.models.intelligence import InterviewIntelligence
from app.services.purpose_relevance import ScoredEvidence


class UnavailableIntelligenceSynthesizer:
    async def synthesize(
        self,
        company: str,
        role: str,
        evidence: list[ScoredEvidence],
    ) -> InterviewIntelligence:
        request = httpx.Request(
            "POST",
            "https://generativelanguage.googleapis.com",
        )

        raise httpx.ConnectError(
            "Intelligence synthesis is not configured.",
            request=request,
        )
