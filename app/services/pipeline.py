from dataclasses import dataclass

from app.models.evidence import EvidenceItem
from app.models.source import SourceResult
from app.services.deduplicator import (
    canonicalize_url,
    deduplicate_sources,
    title_key,
)
from app.services.normalizer import normalize_source, normalize_sources
from app.services.purpose_relevance import ScoredEvidence, rank_evidence
from app.services.relevance import ScoredSource, rank_sources


@dataclass
class ProcessingStats:
    raw_count: int
    normalized_count: int
    unique_count: int
    relevant_count: int


@dataclass
class ProcessedEvidence:
    evidence: list[ScoredSource]
    stats: ProcessingStats


def process_sources(
    results: list[SourceResult],
    company: str,
    role: str,
    minimum_score: int = 8,
) -> ProcessedEvidence:
    raw_count = len(results)

    normalized = normalize_sources(results)
    normalized_count = len(normalized)

    unique = deduplicate_sources(normalized)
    unique_count = len(unique)

    ranked = rank_sources(
        results=unique,
        company=company,
        role=role,
        minimum_score=minimum_score,
    )

    return ProcessedEvidence(
        evidence=ranked,
        stats=ProcessingStats(
            raw_count=raw_count,
            normalized_count=normalized_count,
            unique_count=unique_count,
            relevant_count=len(ranked),
        ),
    )


@dataclass
class ProcessedPurposeEvidence:
    evidence: list[ScoredEvidence]
    stats: ProcessingStats


def normalize_evidence(
    evidence: list[EvidenceItem],
) -> list[EvidenceItem]:
    return [
        EvidenceItem(
            result=normalize_source(item.result),
            purpose=item.purpose.strip(),
            provider=item.provider.strip().lower(),
        )
        for item in evidence
    ]


def deduplicate_evidence(
    evidence: list[EvidenceItem],
) -> list[EvidenceItem]:
    unique_evidence: list[EvidenceItem] = []

    seen_urls: set[tuple[str, str]] = set()
    seen_titles: set[tuple[str, str]] = set()

    for item in evidence:
        purpose = item.purpose
        url_key = canonicalize_url(str(item.result.url))
        normalized_title = title_key(item.result.title)

        purpose_url_key = (purpose, url_key)
        purpose_title_key = (
            purpose,
            normalized_title,
        )

        if purpose_url_key in seen_urls:
            continue

        if (
            normalized_title
            and purpose_title_key in seen_titles
        ):
            continue

        seen_urls.add(purpose_url_key)

        if normalized_title:
            seen_titles.add(purpose_title_key)

        unique_evidence.append(item)

    return unique_evidence


def process_evidence(
    evidence: list[EvidenceItem],
    company: str,
    role: str,
) -> ProcessedPurposeEvidence:
    raw_count = len(evidence)

    normalized = normalize_evidence(evidence)
    normalized_count = len(normalized)

    unique = deduplicate_evidence(normalized)
    unique_count = len(unique)

    ranked = rank_evidence(
        evidence=unique,
        company=company,
        role=role,
    )

    return ProcessedPurposeEvidence(
        evidence=ranked,
        stats=ProcessingStats(
            raw_count=raw_count,
            normalized_count=normalized_count,
            unique_count=unique_count,
            relevant_count=len(ranked),
        ),
    )
