import httpx
import pytest

from app.services.collectors.hackernews import HackerNewsCollector


@pytest.mark.anyio
async def test_hackernews_collector(monkeypatch) -> None:
    async def mock_get(self, url, **kwargs):
        request = httpx.Request("GET", url)

        return httpx.Response(
            200,
            request=request,
            json={
                "hits": [
                    {
                        "title": "Salesforce Engineering Interview",
                        "objectID": "12345",
                        "url": "https://example.com/salesforce-interview",
                    }
                ]
            },
        )

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    collector = HackerNewsCollector()

    results = await collector.collect(
        company="Salesforce",
        role="Software Engineer Intern",
    )

    assert len(results) == 1
    assert results[0].source == "hackernews"
    assert results[0].title == "Salesforce Engineering Interview"
    assert str(results[0].url) == "https://example.com/salesforce-interview"
