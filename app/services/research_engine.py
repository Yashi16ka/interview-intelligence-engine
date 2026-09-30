import asyncio
from typing import Protocol

from app.models.evidence import EvidenceItem
from app.services.collectors.browser import BrowserPageCollector
from app.services.discovery_deduplicator import (
    deduplicate_discovered_sources,
)
from app.services.discovery_orchestrator import DiscoveryOrchestrator
from app.services.evidence_builder import build_evidence_items
from app.services.pipeline import ProcessedPurposeEvidence, process_evidence
from app.services.search_queries import SearchQuery, build_interview_queries


class ATSDiscovery(Protocol):
    async def collect_evidence(
        self,
        company: str,
        queries: list[SearchQuery],
    ) -> list[EvidenceItem]:
        ...


class ResearchEngine:
    def __init__(
        self,
        discovery: DiscoveryOrchestrator,
        ats: ATSDiscovery | None = None,
    ) -> None:
        self.discovery = discovery
        self.ats = ats

    async def collect_evidence(
        self,
        company: str,
        role: str,
    ) -> list[EvidenceItem]:
        queries = build_interview_queries(
            company=company,
            role=role,
        )

        if self.ats is None:
            discovery_result = await self.discovery.discover(
                queries=queries,
            )
            ats_evidence: list[EvidenceItem] = []
        else:
            discovery_result, ats_result = await asyncio.gather(
                self.discovery.discover(
                    queries=queries,
                ),
                self.ats.collect_evidence(
                    company=company,
                    queries=queries,
                ),
                return_exceptions=True,
            )

            if isinstance(discovery_result, Exception):
                discovered_sources = []
            else:
                discovered_sources = discovery_result.sources

            if isinstance(ats_result, Exception):
                ats_evidence = []
            else:
                ats_evidence = ats_result

        if self.ats is None:
            discovered_sources = discovery_result.sources

        discovered = deduplicate_discovered_sources(
            discovered_sources
        )

        urls = [
            str(source.url)
            for source in discovered
        ]

        collector = BrowserPageCollector(
            urls=urls,
        )

        fetched = await collector.collect_with_metadata()

        browser_evidence = build_evidence_items(
            discovered=discovered,
            fetched=fetched,
        )

        return [
            *browser_evidence,
            *ats_evidence,
        ]

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
