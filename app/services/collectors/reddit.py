import httpx

from app.models.source import SourceResult
from app.services.collectors.base import BaseCollector


class RedditCollector(BaseCollector):
    BASE_URL = "https://www.reddit.com/search.json"

    @property
    def name(self) -> str:
        return "reddit"

    async def collect(
        self,
        company: str,
        role: str,
    ) -> list[SourceResult]:
        query = f'"{company}" "{role}" interview'

        headers = {
            "User-Agent": (
                "InterviewIntelligenceEngine/0.1 "
                "(educational project)"
            )
        }

        async with httpx.AsyncClient(
            timeout=10.0,
            headers=headers,
            follow_redirects=True,
        ) as client:
            response = await client.get(
                self.BASE_URL,
                params={
                    "q": query,
                    "limit": 10,
                    "sort": "relevance",
                    "type": "link",
                },
            )
            response.raise_for_status()

        data = response.json()

        results: list[SourceResult] = []

        children = data.get("data", {}).get("children", [])

        for child in children:
            post = child.get("data", {})

            title = post.get("title")
            permalink = post.get("permalink")

            if not title or not permalink:
                continue

            selftext = post.get("selftext", "").strip()

            content = title

            if selftext:
                content = f"{title}\n\n{selftext}"

            results.append(
                SourceResult(
                    source=self.name,
                    title=title,
                    url=f"https://www.reddit.com{permalink}",
                    content=content,
                )
            )

        return results
