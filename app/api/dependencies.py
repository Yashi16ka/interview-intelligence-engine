from fastapi import Request

from app.services.intelligence_synthesizer import (
    IntelligenceSynthesizer,
)
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

def get_intelligence_synthesizer(
    request: Request,
) -> IntelligenceSynthesizer:
    synthesizer = getattr(
        request.app.state,
        "intelligence_synthesizer",
        None,
    )

    if synthesizer is None:
        raise RuntimeError(
            "Intelligence synthesizer has not been initialized."
        )

    return synthesizer

