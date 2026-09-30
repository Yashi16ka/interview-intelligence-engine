from app.models.evidence import EvidenceItem
from app.services.collectors.browser import BrowserPageCollector
from app.services.discovery_deduplicator import (
    deduplicate_discovered_sources,
)
from app.services.discovery_orchestrator import DiscoveryOrchestrator
from app.services.evidence_builder import build_evidence_items
from app.services.pipeline import ProcessedPurposeEvidence, process_evidence
from app.services.search_queries import build_interview_queries


class ResearchEngine:
    def __init__(
        self,
        discovery: DiscoveryOrchestrator,
    ) -> None:
        self.discovery = discovery

    async def collect_evidence(
        self,
        company: str,
        role: str,
    ) -> list[EvidenceItem]:
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

        fetched = await collector.collect_with_metadata()

        return build_evidence_items(
            discovered=discovered,
            fetched=fetched,
        )

    async def research(
        self,
        company: str,
        role: str,
    ) -> ProcessedPurposeEvidence:
        evidence = await self.collect_evidence(
            company=company,
            role=role,
        )

        return process_evidence(
            evidence=evidence,
            company=company,
            role=role,
        )
