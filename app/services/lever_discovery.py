import re

import httpx

from app.models.ats import ATSCandidate
from app.models.discovery import DiscoveredSource
from app.services.discovery import DiscoveryProvider
from app.services.search_queries import SearchQuery


class LeverDiscoveryProvider(DiscoveryProvider):
    BASE_URL = "https://api.lever.co/v0/postings"

    def __init__(
        self,
        candidate: ATSCandidate,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.candidate = candidate
        self.client = client

    @property
    def name(self) -> str:
        return "lever"

    def _extract_role_terms(
        self,
        query: str,
    ) -> set[str]:
        quoted_terms = re.findall(r'"([^"]+)"', query)

        if len(quoted_terms) >= 2:
            role = quoted_terms[1]
        else:
            role = query

        return {
            term.lower()
            for term in re.findall(r"[a-zA-Z0-9+#.]+", role)
            if len(term) > 2
        }

    def _matches_role(
        self,
        title: str,
        role_terms: set[str],
    ) -> bool:
        title_lower = title.lower()

        if not role_terms:
            return True

        matched = sum(
            term in title_lower
            for term in role_terms
        )

        return matched >= max(1, len(role_terms) // 2)

    async def discover(
        self,
        queries: list[SearchQuery],
    ) -> list[DiscoveredSource]:
        role_queries = [
            query
            for query in queries
            if query.purpose == "role_requirements"
        ]

        if not role_queries:
            return []

        owns_client = self.client is None

        client = self.client or httpx.AsyncClient(
            timeout=10.0,
            follow_redirects=True,
        )

        try:
            response = await client.get(
                f"{self.BASE_URL}/{self.candidate.slug}",
                params={"mode": "json"},
            )
            response.raise_for_status()

            jobs = response.json()
        finally:
            if owns_client:
                await client.aclose()

        results: list[DiscoveredSource] = []
        seen_urls: set[str] = set()

        for query in role_queries:
            role_terms = self._extract_role_terms(
                query.query
            )

            for job in jobs:
                title = job.get("text")
                url = job.get("hostedUrl")

                if not title or not url:
                    continue

                if not self._matches_role(
                    title=title,
                    role_terms=role_terms,
                ):
                    continue

                if url in seen_urls:
                    continue

                seen_urls.add(url)

                results.append(
                    DiscoveredSource(
                        title=title,
                        url=url,
                        purpose=query.purpose,
                        provider=self.name,
                    )
                )

        return results
