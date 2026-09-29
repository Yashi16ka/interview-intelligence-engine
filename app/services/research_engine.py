from app.services.collectors.browser import BrowserPageCollector
from app.services.discovery_deduplicator import (
    deduplicate_discovered_sources,
)
from app.services.discovery_orchestrator import DiscoveryOrchestrator
from app.services.pipeline import ProcessedEvidence, process_sources
from app.services.search_queries import build_interview_queries


class ResearchEngine:
    def __init__(
        self,
        discovery: DiscoveryOrchestrator,
    ) -> None:
        self.discovery = discovery

    async def research(
        self,
        company: str,
        role: str,
    ) -> ProcessedEvidence:
        queries = build_interview_queries(
            company=company,
            role=role,
        )

        discovery_results = await self.discovery.discover(
            queries=queries,
        )

        discovered = deduplicate_discovered_sources(
            discovery_results.sources
        )

        urls = [
            str(source.url)
            for source in discovered
        ]

        collector = BrowserPageCollector(urls=urls)

        collected = await collector.collect(
            company=company,
            role=role,
        )

        return process_sources(
            results=collected,
            company=company,
            role=role,
        )
