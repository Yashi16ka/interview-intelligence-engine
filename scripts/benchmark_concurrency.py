import asyncio
import statistics
import time

from app.models.source import SourceResult
from app.services.collectors.base import BaseCollector
from app.services.orchestrator import ResearchOrchestrator


class BenchmarkCollector(BaseCollector):
    def __init__(self, collector_name: str, delay: float) -> None:
        self.collector_name = collector_name
        self.delay = delay

    @property
    def name(self) -> str:
        return self.collector_name

    async def collect(
        self,
        company: str,
        role: str,
    ) -> list[SourceResult]:
        await asyncio.sleep(self.delay)

        return [
            SourceResult(
                source=self.name,
                title=f"{self.name} result",
                url=f"https://example.com/{self.name}",
                content="Benchmark result",
            )
        ]


async def measure(operation, runs: int = 5) -> list[float]:
    durations = []

    for _ in range(runs):
        start = time.perf_counter()

        await operation(
            company="Salesforce",
            role="Software Engineer Intern",
        )

        durations.append(time.perf_counter() - start)

    return durations


async def main() -> None:
    orchestrator = ResearchOrchestrator(
        collectors=[
            BenchmarkCollector("source-a", 0.30),
            BenchmarkCollector("source-b", 0.40),
            BenchmarkCollector("source-c", 0.50),
        ]
    )

    sequential = await measure(orchestrator.research_sequential)
    concurrent = await measure(orchestrator.research)

    sequential_median = statistics.median(sequential)
    concurrent_median = statistics.median(concurrent)

    reduction = (
        (sequential_median - concurrent_median)
        / sequential_median
        * 100
    )

    print("Sequential runs:")
    for duration in sequential:
        print(f"  {duration:.3f}s")

    print()

    print("Concurrent runs:")
    for duration in concurrent:
        print(f"  {duration:.3f}s")

    print()

    print(f"Sequential median: {sequential_median:.3f}s")
    print(f"Concurrent median: {concurrent_median:.3f}s")
    print(f"Latency reduction: {reduction:.1f}%")


if __name__ == "__main__":
    asyncio.run(main())
