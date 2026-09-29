import asyncio

from app.services.collectors.hackernews import HackerNewsCollector
from app.services.collectors.stackoverflow import StackOverflowCollector
from app.services.orchestrator import ResearchOrchestrator
from app.services.pipeline import process_sources
from app.services.relevance import score_source


async def main() -> None:
    company = "Salesforce"
    role = "Software Engineer Intern"

    orchestrator = ResearchOrchestrator(
        collectors=[
            HackerNewsCollector(),
            StackOverflowCollector(),
        ]
    )

    research = await orchestrator.research(
        company=company,
        role=role,
    )

    print("RAW RETRIEVAL")
    print("=" * 70)

    for index, result in enumerate(
        research.results,
        start=1,
    ):
        scored = score_source(
            result=result,
            company=company,
            role=role,
        )

        print()
        print(f"{index}. [{result.source}] {result.title}")
        print(f"   Score: {scored.score}")
        print(
            "   Matched:",
            ", ".join(scored.matched_terms) or "none",
        )
        print(f"   URL: {result.url}")

    if research.errors:
        print()
        print("COLLECTOR ERRORS")
        print("=" * 70)

        for error in research.errors:
            print(
                f"{error.source}: "
                f"{error.error_type} - {error.message}"
            )

    processed = process_sources(
        results=research.results,
        company=company,
        role=role,
    )

    print()
    print("PIPELINE")
    print("=" * 70)
    print(f"Raw:        {processed.stats.raw_count}")
    print(f"Normalized: {processed.stats.normalized_count}")
    print(f"Unique:     {processed.stats.unique_count}")
    print(f"Relevant:   {processed.stats.relevant_count}")


if __name__ == "__main__":
    asyncio.run(main())
