"""Coordinate event extraction and deterministic missing-field checks."""

from collections.abc import Awaitable, Callable

from app.models import DraftRequest, DraftResponse
from app.rules import missing_date_time_fields

Extractor = Callable[[DraftRequest], Awaitable[DraftResponse]]


async def draft_event(request: DraftRequest, *, extractor: Extractor) -> DraftResponse:
    """Return a normalized draft with stable, merged missing-field flags."""
    extracted = await extractor(request)
    date = extracted.date.strip()
    time = extracted.time.strip()
    missing_fields = list(
        dict.fromkeys(
            extracted.missing_fields + missing_date_time_fields(date=date, time=time)
        )
    )
    return extracted.model_copy(
        update={"date": date, "time": time, "missing_fields": missing_fields}
    )
