import httpx

from app.models.source import SourceResult
from app.services.collectors.base import BaseCollector


class HackerNewsCollector(BaseCollector):
    BASE_URL = "https://hn.algolia.com/api/v1/search"

    @property
    def name(self) -> str:
        return "hackernews"

    async def collect(
        self,
        company: str,
        role: str,
    ) -> list[SourceResult]:
        query = f"{company} {role}"

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                self.BASE_URL,
                params={
                    "query": query,
                    "tags": "story",
                    "hitsPerPage": 10,
                },
            )
            response.raise_for_status()

        data = response.json()

        results: list[SourceResult] = []

        for hit in data.get("hits", []):
            title = hit.get("title")
            object_id = hit.get("objectID")

            if not title or not object_id:
                continue

            source_url = (
                hit.get("url")
                or f"https://news.ycombinator.com/item?id={object_id}"
            )

            results.append(
                SourceResult(
                    source=self.name,
                    title=title,
                    url=source_url,
                    content=title,
                )
            )

        return results
