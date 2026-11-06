from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.agent import DraftRequest, DraftResponse, SourceQuotes

app = FastAPI(title="EventFlow")


@app.get("/", response_class=HTMLResponse)
def read_root() -> str:
    return Path(__file__).with_name("page.html").read_text(encoding="utf-8")


@app.post("/draft", response_model=DraftResponse)
def create_draft(request: DraftRequest) -> DraftResponse:
    return DraftResponse(
        title="Example event (placeholder)",
        description="This is a fixed example description, not extracted from your text.",
        date="2026-12-01",
        time="17:00",
        location="Example room",
        sig="",
        kind="Other",
        missing_fields=[],
        uncertain_fields=[],
        source_quotes=SourceQuotes(
            title="Placeholder source quote",
            description="Placeholder source quote",
            date="Placeholder source quote",
            time="Placeholder source quote",
            location="Placeholder source quote",
            sig="",
            kind="Placeholder source quote",
        ),
    )
