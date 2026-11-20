from fastapi.testclient import TestClient

from app.main import app, get_extractor
from app.models import DraftRequest, DraftResponse, SourceQuotes

client = TestClient(app)


def test_page_loads() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "<form" in response.text


def test_draft_answers_with_the_declared_fields() -> None:
    async def extract(request: DraftRequest) -> DraftResponse:
        return DraftResponse(
            title="Intro to Git", description="", date="", time="", location="",
            sig="", kind="Workshop", missing_fields=[], uncertain_fields=[],
            source_quotes=SourceQuotes(
                title="Intro to Git", description="", date="", time="", location="",
                sig="", kind="workshop",
            ),
        )

    app.dependency_overrides[get_extractor] = lambda: extract
    try:
        response = client.post(
            "/draft",
            json={
                "announcement_text": "Intro to Git workshop, Nov 3 at 6 PM in Holmes Hall 244.",
                "posted_date": "2026-10-20",
            },
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert set(response.json()) == {
        "title",
        "description",
        "date",
        "time",
        "location",
        "sig",
        "kind",
        "missing_fields",
        "uncertain_fields",
        "source_quotes",
    }
