from datetime import timedelta

import asyncpg
import pytest

from app.models.evidence import EvidenceItem
from app.models.source import SourceResult
from app.services.postgres_research_cache import (
    PostgresResearchCache,
)


DATABASE_URL = (
    "postgresql://localhost/interview_intelligence"
)


def build_evidence() -> list[EvidenceItem]:
    return [
        EvidenceItem(
            result=SourceResult(
                source="test",
                title="Software Engineer",
                url="https://example.com/job",
                content=(
                    "Example Software Engineer requirements "
                    "include Python and PostgreSQL."
                ),
            ),
            purpose="role_requirements",
            provider="test_provider",
        )
    ]


@pytest.fixture
async def cache() -> PostgresResearchCache:
    cache = PostgresResearchCache(
        database_url=DATABASE_URL,
        ttl=timedelta(hours=1),
    )

    await cache.initialize()
    await cache.clear()

    yield cache

    await cache.clear()
    await cache.close()


@pytest.mark.anyio
async def test_postgres_cache_round_trip(
    cache: PostgresResearchCache,
) -> None:
    evidence = build_evidence()

    await cache.set(
        company="Example",
        role="Software Engineer",
        evidence=evidence,
    )

    cached = await cache.get(
        company="Example",
        role="Software Engineer",
    )

    assert cached is not None
    assert len(cached) == 1
    assert cached[0] == evidence[0]


@pytest.mark.anyio
async def test_postgres_cache_normalizes_key(
    cache: PostgresResearchCache,
) -> None:
    await cache.set(
        company=" Example ",
        role="Software   Engineer",
        evidence=build_evidence(),
    )

    cached = await cache.get(
        company="example",
        role=" software engineer ",
    )

    assert cached is not None
    assert len(cached) == 1


@pytest.mark.anyio
async def test_postgres_cache_expires_entries() -> None:
    cache = PostgresResearchCache(
        database_url=DATABASE_URL,
        ttl=timedelta(seconds=-1),
    )

    await cache.initialize()
    await cache.clear()

    try:
        await cache.set(
            company="Example",
            role="Software Engineer",
            evidence=build_evidence(),
        )

        cached = await cache.get(
            company="Example",
            role="Software Engineer",
        )

        assert cached is None
    finally:
        await cache.clear()
        await cache.close()


@pytest.mark.anyio
async def test_postgres_cache_stores_jsonb() -> None:
    cache = PostgresResearchCache(
        database_url=DATABASE_URL,
        ttl=timedelta(hours=1),
    )

    await cache.initialize()
    await cache.clear()

    try:
        await cache.set(
            company="Example",
            role="Software Engineer",
            evidence=build_evidence(),
        )

        connection = await asyncpg.connect(
            DATABASE_URL
        )

        try:
            data_type = await connection.fetchval(
                """
                SELECT data_type
                FROM information_schema.columns
                WHERE table_name = 'research_cache'
                  AND column_name = 'evidence'
                """
            )
        finally:
            await connection.close()

        assert data_type == "jsonb"
    finally:
        await cache.clear()
        await cache.close()
