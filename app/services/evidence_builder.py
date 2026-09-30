from app.models.browser import BrowserFetchResult
from app.models.discovery import DiscoveredSource
from app.models.evidence import EvidenceItem
from app.services.deduplicator import canonicalize_url


def build_evidence_items(
    discovered: list[DiscoveredSource],
    fetched: list[BrowserFetchResult],
) -> list[EvidenceItem]:
    discovery_by_url = {
        canonicalize_url(str(source.url)): source
        for source in discovered
    }

    evidence: list[EvidenceItem] = []

    for item in fetched:
        requested_url = canonicalize_url(
            str(item.requested_url)
        )

        source = discovery_by_url.get(requested_url)

        if source is None:
            continue

        evidence.append(
            EvidenceItem(
                result=item.result,
                purpose=source.purpose,
                provider=source.provider,
            )
        )

    return evidence
