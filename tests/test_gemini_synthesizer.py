import json

import httpx
import pytest

from app.models.evidence import EvidenceItem
from app.models.source import SourceResult
from app.services.gemini_synthesizer import GeminiSynthesizer
from app.services.purpose_relevance import ScoredEvidence


def make_evidence() -> list[ScoredEvidence]:
    return [
        ScoredEvidence(
            evidence=EvidenceItem(
                result=SourceResult(
                    source="browser",
                    title="Interview experience",
                    url="https://example.com/interview",
                    content=(
                        "The interview included a "
                        "system design round."
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


@pytest.mark.anyio
async def test_gemini_synthesizer_returns_grounded_intelligence() -> None:
    synthesis_json = {
        "key_topics": [
            {
                "topic": "System design",
                "reason": "The interview evidence includes it.",
                "evidence_ids": ["E1"],
            }
        ],
        "likely_questions": [],
        "preparation_priorities": [],
        "study_plan": [],
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["x-goog-api-key"] == "test-key"

        payload = json.loads(request.content)

        assert "contents" in payload
        assert "generationConfig" in payload
        assert (
            payload["generationConfig"]["responseMimeType"]
            == "application/json"
        )
        assert "responseSchema" in payload["generationConfig"]

        return httpx.Response(
            200,
            json={
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "text": json.dumps(
                                        synthesis_json
                                    )
                                }
                            ]
                        }
                    }
                ]
            },
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler)
    ) as client:
        synthesizer = GeminiSynthesizer(
            api_key="test-key",
            client=client,
        )

        result = await synthesizer.synthesize(
            company="Example",
            role="Software Engineer",
            evidence=make_evidence(),
        )

    assert result.key_topics[0].topic == "System design"
    assert [
        str(url)
        for url in result.key_topics[0].evidence_urls
    ] == ["https://example.com/interview"]


@pytest.mark.anyio
async def test_gemini_synthesizer_skips_model_when_no_evidence() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError(
            "Gemini should not be called when evidence is empty"
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler)
    ) as client:
        synthesizer = GeminiSynthesizer(
            api_key="test-key",
            client=client,
        )

        result = await synthesizer.synthesize(
            company="Example",
            role="Software Engineer",
            evidence=[],
        )

    assert result.key_topics == []
    assert result.likely_questions == []
    assert result.preparation_priorities == []
    assert result.study_plan == []


@pytest.mark.anyio
async def test_gemini_synthesizer_rejects_unknown_evidence_id() -> None:
    synthesis_json = {
        "key_topics": [
            {
                "topic": "System design",
                "reason": "Prepare system design.",
                "evidence_ids": ["E99"],
            }
        ],
        "likely_questions": [],
        "preparation_priorities": [],
        "study_plan": [],
    }

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "text": json.dumps(
                                        synthesis_json
                                    )
                                }
                            ]
                        }
                    }
                ]
            },
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler)
    ) as client:
        synthesizer = GeminiSynthesizer(
            api_key="test-key",
            client=client,
        )

        with pytest.raises(
            ValueError,
            match="Unknown evidence ID: E99",
        ):
            await synthesizer.synthesize(
                company="Example",
                role="Software Engineer",
                evidence=make_evidence(),
            )


@pytest.mark.anyio
async def test_gemini_synthesizer_retries_temporary_503() -> None:
    synthesis_json = {
        "key_topics": [
            {
                "topic": "System design",
                "reason": "Supported by interview evidence.",
                "evidence_ids": ["E1"],
            }
        ],
        "likely_questions": [],
        "preparation_priorities": [],
        "study_plan": [],
    }

    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        if attempts == 1:
            return httpx.Response(
                503,
                json={
                    "error": {
                        "code": 503,
                        "message": "Model temporarily unavailable.",
                        "status": "UNAVAILABLE",
                    }
                },
            )

        return httpx.Response(
            200,
            json={
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "text": json.dumps(
                                        synthesis_json
                                    )
                                }
                            ]
                        }
                    }
                ]
            },
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler)
    ) as client:
        synthesizer = GeminiSynthesizer(
            api_key="test-key",
            client=client,
            retry_delay=0,
        )

        result = await synthesizer.synthesize(
            company="Example",
            role="Software Engineer",
            evidence=make_evidence(),
        )

    assert attempts == 2
    assert result.key_topics[0].topic == "System design"


@pytest.mark.anyio
async def test_gemini_synthesizer_does_not_retry_400() -> None:
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        return httpx.Response(
            400,
            json={
                "error": {
                    "code": 400,
                    "message": "Invalid request.",
                    "status": "INVALID_ARGUMENT",
                }
            },
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler)
    ) as client:
        synthesizer = GeminiSynthesizer(
            api_key="test-key",
            client=client,
            retry_delay=0,
        )

        with pytest.raises(httpx.HTTPStatusError):
            await synthesizer.synthesize(
                company="Example",
                role="Software Engineer",
                evidence=make_evidence(),
            )

    assert attempts == 1
