import asyncio

from app.models.source import CollectorError, ResearchResults
from app.services.collectors.base import BaseCollector


class ResearchOrchestrator:
    def __init__(self, collectors: list[BaseCollector]) -> None:
        self.collectors = collectors

    async def research_sequential(
        self,
        company: str,
        role: str,
    ) -> ResearchResults:
        results = []
        errors = []

        for collector in self.collectors:
            try:
                collector_results = await collector.collect(company, role)
                results.extend(collector_results)
            except Exception as exc:
                errors.append(
                    CollectorError(
                        source=collector.name,
                        error_type=type(exc).__name__,
                        message=str(exc),
                    )
                )

        return ResearchResults(
            results=results,
            errors=errors,
        )

    async def research(
        self,
        company: str,
        role: str,
    ) -> ResearchResults:
        tasks = [
            collector.collect(company, role)
            for collector in self.collectors
        ]

        outcomes = await asyncio.gather(
            *tasks,
            return_exceptions=True,
        )

        results = []
        errors = []

        for collector, outcome in zip(
            self.collectors,
            outcomes,
            strict=True,
        ):
            if isinstance(outcome, BaseException):
                errors.append(
                    CollectorError(
                        source=collector.name,
                        error_type=type(outcome).__name__,
                        message=str(outcome),
                    )
                )
            else:
                results.extend(outcome)

        return ResearchResults(
            results=results,
            errors=errors,
        )
