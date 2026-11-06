# EventFlow

Turn ACM announcements into event drafts for officer review. Paste an
announcement and its posted date to extract title, description, date, time,
location, SIG, and kind with source quotes and missing/uncertain flags. Python
also checks for missing date and time. Review every field; nothing is saved.

Install dependencies with `uv sync`, then start the app:

```bash
uv run fastapi dev app/main.py
```

Set these environment variables, or copy `.env.example` to a local `.env` and
fill its empty values. Existing environment values take precedence over `.env`.
Keep credentials in the environment or the untracked `.env` only.

```dotenv
LLM_API_TOKEN=
LLM_API_GATEWAY=
LLM_MODEL=
```

`LLM_API_TOKEN` is the course gateway token, `LLM_API_GATEWAY` is its OpenAI
compatible base URL, and `LLM_MODEL` is the model identifier confirmed by the
course gateway. No model name is assumed. Settings are loaded only when
extraction is requested, so the page and simulated tests work without them.

Run the project checks:

```bash
uv run ruff check
uv run mypy
uv run pytest
node tests/page-smoke.cjs
```

Tests prohibit real model requests and use simulated model output. They verify
validation, the route-to-agent-to-rule flow, typed output, and safe errors. The
Node smoke check executes the page script with minimal DOM/fetch stand-ins;
it is not browser verification. These checks do not establish
real extraction accuracy. The course model name is still unknown, so a live
gateway smoke test and actual structured-output compatibility remain unverified.
Every real draft requires human review, especially proposed relative dates.

Blank announcements or missing/invalid posted dates return 422 before
extraction. Missing gateway configuration returns 503; gateway or structured
output failures return a generic 502. The page keeps your inputs, clears the
previous result when submitting, and allows retrying. Copying, editing, approval,
saving, retrieval, and scheduling checks remain unimplemented.
