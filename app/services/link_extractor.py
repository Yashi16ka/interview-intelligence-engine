from dataclasses import dataclass
from urllib.parse import urljoin, urlsplit


@dataclass(frozen=True)
class DiscoveredLink:
    title: str
    url: str


def normalize_link(
    base_url: str,
    href: str,
) -> str | None:
    href = href.strip()

    if not href:
        return None

    if href.startswith(("#", "mailto:", "tel:", "javascript:")):
        return None

    absolute = urljoin(base_url, href)
    parts = urlsplit(absolute)

    if parts.scheme not in {"http", "https"}:
        return None

    return absolute


def is_same_domain(
    first_url: str,
    second_url: str,
) -> bool:
    first = urlsplit(first_url).netloc.lower()
    second = urlsplit(second_url).netloc.lower()

    first = first.removeprefix("www.")
    second = second.removeprefix("www.")

    return first == second
