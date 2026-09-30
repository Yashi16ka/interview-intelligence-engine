import httpx

from app.models.ats import ATSCandidate
from app.models.discovery import DiscoveredSource
from app.services.discovery import DiscoveryProvider
from app.services.role_matching import extract_role_terms, matches_role
from app.services.search_queries import SearchQuery


class AshbyDiscoveryProvider(DiscoveryProvider):
    BASE_URL = "https://api.ashbyhq.com/posting-api/job-board"

    def __init__(
        self,
        candidate: ATSCandidate,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.candidate = candidate
        self.client = client

    @property
    def name(self) -> str:
        return "ashby"

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
            )
            response.raise_for_status()

            data = response.json()
        finally:
            if owns_client:
                await client.aclose()

        if not isinstance(data, dict):
            return []

        jobs = data.get("jobs")

        if not isinstance(jobs, list):
            return []

        results: list[DiscoveredSource] = []
        seen_urls: set[str] = set()

        for query in role_queries:
            role_terms = extract_role_terms(
                query.query
            )

            for job in jobs:
                if not isinstance(job, dict):
                    continue

                title = job.get("title")
                url = job.get("jobUrl")

                if not title or not url:
                    continue

                if not matches_role(
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
