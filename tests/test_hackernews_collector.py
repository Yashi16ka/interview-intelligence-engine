import httpx
import pytest

from app.services.collectors.hackernews import HackerNewsCollector


@pytest.mark.anyio
async def test_hackernews_collector_searches_stories_and_comments(
    monkeypatch,
) -> None:
    requested_tags: list[str] = []

    async def mock_get(self, url, **kwargs):
        params = kwargs["params"]
        tag = params["tags"]
        requested_tags.append(tag)

        request = httpx.Request("GET", url)

        if tag == "story":
            payload = {
                "hits": [
                    {
                        "title": "Example Corp Engineering Interview",
                        "story_text": (
                            "Discussion about an Example Corp "
                            "technical interview."
                        ),
                        "objectID": "12345",
                        "url": "https://example.com/interview",
                    }
                ]
            }
        else:
            payload = {
                "hits": [
                    {
                        "story_title": "Hiring discussion",
                        "comment_text": (
                            "My Example Corp Backend Engineer "
                            "interview included a coding challenge."
                        ),
                        "story_id": "67890",
                        "objectID": "99999",
                    }
                ]
            }

        return httpx.Response(
            200,
            request=request,
            json=payload,
        )

    monkeypatch.setattr(
        httpx.AsyncClient,
        "get",
        mock_get,
    )

    collector = HackerNewsCollector()

    results = await collector.collect(
        company="Example Corp",
        role="Backend Engineer",
    )

    assert set(requested_tags) == {
        "story",
        "comment",
    }

    assert len(results) == 2

    story = results[0]
    comment = results[1]

    assert story.source == "hackernews"
    assert story.title == "Example Corp Engineering Interview"
    assert (
        str(story.url)
        == "https://example.com/interview"
    )

    assert comment.source == "hackernews"
    assert comment.title == "Hiring discussion"
    assert "coding challenge" in comment.content
    assert (
        str(comment.url)
        == "https://news.ycombinator.com/item?id=67890"
    )


@pytest.mark.anyio
async def test_hackernews_comment_falls_back_to_object_id(
    monkeypatch,
) -> None:
    async def mock_get(self, url, **kwargs):
        tag = kwargs["params"]["tags"]
        request = httpx.Request("GET", url)

        if tag == "story":
            payload = {"hits": []}
        else:
            payload = {
                "hits": [
                    {
                        "comment_text": "Interview discussion",
                        "objectID": "55555",
                    }
                ]
            }

        return httpx.Response(
            200,
            request=request,
            json=payload,
        )

    monkeypatch.setattr(
        httpx.AsyncClient,
        "get",
        mock_get,
    )

    collector = HackerNewsCollector()

    results = await collector.collect(
        company="Example Corp",
        role="Data Engineer",
    )

    assert len(results) == 1
    assert results[0].title == "Hacker News discussion"
    assert (
        str(results[0].url)
        == "https://news.ycombinator.com/item?id=55555"
    )
