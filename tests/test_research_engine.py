import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from app.models.discovery import DiscoveredSource
from app.services.discovery import DiscoveryProvider
from app.services.discovery_orchestrator import DiscoveryOrchestrator
from app.services.research_engine import ResearchEngine
from app.services.search_queries import SearchQuery


class PageHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        body = (
            "<html>"
            "<head><title>Example Interview</title></head>"
            "<body>"
            "Example Software Engineer technical interview "
            "included a coding challenge and system design."
            "</body>"
            "</html>"
        ).encode()

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header(
            "Content-Length",
            str(len(body)),
        )
        self.end_headers()
        self.wfile.write(body)

    def log_message(
        self,
        format: str,
        *args: object,
    ) -> None:
        pass


class FakeDiscoveryProvider(DiscoveryProvider):
    def __init__(self, url: str) -> None:
        self.url = url

    @property
    def name(self) -> str:
        return "fake"

    async def discover(
        self,
        queries: list[SearchQuery],
    ) -> list[DiscoveredSource]:
        return [
            DiscoveredSource(
                title="Interview experience",
                url=self.url,
                purpose="interview_experience",
                provider=self.name,
            )
        ]


@pytest.mark.anyio
async def test_research_engine_end_to_end() -> None:
    server = HTTPServer(
        ("127.0.0.1", 0),
        PageHandler,
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )
    thread.start()

    try:
        host, port = server.server_address
        url = f"http://{host}:{port}/interview"

        discovery = DiscoveryOrchestrator(
            providers=[
                FakeDiscoveryProvider(url),
            ]
        )

        engine = ResearchEngine(
            discovery=discovery,
        )

        collected_evidence = await engine.collect_evidence(
            company="Example",
            role="Software Engineer",
        )

        assert len(collected_evidence) == 1
        assert collected_evidence[0].purpose == "interview_experience"
        assert collected_evidence[0].provider == "fake"
        assert collected_evidence[0].result.source == "browser"

        result = await engine.research(
            company="Example",
            role="Software Engineer",
        )

        assert result.stats.raw_count == 1
        assert result.stats.normalized_count == 1
        assert result.stats.unique_count == 1
        assert result.stats.relevant_count == 1

        assert len(result.evidence) == 1

        evidence = result.evidence[0]

        assert evidence.evidence.result.source == "browser"
        assert "coding challenge" in evidence.evidence.result.content
        assert evidence.evidence.purpose == "interview_experience"
        assert evidence.evidence.provider == "fake"
        assert evidence.score >= 5

    finally:
        server.shutdown()
        server.server_close()
        thread.join()
