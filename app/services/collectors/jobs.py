import httpx

from app.models.source import SourceResult
from app.services.collectors.base import BaseCollector


class JobsCollector(BaseCollector):
    BASE_URL = "https://remotive.com/api/remote-jobs"

    @property
    def name(self) -> str:
        return "jobs"

    async def collect(
        self,
        company: str,
        role: str,
    ) -> list[SourceResult]:
        async with httpx.AsyncClient(
            timeout=10.0,
            follow_redirects=True,
        ) as client:
            response = await client.get(
                self.BASE_URL,
                params={"search": role},
            )
            response.raise_for_status()

        data = response.json()

        results: list[SourceResult] = []

        for job in data.get("jobs", []):
            job_company = job.get("company_name", "")
            title = job.get("title")
            url = job.get("url")
            description = job.get("description", "")

            if not title or not url:
                continue

            if company.lower() not in job_company.lower():
                continue

            results.append(
                SourceResult(
                    source=self.name,
                    title=title,
                    url=url,
                    content=description or title,
                )
            )

        return results[:10]
