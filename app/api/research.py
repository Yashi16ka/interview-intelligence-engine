from fastapi import APIRouter

from app.models.research import ResearchRequest, ResearchResponse


router = APIRouter(prefix="/research", tags=["research"])


@router.post("", response_model=ResearchResponse)
async def research_interview(request: ResearchRequest) -> ResearchResponse:
    return ResearchResponse(
        company=request.company,
        role=request.role,
        status="research_queued",
    )
