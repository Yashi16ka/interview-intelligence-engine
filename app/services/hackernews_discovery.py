import asyncio

import httpx

from app.models.discovery import DiscoveredSource
from app.services.discovery import DiscoveryProvider
from app.services.search_queries import SearchQuery


class HackerNewsDiscoveryProvider(DiscoveryProvider):
    BASE_URL = "https://hn.algolia.com/api/v1/search"

    def __init__(
        self,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.client = client

    @property
    def name(self) -> str:
        return "hackernews"

    def _build_provider_query(
        self,
        query: SearchQuery,
    ) -> str | None:
        if query.purpose == "role_requirements":
            return None

        if not query.company:
            return query.query

        if query.purpose == "interview_experience":
            return f"{query.company} interview"

        if query.purpose == "interview_questions":
            return f"{query.company} interview questions"

        if query.purpose == "technical_interview":
            if query.role:
                return (
                    f"{query.company} "
                    f"{query.role} interview"
                )

            return f"{query.company} technical interview"

        if query.purpose == "company_engineering":
            return f"{query.company} engineering"

        return query.query

    async def _discover_query(
        self,
        query: SearchQuery,
        client: httpx.AsyncClient,
    ) -> list[DiscoveredSource]:
        provider_query = self._build_provider_query(query)

        if provider_query is None:
            return []

        response = await client.get(
            self.BASE_URL,
            params={
                "query": provider_query,
                "tags": "story",
                "hitsPerPage": 10,
            },
        )
        response.raise_for_status()

        data = response.json()
        sources: list[DiscoveredSource] = []

        for hit in data.get("hits", []):
            object_id = hit.get("objectID")
            title = hit.get("title")

            if not object_id or not title:
                continue

            story_text = hit.get("story_text")

            if query.company:
                if not story_text:
                    continue

                if (
                    query.company.casefold()
                    not in story_text.casefold()
                ):
                    continue

            url = hit.get("url")

            if not url:
                url = (
                    "https://news.ycombinator.com/"
                    f"item?id={object_id}"
                )

            sources.append(
                DiscoveredSource(
                    title=title,
                    url=url,
                    purpose=query.purpose,
                    provider=self.name,
                )
            )

        return sources

    async def discover(
        self,
        queries: list[SearchQuery],
    ) -> list[DiscoveredSource]:
        owns_client = self.client is None

        client = self.client or httpx.AsyncClient(
            timeout=10.0,
            follow_redirects=True,
        )

        try:
            results = await asyncio.gather(
                *[
                    self._discover_query(
                        query=query,
                        client=client,
                    )
                    for query in queries
                ]
            )
        finally:
            if owns_client:
                await client.aclose()

        return [
            source
            for query_results in results
            for source in query_results
        ]
