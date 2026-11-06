"""Business rules for reviewing event drafts."""


def missing_date_time_fields(date: str, time: str) -> list[str]:
    """Return missing date/time field names; an empty string means absent."""
    missing = []
    if not date:
        missing.append("date")
    if not time:
        missing.append("time")
    return missing
