from fastapi import Request

from app.services.research_engine import ResearchEngine


def get_research_engine(
    request: Request,
) -> ResearchEngine:
    engine = getattr(
        request.app.state,
        "research_engine",
        None,
    )

    if engine is None:
        raise RuntimeError(
            "Research engine has not been initialized."
        )

    return engine
