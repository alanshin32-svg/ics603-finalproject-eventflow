"""Shared request and draft data contracts."""

import re
from datetime import date

from pydantic import BaseModel, field_validator


class DraftRequest(BaseModel):
    announcement_text: str
    posted_date: str

    @field_validator("announcement_text")
    @classmethod
    def require_announcement(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Announcement text must not be blank.")
        return value

    @field_validator("posted_date")
    @classmethod
    def require_iso_posted_date(cls, value: str) -> str:
        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
            raise ValueError("Posted date must use YYYY-MM-DD.")
        date.fromisoformat(value)
        return value


class SourceQuotes(BaseModel):
    title: str
    description: str
    date: str
    time: str
    location: str
    sig: str
    kind: str


class DraftResponse(BaseModel):
    title: str
    description: str
    date: str
    time: str
    location: str
    sig: str
    kind: str
    missing_fields: list[str]
    uncertain_fields: list[str]
    source_quotes: SourceQuotes
