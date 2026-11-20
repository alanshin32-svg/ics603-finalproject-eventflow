import asyncio

import pytest

from app.drafting import draft_event
from app.models import DraftRequest, DraftResponse, SourceQuotes


@pytest.mark.parametrize(
    ("supplied_date", "supplied_time", "model_flags", "expected"),
    [
        ("", "", [], ["date", "time"]),
        ("  ", "17:00", ["description", "date"], ["description", "date"]),
        ("2026-10-22", "", [], ["time"]),
        ("2026-10-22", "17:00", [], []),
        (" 2026-10-22 ", " 17:00 ", [], []),
        ("2026-10-22", " \t ", ["location", "location"], ["location", "time"]),
    ],
)
def test_merges_missing_flags_without_mutating_extracted_fields(
    supplied_date: str,
    supplied_time: str,
    model_flags: list[str],
    expected: list[str],
) -> None:
    request = DraftRequest(
        announcement_text="Resume Review Day! This Thursday 5-7pm in POST 318.",
        posted_date="2026-10-20",
    )
    original = DraftResponse(
        title="Resume Review Day",
        description="Bring a resume for review from 5-7 PM.",
        date=supplied_date,
        time=supplied_time,
        location="POST 318",
        sig="",
        kind="Networking",
        missing_fields=model_flags,
        uncertain_fields=["date", "kind"],
        source_quotes=SourceQuotes(
            title="Resume Review Day!",
            description="Resume Review Day! This Thursday 5-7pm in POST 318.",
            date="This Thursday",
            time="5-7pm",
            location="POST 318",
            sig="",
            kind="Resume Review Day!",
        ),
    )
    original_before_call = original.model_dump()
    calls: list[DraftRequest] = []

    async def extract(supplied_request: DraftRequest) -> DraftResponse:
        calls.append(supplied_request)
        return original

    result = asyncio.run(draft_event(request, extractor=extract))

    assert result.missing_fields == expected
    assert result.date == supplied_date.strip()
    assert result.time == supplied_time.strip()
    assert result.model_dump(exclude={"date", "time", "missing_fields"}) == {
        key: value
        for key, value in original_before_call.items()
        if key not in {"date", "time", "missing_fields"}
    }
    assert original.model_dump() == original_before_call
    assert result is not original
    assert calls == [request]


def test_retrospective_stays_empty_with_missing_date_and_time() -> None:
    request = DraftRequest(
        announcement_text="Thanks everyone who came to last week's meeting!",
        posted_date="2026-10-20",
    )
    empty_quotes = SourceQuotes(
        title="", description="", date="", time="", location="", sig="", kind=""
    )
    original = DraftResponse(
        title="",
        description="",
        date="",
        time="",
        location="",
        sig="",
        kind="",
        missing_fields=[],
        uncertain_fields=[],
        source_quotes=empty_quotes,
    )

    async def extract(supplied_request: DraftRequest) -> DraftResponse:
        return original

    result = asyncio.run(draft_event(request, extractor=extract))

    assert result.model_dump() == {
        "title": "",
        "description": "",
        "date": "",
        "time": "",
        "location": "",
        "sig": "",
        "kind": "",
        "missing_fields": ["date", "time"],
        "uncertain_fields": [],
        "source_quotes": {
            "title": "", "description": "", "date": "", "time": "",
            "location": "", "sig": "", "kind": "",
        },
    }
