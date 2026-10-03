import httpx

from app.models.ats import ATSCandidate
from app.models.discovery import DiscoveredSource
from app.models.evidence import EvidenceItem
from app.models.source import SourceResult
from app.services.discovery import DiscoveryProvider
from app.services.role_matching import matches_role_query
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

    async def _fetch_jobs(
        self,
    ) -> list[dict]:
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

        return [
            job
            for job in jobs
            if isinstance(job, dict)
        ]

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

        jobs = await self._fetch_jobs()

        results: list[DiscoveredSource] = []
        seen_urls: set[str] = set()

        for query in role_queries:
            for job in jobs:
                title = job.get("title")
                url = job.get("jobUrl")

                if not title or not url:
                    continue

                if not matches_role_query(
                    title=title,
                    role=query.role or query.query,
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

    async def collect_evidence(
        self,
        queries: list[SearchQuery],
    ) -> list[EvidenceItem]:
        role_queries = [
            query
            for query in queries
            if query.purpose == "role_requirements"
        ]

        if not role_queries:
            return []

        jobs = await self._fetch_jobs()

        evidence: list[EvidenceItem] = []
        seen_urls: set[str] = set()

        for query in role_queries:
            for job in jobs:
                title = job.get("title")
                url = job.get("jobUrl")
                content = job.get("descriptionPlain")

                if not title or not url or not content:
                    continue

                if not matches_role_query(
                    title=title,
                    role=query.role or query.query,
                ):
                    continue

                if url in seen_urls:
                    continue

                seen_urls.add(url)

                evidence.append(
                    EvidenceItem(
                        result=SourceResult(
                            source=self.name,
                            title=title,
                            url=url,
                            content=content,
                        ),
                        purpose=query.purpose,
                        provider=self.name,
                    )
                )

        return evidence
