import pytest

from app.rules import missing_date_time_fields


@pytest.mark.parametrize(
    ("date", "time", "expected"),
    [
        ("", "", ["date", "time"]),
        ("", "17:00", ["date"]),
        ("2026-10-22", "", ["time"]),
        ("2026-10-22", "17:00", []),
    ],
)
def test_missing_date_time_fields(
    date: str, time: str, expected: list[str]
) -> None:
    assert missing_date_time_fields(date=date, time=time) == expected
