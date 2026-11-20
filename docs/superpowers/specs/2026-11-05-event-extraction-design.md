# Real event draft extraction

## Intent

Help ACM officers turn a pasted announcement and its posted date into a real,
structured draft they can inspect against the original text. Replace the
skeleton's fixed response without building persistence or the entire proposal.
This is one focused feature in the existing FastAPI application.

## Chosen scope

The user chose candidate A: extract title, description, date, time, location,
SIG, and kind, with source quotes and missing/uncertain field lists. The user
also chose to run the existing Python missing-date/time check after extraction.
Candidate C's editing and copying are reserved for a later change.

No database, retrieval, saved-description style examples, scheduling conflicts,
accounts, editing, copying, approval actions, or saving are included. Past-date,
room-normalization, and other business checks remain separate future work.
Existing disabled page areas remain clearly marked as unimplemented.

## Approaches

1. Model extraction only: smallest integration, but missing-date/time reporting
   would rely entirely on the model.
2. Model extraction plus the existing Python date/time check: slightly more
   integration, with deterministic reporting whenever date or time is blank.
   The user selected this recommended approach.

Both approaches use the existing FastAPI/Pydantic AI stack and the course
gateway. Neither needs retrieval or a database.

## Request and result

Keep GET / and POST /draft and the existing successful-response field names.
The request has announcement_text and posted_date. The response has title,
description, date, time, location, sig, kind, missing_fields, uncertain_fields,
and source_quotes with one entry per drafted field.

Use the proposal's Kind and SIG lists as prompt reference data for this slice;
do not create reference tables or invent additional values. The ACM form is
still authoritative if its lists differ. The description is one to three
sentences using facts only from the new announcement, including an end time
when supplied. No slug or image is generated.

Prompt the model to leave absent values and their quotes empty, flag uncertain
choices, and use the posted date to interpret relative dates. Proposed relative
dates are marked uncertain for human confirmation. Dates use YYYY-MM-DD and
times HH:MM. Source quotes come from the announcement; description wording may
be paraphrased. A retrospective message with no upcoming event produces no
invented event details and cannot cause a record to be saved.

After extraction, merge the helper's missing date/time names with the model's
missing_fields, without duplicates. Missing or whitespace-only date/time
values are represented as empty strings before the existing helper runs.
This check identifies absence; it does not establish calendar correctness or
guarantee model accuracy. The officer still reviews every result.

## Flow and responsibilities

- app/main.py serves the page and handles HTTP requests; routes contain no
  business rules or model prompts.
- app/agent.py owns model construction, extraction instructions, and invocation.
- app/rules.py keeps the existing pure Python date/time check.
- Proposed app/models.py owns request and response models, separating the
  shared data contract from the model client.
- Proposed app/drafting.py coordinates extraction and the missing-field check,
  keeping that orchestration out of the HTTP routes.
- app/page.html submits the request, displays returned fields and flags, and
  preserves the entered text/date after success or failure. It clears an old
  result when a new request starts so a failed request cannot look successful.

The two additional modules are the agent's proposed responsibility split, not
a choice previously made by the user. Update AGENTS.md Layout with that split
in the implementation change.

## Configuration and failure behavior

Continue reading LLM_API_TOKEN and LLM_API_GATEWAY from the environment, with
local .env support. The agent proposes LLM_MODEL as a separate configuration
value so a course model name is never guessed or hardcoded. Document names
and placeholders in .env.example and README; never commit real credentials.

The model name remains unknown by the user's decision. It does not block the
design or simulated tests. It blocks a real gateway smoke test: tell the user
when that point is reached, and do not claim real extraction was verified.

Agent-proposed defaults: blank announcement/posted date and malformed posted
date return a clear 422 response before a model call. Missing configuration
returns 503; gateway failures, timeout, or invalid structured output return a
generic 502 message without exposing provider details or credentials. The page
shows a readable error and allows retrying. GET / and simulated tests must
work without gateway credentials. No fallback placeholder masquerades as a
real extraction result.

## Evidence and completion

Write failing tests before implementation. Test request validation, structured
response wiring, Python missing-field merging, configuration/provider errors,
and unchanged source input behavior where feasible. Keep the skeleton tests
focused on page presence and the declared successful response fields.

Tests must never call a real model: use Pydantic AI TestModel with
override_allow_model_requests(False), and controlled simulated failures where
needed. Run uv run ruff check, uv run mypy, and uv run pytest; keep all checks
intact. A real gateway test is separate and awaits a confirmed model name.

Reflect the agreed feature boundary in the relevant sections of
docs/proposal.md (Up to three core features, LLM role, and Human review),
preserving the full-project goals rather than presenting this slice as all of
version one. Name affected proposal sections in the eventual PR Summary.
Leave the user's existing uncommitted AGENTS.md edit untouched unless they
authorize consolidating its duplicate Spec section.

## Remaining builder choices

The implementation plan should verify the installed Pydantic AI API and name
the concrete interfaces and test seams. Model name and actual gateway
compatibility remain explicitly unresolved until a real smoke test is possible.
