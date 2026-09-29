import pytest

from app.models.discovery import DiscoveredSource
from app.services.discovery import DiscoveryProvider
from app.services.search_queries import SearchQuery


class FakeDiscoveryProvider(DiscoveryProvider):
    @property
    def name(self) -> str:
        return "fake"

    async def discover(
        self,
        queries: list[SearchQuery],
    ) -> list[DiscoveredSource]:
        return [
            DiscoveredSource(
                title=query.query,
                url=f"https://example.com/{index}",
                purpose=query.purpose,
                provider=self.name,
            )
            for index, query in enumerate(
                queries,
                start=1,
            )
        ]


@pytest.mark.anyio
async def test_discovery_provider() -> None:
    provider = FakeDiscoveryProvider()

    queries = [
        SearchQuery(
            purpose="interview_experience",
            query='"Example" "Software Engineer" interview experience',
        ),
        SearchQuery(
            purpose="interview_questions",
            query='"Example" "Software Engineer" interview questions',
        ),
    ]

    results = await provider.discover(queries)

    assert len(results) == 2

    assert results[0].purpose == "interview_experience"
    assert results[0].provider == "fake"

    assert results[1].purpose == "interview_questions"
    assert results[1].provider == "fake"
