import hashlib
from typing import Protocol

from app.models.evidence import EvidenceItem


def normalize_cache_component(value: str) -> str:
    return " ".join(
        value.lower().strip().split()
    )


def build_research_cache_key(
    company: str,
    role: str,
) -> str:
    normalized_company = normalize_cache_component(
        company
    )
    normalized_role = normalize_cache_component(
        role
    )

    raw_key = (
        f"{normalized_company}:{normalized_role}"
    )

    return hashlib.sha256(
        raw_key.encode("utf-8")
    ).hexdigest()


class ResearchCache(Protocol):
    async def get(
        self,
        company: str,
        role: str,
    ) -> list[EvidenceItem] | None:
        ...

    async def set(
        self,
        company: str,
        role: str,
        evidence: list[EvidenceItem],
    ) -> None:
        ...
