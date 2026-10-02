import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from app.api.research import router as research_router
from app.services.gemini_synthesizer import GeminiSynthesizer
from app.services.intelligence_synthesizer import (
    IntelligenceSynthesizer,
)
from app.services.unavailable_intelligence_synthesizer import (
    UnavailableIntelligenceSynthesizer,
)
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
    intelligence_synthesizer: IntelligenceSynthesizer | None = None,
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(
        app: FastAPI,
    ) -> AsyncIterator[None]:
        cache: PostgresResearchCache | None = None
        gemini_client: httpx.AsyncClient | None = None

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

        if intelligence_synthesizer is not None:
            app.state.intelligence_synthesizer = (
                intelligence_synthesizer
            )
        else:
            api_key = os.getenv("GEMINI_API_KEY")

            if not api_key:
                app.state.intelligence_synthesizer = (
                    UnavailableIntelligenceSynthesizer()
                )
            else:
                gemini_client = httpx.AsyncClient(
                    timeout=30.0,
                )

                app.state.intelligence_synthesizer = (
                    GeminiSynthesizer(
                        api_key=api_key,
                        client=gemini_client,
                    )
                )

        try:
            yield
        finally:
            if gemini_client is not None:
                await gemini_client.aclose()

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
