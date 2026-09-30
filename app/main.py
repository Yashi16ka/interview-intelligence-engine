import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.research import router as research_router
from app.services.postgres_research_cache import (
    PostgresResearchCache,
)
from app.services.research_engine import ResearchEngine
from app.services.research_engine_factory import (
    build_research_engine,
)


DEFAULT_DATABASE_URL = (
    "postgresql://localhost/interview_intelligence"
)


def create_app(
    research_engine: ResearchEngine | None = None,
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(
        app: FastAPI,
    ) -> AsyncIterator[None]:
        cache: PostgresResearchCache | None = None

        if research_engine is None:
            database_url = os.getenv(
                "DATABASE_URL",
                DEFAULT_DATABASE_URL,
            )

            cache = PostgresResearchCache(
                database_url=database_url,
            )
            await cache.initialize()

            app.state.research_engine = (
                build_research_engine(
                    cache=cache,
                )
            )
        else:
            app.state.research_engine = research_engine

        try:
            yield
        finally:
            if cache is not None:
                await cache.close()

    app = FastAPI(
        title="Interview Intelligence Engine",
        version="0.1.0",
        lifespan=lifespan,
    )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "healthy"}

    app.include_router(research_router)

    return app


app = create_app()
