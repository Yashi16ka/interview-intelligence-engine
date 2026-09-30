from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_research_engine
from app.models.research import (
    ResearchEvidenceResponse,
    ResearchRequest,
    ResearchResponse,
    ResearchStatsResponse,
)
from app.services.research_engine import ResearchEngine


router = APIRouter(
    prefix="/research",
    tags=["research"],
)


@router.post(
    "",
    response_model=ResearchResponse,
)
async def research_interview(
    request: ResearchRequest,
    engine: Annotated[
        ResearchEngine,
        Depends(get_research_engine),
    ],
) -> ResearchResponse:
    result = await engine.research(
        company=request.company,
        role=request.role,
    )

    evidence = [
        ResearchEvidenceResponse(
            source=item.evidence.result.source,
            title=item.evidence.result.title,
            url=item.evidence.result.url,
            purpose=item.evidence.purpose,
            provider=item.evidence.provider,
            score=item.score,
            matched_terms=item.matched_terms,
        )
        for item in result.evidence
    ]

    return ResearchResponse(
        company=request.company,
        role=request.role,
        status="completed",
        stats=ResearchStatsResponse(
            raw_count=result.stats.raw_count,
            normalized_count=(
                result.stats.normalized_count
            ),
            unique_count=result.stats.unique_count,
            relevant_count=(
                result.stats.relevant_count
            ),
        ),
        evidence=evidence,
    )
