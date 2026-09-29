import httpx
import pytest

from app.services.collectors.jobs import JobsCollector


@pytest.mark.anyio
async def test_jobs_collector(monkeypatch) -> None:
    async def mock_get(self, url, **kwargs):
        request = httpx.Request("GET", url)

        return httpx.Response(
            200,
            request=request,
            json={
                "jobs": [
                    {
                        "company_name": "Salesforce",
                        "title": "Software Engineer Intern",
                        "url": "https://example.com/jobs/123",
                        "description": (
                            "Build backend services using Python, "
                            "SQL, and distributed systems."
                        ),
                    },
                    {
                        "company_name": "Different Company",
                        "title": "Software Engineer Intern",
                        "url": "https://example.com/jobs/456",
                        "description": "Unrelated job.",
                    },
                ]
            },
        )

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    collector = JobsCollector()

    results = await collector.collect(
        company="Salesforce",
        role="Software Engineer Intern",
    )

    assert len(results) == 1

    result = results[0]

    assert result.source == "jobs"
    assert result.title == "Software Engineer Intern"
    assert "Python" in result.content
    assert str(result.url) == "https://example.com/jobs/123"
