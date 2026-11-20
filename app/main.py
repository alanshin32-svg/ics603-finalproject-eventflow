from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from app.agent import ConfigurationError, ExtractionError, extract_draft
from app.drafting import Extractor, draft_event
from app.models import DraftRequest, DraftResponse

app = FastAPI(title="EventFlow")


def get_extractor() -> Extractor:
    return extract_draft


@app.get("/", response_class=HTMLResponse)
def read_root() -> str:
    return Path(__file__).with_name("page.html").read_text(encoding="utf-8")


@app.post("/draft", response_model=DraftResponse)
async def create_draft(
    request: DraftRequest, extractor: Annotated[Extractor, Depends(get_extractor)]
) -> DraftResponse:
    try:
        return await draft_event(request, extractor=extractor)
    except ConfigurationError:
        raise HTTPException(
            status_code=503, detail="Event extraction is not configured."
        ) from None
    except ExtractionError:
        raise HTTPException(
            status_code=502, detail="Could not create a draft. Please try again."
        ) from None
