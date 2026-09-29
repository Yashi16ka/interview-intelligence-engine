import asyncio

from app.models.source import SourceResult
from app.services.collectors.base import BaseCollector


class MockCollector(BaseCollector):
    @property
    def name(self) -> str:
        return "mock"

    async def collect(
        self,
        company: str,
        role: str,
    ) -> list[SourceResult]:
        await asyncio.sleep(0.01)

        return [
            SourceResult(
                source=self.name,
                title=f"{role} at {company}",
                url="https://example.com/interview",
                content=(
                    f"Example interview information for a "
                    f"{role} position at {company}."
                ),
            )
        ]
