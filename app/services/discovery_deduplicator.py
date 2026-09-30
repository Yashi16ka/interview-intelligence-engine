from app.models.discovery import (
    DiscoveredSource,
    DiscoveredTarget,
)
from app.services.deduplicator import canonicalize_url


def deduplicate_discovered_sources(
    sources: list[DiscoveredSource],
) -> list[DiscoveredTarget]:
    targets_by_url: dict[str, DiscoveredTarget] = {}

    for source in sources:
        url_key = canonicalize_url(str(source.url))

        existing = targets_by_url.get(url_key)

        if existing is None:
            targets_by_url[url_key] = DiscoveredTarget(
                title=source.title,
                url=source.url,
                purposes=[source.purpose],
                providers=[source.provider],
            )
            continue

        if source.purpose not in existing.purposes:
            existing.purposes.append(source.purpose)

        if source.provider not in existing.providers:
            existing.providers.append(source.provider)

    return list(targets_by_url.values())
