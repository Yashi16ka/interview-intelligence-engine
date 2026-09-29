import html
import re

from app.models.source import SourceResult


def normalize_text(text: str) -> str:
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def normalize_source(result: SourceResult) -> SourceResult:
    return SourceResult(
        source=result.source.strip().lower(),
        title=normalize_text(result.title),
        url=result.url,
        content=normalize_text(result.content),
    )


def normalize_sources(
    results: list[SourceResult],
) -> list[SourceResult]:
    return [
        normalize_source(result)
        for result in results
    ]
