from app.models.browser import BrowserFetchResult
from app.models.discovery import DiscoveredTarget
from app.models.evidence import EvidenceItem
from app.services.deduplicator import canonicalize_url


def build_evidence_items(
    discovered: list[DiscoveredTarget],
    fetched: list[BrowserFetchResult],
) -> list[EvidenceItem]:
    discovery_by_url = {
        canonicalize_url(str(target.url)): target
        for target in discovered
    }

    evidence: list[EvidenceItem] = []

    for item in fetched:
        requested_url = canonicalize_url(
            str(item.requested_url)
        )

        target = discovery_by_url.get(requested_url)

        if target is None:
            continue

        provider = ",".join(target.providers)

        for purpose in target.purposes:
            evidence.append(
                EvidenceItem(
                    result=item.result,
                    purpose=purpose,
                    provider=provider,
                )
            )

    return evidence
