from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_page_loads() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "<form" in response.text


def test_draft_answers_with_the_declared_fields() -> None:
    response = client.post(
        "/draft",
        json={
            "announcement_text": "Intro to Git workshop, Nov 3 at 6 PM in Holmes Hall 244.",
            "posted_date": "2026-10-20",
        },
    )
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
