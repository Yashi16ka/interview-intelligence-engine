from app.services.ats_orchestrator import build_ats_orchestrator
from app.services.discovery_orchestrator import DiscoveryOrchestrator
from app.services.postgres_research_cache import PostgresResearchCache
from app.services.research_engine import ResearchEngine


def build_research_engine(
    cache: PostgresResearchCache,
) -> ResearchEngine:
    discovery = DiscoveryOrchestrator(
        providers=[],
    )

    ats = build_ats_orchestrator()

    return ResearchEngine(
        discovery=discovery,
        ats=ats,
        cache=cache,
    )
