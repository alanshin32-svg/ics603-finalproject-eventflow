# EventFlow

Turn ACM announcements into event drafts for officer review. The extraction
module supports typed gateway output; the current HTTP route still serves the
skeleton placeholder until extraction is connected in the next task.

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
```

Tests prohibit real model requests and use simulated model output. They verify
validation, gateway wiring, typed output, and safe errors; they do not establish
real extraction accuracy. The course model name is still unknown, so a live
gateway smoke test and actual structured-output compatibility remain unverified.
Every real draft requires human review, especially proposed relative dates.
