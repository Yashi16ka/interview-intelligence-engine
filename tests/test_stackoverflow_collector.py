import httpx
import pytest

from app.services.collectors.stackoverflow import StackOverflowCollector


@pytest.mark.anyio
async def test_stackoverflow_collector(monkeypatch) -> None:
    async def mock_get(self, url, **kwargs):
        request = httpx.Request("GET", url)

        return httpx.Response(
            200,
            request=request,
            json={
                "items": [
                    {
                        "title": "Salesforce API design question",
                        "link": "https://stackoverflow.com/questions/12345/example",
                        "tags": [
                            "salesforce",
                            "rest",
                            "api",
                        ],
                    }
                ]
            },
        )

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    collector = StackOverflowCollector()

    results = await collector.collect(
        company="Salesforce",
        role="Software Engineer",
    )

    assert len(results) == 1

    result = results[0]

    assert result.source == "stackoverflow"
    assert result.title == "Salesforce API design question"
    assert "salesforce" in result.content
    assert "rest" in result.content
    assert str(result.url) == (
        "https://stackoverflow.com/questions/12345/example"
    )
