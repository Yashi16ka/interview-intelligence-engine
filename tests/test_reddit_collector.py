import httpx
import pytest

from app.services.collectors.reddit import RedditCollector


@pytest.mark.anyio
async def test_reddit_collector(monkeypatch) -> None:
    async def mock_get(self, url, **kwargs):
        request = httpx.Request("GET", url)

        return httpx.Response(
            200,
            request=request,
            json={
                "data": {
                    "children": [
                        {
                            "data": {
                                "title": "Salesforce SWE Intern Interview",
                                "selftext": (
                                    "I was asked about arrays, graphs, "
                                    "and object-oriented design."
                                ),
                                "permalink": (
                                    "/r/csMajors/comments/abc123/"
                                    "salesforce_interview/"
                                ),
                            }
                        }
                    ]
                }
            },
        )

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    collector = RedditCollector()

    results = await collector.collect(
        company="Salesforce",
        role="Software Engineer Intern",
    )

    assert len(results) == 1

    result = results[0]

    assert result.source == "reddit"
    assert result.title == "Salesforce SWE Intern Interview"
    assert "arrays" in result.content
    assert "graphs" in result.content
    assert str(result.url).startswith("https://www.reddit.com/")
