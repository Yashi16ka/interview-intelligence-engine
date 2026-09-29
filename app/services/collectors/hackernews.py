import asyncio

import httpx

from app.models.source import SourceResult
from app.services.collectors.base import BaseCollector


class HackerNewsCollector(BaseCollector):
    BASE_URL = "https://hn.algolia.com/api/v1/search"

    @property
    def name(self) -> str:
        return "hackernews"

    async def _search(
        self,
        client: httpx.AsyncClient,
        query: str,
        tag: str,
    ) -> list[SourceResult]:
        response = await client.get(
            self.BASE_URL,
            params={
                "query": query,
                "tags": tag,
                "hitsPerPage": 10,
            },
        )
        response.raise_for_status()

        data = response.json()
        results: list[SourceResult] = []

        for hit in data.get("hits", []):
            object_id = hit.get("objectID")

            if not object_id:
                continue

            if tag == "comment":
                title = (
                    hit.get("story_title")
                    or "Hacker News discussion"
                )
                content = (
                    hit.get("comment_text")
                    or title
                )
                story_id = hit.get("story_id")

                source_url = (
                    f"https://news.ycombinator.com/item?id={story_id}"
                    if story_id
                    else f"https://news.ycombinator.com/item?id={object_id}"
                )
            else:
                title = hit.get("title")

                if not title:
                    continue

                content = hit.get("story_text") or title
                source_url = (
                    hit.get("url")
                    or f"https://news.ycombinator.com/item?id={object_id}"
                )

            results.append(
                SourceResult(
                    source=self.name,
                    title=title,
                    url=source_url,
                    content=content,
                )
            )

        return results

    async def collect(
        self,
        company: str,
        role: str,
    ) -> list[SourceResult]:
        query = f"{company} {role} interview"

        async with httpx.AsyncClient(timeout=10.0) as client:
            stories, comments = await asyncio.gather(
                self._search(
                    client=client,
                    query=query,
                    tag="story",
                ),
                self._search(
                    client=client,
                    query=query,
                    tag="comment",
                ),
            )

        return stories + comments
