import asyncio
import json

import httpx

from app.models.intelligence import InterviewIntelligence
from app.models.synthesis import SynthesisResponse
from app.services.gemini_schema import flatten_json_schema
from app.services.intelligence_resolver import resolve_synthesis_response
from app.services.purpose_relevance import ScoredEvidence
from app.services.synthesis_prompt import build_synthesis_prompt


class GeminiSynthesizer:
    def __init__(
        self,
        api_key: str,
        client: httpx.AsyncClient,
        model: str = "gemini-3.8-flash",
        max_attempts: int = 3,
        retry_delay: float = 1.0,
    ) -> None:
        self.api_key = api_key
        self.client = client
        self.model = model
        self.max_attempts = max_attempts
        self.retry_delay = retry_delay

    async def synthesize(
        self,
        company: str,
        role: str,
        evidence: list[ScoredEvidence],
    ) -> InterviewIntelligence:
        if not evidence:
            return InterviewIntelligence()

        prompt = build_synthesis_prompt(
            company=company,
            role=role,
            evidence=evidence,
        )

        schema = flatten_json_schema(
            SynthesisResponse.model_json_schema()
        )

        response = None

        for attempt in range(1, self.max_attempts + 1):
            response = await self.client.post(
                (
                    "https://generativelanguage.googleapis.com/v1beta/"
                    f"models/{self.model}:generateContent"
                ),
                headers={
                    "x-goog-api-key": self.api_key,
                    "Content-Type": "application/json",
                },
                json={
                    "contents": [
                        {
                            "parts": [
                                {
                                    "text": prompt,
                                }
                            ]
                        }
                    ],
                    "generationConfig": {
                        "responseMimeType": "application/json",
                        "responseSchema": schema,
                    },
                },
            )

            if response.status_code not in {429, 500, 502, 503, 504}:
                break

            if attempt == self.max_attempts:
                break

            await asyncio.sleep(
                self.retry_delay * attempt
            )

        response.raise_for_status()

        payload = response.json()

        text = payload["candidates"][0]["content"]["parts"][0]["text"]
        synthesis_data = json.loads(text)

        synthesis = SynthesisResponse.model_validate(
            synthesis_data
        )

        return resolve_synthesis_response(
            synthesis=synthesis,
            evidence=evidence,
        )
