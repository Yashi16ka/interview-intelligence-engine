import asyncio
import time

from app.services.collectors.hackernews import HackerNewsCollector
from app.services.collectors.jobs import JobsCollector
from app.services.collectors.reddit import RedditCollector
from app.services.collectors.stackoverflow import StackOverflowCollector
from app.services.orchestrator import ResearchOrchestrator


async def measure(
    label: str,
    operation,
) -> None:
    start = time.perf_counter()

    research = await operation(
        company="Salesforce",
        role="Software Engineer Intern",
    )

    elapsed = time.perf_counter() - start

    print(f"{label}: {elapsed:.3f}s")
    print(f"  Results: {len(research.results)}")
    print(f"  Failures: {len(research.errors)}")

    counts: dict[str, int] = {}

    for result in research.results:
        counts[result.source] = counts.get(result.source, 0) + 1

    for source, count in counts.items():
        print(f"  {source}: {count}")

    for error in research.errors:
        print(
            f"  ERROR {error.source}: "
            f"{error.error_type}"
        )

    print()


async def main() -> None:
    orchestrator = ResearchOrchestrator(
        collectors=[
            HackerNewsCollector(),
            JobsCollector(),
            StackOverflowCollector(),
            RedditCollector(),
        ]
    )

    await measure(
        "Sequential",
        orchestrator.research_sequential,
    )

    await measure(
        "Concurrent",
        orchestrator.research,
    )


if __name__ == "__main__":
    asyncio.run(main())
