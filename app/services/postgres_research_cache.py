import json
from datetime import timedelta

import asyncpg

from app.models.evidence import EvidenceItem
from app.services.research_cache import (
    build_research_cache_key,
)


class PostgresResearchCache:
    def __init__(
        self,
        database_url: str,
        ttl: timedelta = timedelta(hours=24),
    ) -> None:
        self.database_url = database_url
        self.ttl = ttl
        self.pool: asyncpg.Pool | None = None

    async def initialize(self) -> None:
        if self.pool is None:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=1,
                max_size=5,
            )

        await self.pool.execute(
            """
            CREATE TABLE IF NOT EXISTS research_cache (
                cache_key TEXT PRIMARY KEY,
                company TEXT NOT NULL,
                role TEXT NOT NULL,
                evidence JSONB NOT NULL,
                created_at TIMESTAMPTZ NOT NULL
                    DEFAULT NOW(),
                expires_at TIMESTAMPTZ NOT NULL
            )
            """
        )

        await self.pool.execute(
            """
            CREATE INDEX IF NOT EXISTS
                idx_research_cache_expires_at
            ON research_cache (expires_at)
            """
        )

    def _require_pool(self) -> asyncpg.Pool:
        if self.pool is None:
            raise RuntimeError(
                "PostgresResearchCache.initialize() "
                "must be called before use."
            )

        return self.pool

    async def get(
        self,
        company: str,
        role: str,
    ) -> list[EvidenceItem] | None:
        pool = self._require_pool()

        cache_key = build_research_cache_key(
            company=company,
            role=role,
        )

        row = await pool.fetchrow(
            """
            SELECT evidence
            FROM research_cache
            WHERE cache_key = $1
              AND expires_at > NOW()
            """,
            cache_key,
        )

        if row is None:
            return None

        payload = row["evidence"]

        if isinstance(payload, str):
            payload = json.loads(payload)

        return [
            EvidenceItem.model_validate(item)
            for item in payload
        ]

    async def set(
        self,
        company: str,
        role: str,
        evidence: list[EvidenceItem],
    ) -> None:
        pool = self._require_pool()

        cache_key = build_research_cache_key(
            company=company,
            role=role,
        )

        payload = json.dumps(
            [
                item.model_dump(mode="json")
                for item in evidence
            ]
        )

        await pool.execute(
            """
            INSERT INTO research_cache (
                cache_key,
                company,
                role,
                evidence,
                created_at,
                expires_at
            )
            VALUES (
                $1,
                $2,
                $3,
                $4::jsonb,
                NOW(),
                NOW() + $5::interval
            )
            ON CONFLICT (cache_key)
            DO UPDATE SET
                company = EXCLUDED.company,
                role = EXCLUDED.role,
                evidence = EXCLUDED.evidence,
                created_at = NOW(),
                expires_at = EXCLUDED.expires_at
            """,
            cache_key,
            company.strip(),
            role.strip(),
            payload,
            self.ttl,
        )

    async def clear(self) -> None:
        pool = self._require_pool()

        await pool.execute(
            "TRUNCATE TABLE research_cache"
        )

    async def close(self) -> None:
        if self.pool is not None:
            await self.pool.close()
            self.pool = None
