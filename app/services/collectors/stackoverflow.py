import httpx

from app.models.source import SourceResult
from app.services.collectors.base import BaseCollector


class StackOverflowCollector(BaseCollector):
    BASE_URL = "https://api.stackexchange.com/2.3/search/advanced"

    @property
    def name(self) -> str:
        return "stackoverflow"

    async def collect(
        self,
        company: str,
        role: str,
    ) -> list[SourceResult]:
        query = f"{company} {role}"

        async with httpx.AsyncClient(
            timeout=10.0,
            follow_redirects=True,
        ) as client:
            response = await client.get(
                self.BASE_URL,
                params={
                    "site": "stackoverflow",
                    "q": query,
                    "pagesize": 10,
                    "order": "desc",
                    "sort": "relevance",
                },
            )
            response.raise_for_status()

        data = response.json()

        results: list[SourceResult] = []

        for item in data.get("items", []):
            title = item.get("title")
            url = item.get("link")

            if not title or not url:
                continue

            tags = item.get("tags", [])
            tag_text = ", ".join(tags)

            content = title

            if tag_text:
                content = f"{title}\nTags: {tag_text}"

            results.append(
                SourceResult(
                    source=self.name,
                    title=title,
                    url=url,
                    content=content,
                )
            )

        return results
