from fastapi.testclient import TestClient

from app.main import create_app
from app.models.evidence import EvidenceItem
from app.models.source import SourceResult
from app.services.pipeline import (
    ProcessedPurposeEvidence,
    ProcessingStats,
)
from app.services.purpose_relevance import ScoredEvidence


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


app = create_app(
    research_engine=FakeResearchEngine(),
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
    }
