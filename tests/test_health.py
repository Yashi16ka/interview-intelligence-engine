from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_research_request() -> None:
    response = client.post(
        "/research",
        json={
            "company": "Salesforce",
            "role": "Software Engineer Intern",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "company": "Salesforce",
        "role": "Software Engineer Intern",
        "status": "research_queued",
    }
