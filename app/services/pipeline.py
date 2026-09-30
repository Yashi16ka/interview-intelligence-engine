from dataclasses import dataclass

from app.models.evidence import EvidenceItem
from app.models.source import SourceResult
from app.services.deduplicator import deduplicate_sources
from app.services.normalizer import normalize_sources
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


def process_evidence(
    evidence: list[EvidenceItem],
    company: str,
    role: str,
) -> ProcessedPurposeEvidence:
    raw_count = len(evidence)

    ranked = rank_evidence(
        evidence=evidence,
        company=company,
        role=role,
    )

    return ProcessedPurposeEvidence(
        evidence=ranked,
        stats=ProcessingStats(
            raw_count=raw_count,
            normalized_count=raw_count,
            unique_count=raw_count,
            relevant_count=len(ranked),
        ),
    )
