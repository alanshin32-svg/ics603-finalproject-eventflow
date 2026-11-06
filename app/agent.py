"""Request and output models; no model calls in the skeleton."""

from pydantic import BaseModel


class DraftRequest(BaseModel):
    announcement_text: str
    posted_date: str


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
