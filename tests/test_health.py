import httpx
from fastapi.testclient import TestClient

from app.main import create_app
from app.models.evidence import EvidenceItem
from app.models.intelligence import InterviewIntelligence, KeyTopic
from app.models.source import SourceResult
from app.services.pipeline import (
    ProcessedPurposeEvidence,
    ProcessingStats,
)
from app.services.purpose_relevance import ScoredEvidence
from app.services.synthesis_errors import SynthesisResponseError


class FakeResearchEngine:
    async def research(
        self,
        company: str,
        role: str,
    ) -> ProcessedPurposeEvidence:
        evidence = EvidenceItem(
            result=SourceResult(
                source="fake_ats",
                title="Software Engineer Intern",
                url="https://example.com/job",
                content=(
                    "Salesforce Software Engineer requirements "
                    "include Python and APIs."
                ),
            ),
            purpose="role_requirements",
            provider="fake_ats",
        )

        return ProcessedPurposeEvidence(
            evidence=[
                ScoredEvidence(
                    evidence=evidence,
                    score=8,
                    matched_terms=[
                        "salesforce",
                        "software",
                        "engineer",
                    ],
                )
            ],
            stats=ProcessingStats(
                raw_count=1,
                normalized_count=1,
                unique_count=1,
                relevant_count=1,
            ),
        )


class FakeSynthesizer:
    async def synthesize(
        self,
        company: str,
        role: str,
        evidence: list[ScoredEvidence],
    ) -> InterviewIntelligence:
        assert company == "Salesforce"
        assert role == "Software Engineer Intern"
        assert len(evidence) == 1

        return InterviewIntelligence(
            key_topics=[
                KeyTopic(
                    topic="Python and APIs",
                    reason="Supported by role requirements.",
                    evidence_urls=[
                        evidence[0].evidence.result.url,
                    ],
                )
            ]
        )


app = create_app(
    research_engine=FakeResearchEngine(),
    intelligence_synthesizer=FakeSynthesizer(),
)


def test_health() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
    }


def test_research_request() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/research",
            json={
                "company": "Salesforce",
                "role": "Software Engineer Intern",
            },
        )

    assert response.status_code == 200
    assert response.json() == {
        "company": "Salesforce",
        "role": "Software Engineer Intern",
        "status": "completed",
        "stats": {
            "raw_count": 1,
            "normalized_count": 1,
            "unique_count": 1,
            "relevant_count": 1,
        },
        "evidence": [
            {
                "source": "fake_ats",
                "title": "Software Engineer Intern",
                "url": "https://example.com/job",
                "purpose": "role_requirements",
                "provider": "fake_ats",
                "score": 8,
                "matched_terms": [
                    "salesforce",
                    "software",
                    "engineer",
                ],
            }
        ],
        "intelligence": {
            "key_topics": [
                {
                    "topic": "Python and APIs",
                    "reason": "Supported by role requirements.",
                    "evidence_urls": [
                        "https://example.com/job",
                    ],
                }
            ],
            "likely_questions": [],
            "preparation_priorities": [],
            "study_plan": [],
        },
    }


class UnavailableSynthesizer:
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
        response = httpx.Response(
            503,
            request=request,
        )

        raise httpx.HTTPStatusError(
            "Gemini unavailable",
            request=request,
            response=response,
        )


def test_research_returns_partial_when_synthesis_unavailable() -> None:
    partial_app = create_app(
        research_engine=FakeResearchEngine(),
        intelligence_synthesizer=UnavailableSynthesizer(),
    )

    with TestClient(partial_app) as client:
        response = client.post(
            "/research",
            json={
                "company": "Salesforce",
                "role": "Software Engineer Intern",
            },
        )

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "partial"
    assert len(payload["evidence"]) == 1
    assert payload["intelligence"] == {
        "key_topics": [],
        "likely_questions": [],
        "preparation_priorities": [],
        "study_plan": [],
    }



def test_app_starts_without_gemini_api_key(
    monkeypatch,
) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    app_without_gemini = create_app(
        research_engine=FakeResearchEngine(),
    )

    with TestClient(app_without_gemini) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
    }

    with TestClient(app_without_gemini) as client:
        research_response = client.post(
            "/research",
            json={
                "company": "Salesforce",
                "role": "Software Engineer Intern",
            },
        )

    assert research_response.status_code == 200

    payload = research_response.json()

    assert payload["status"] == "partial"
    assert len(payload["evidence"]) == 1
    assert payload["intelligence"] == {
        "key_topics": [],
        "likely_questions": [],
        "preparation_priorities": [],
        "study_plan": [],
    }


class InvalidResponseSynthesizer:
    async def synthesize(
        self,
        company: str,
        role: str,
        evidence: list[ScoredEvidence],
    ) -> InterviewIntelligence:
        raise SynthesisResponseError(
            "Gemini returned invalid synthesis output."
        )


def test_research_returns_partial_when_synthesis_response_is_invalid() -> None:
    invalid_response_app = create_app(
        research_engine=FakeResearchEngine(),
        intelligence_synthesizer=InvalidResponseSynthesizer(),
    )

    with TestClient(invalid_response_app) as client:
        response = client.post(
            "/research",
            json={
                "company": "Salesforce",
                "role": "Software Engineer Intern",
            },
        )

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "partial"
    assert len(payload["evidence"]) == 1
    assert payload["intelligence"] == {
        "key_topics": [],
        "likely_questions": [],
        "preparation_priorities": [],
        "study_plan": [],
    }
