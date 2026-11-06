import asyncio

import pytest
from pydantic import ValidationError
from pydantic_ai import capture_run_messages
from pydantic_ai.exceptions import (
    ModelConnectionError,
    ModelHTTPError,
    RunTimedOut,
    UnexpectedModelBehavior,
)
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    UserPromptPart,
)
from pydantic_ai.models.function import AgentInfo, FunctionModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.models.test import TestModel

from app import agent
from app.agent import DraftRequest


@pytest.fixture
def payload() -> dict[str, object]:
    return {
        "title": "Intro to Git",
        "description": "Join the Intro to Git workshop on Nov 3 at 6 PM.",
        "date": "2026-11-03",
        "time": "18:00",
        "location": "",
        "sig": "",
        "kind": "Workshop",
        "missing_fields": ["location", "sig"],
        "uncertain_fields": [],
        "source_quotes": {
            "title": "Intro to Git",
            "description": "Intro to Git workshop, Nov 3 at 6 PM.",
            "date": "Nov 3",
            "time": "6 PM",
            "location": "",
            "sig": "",
            "kind": "workshop",
        },
    }


@pytest.fixture
def request_data() -> DraftRequest:
    return DraftRequest(
        announcement_text="Intro to Git workshop, Nov 3 at 6 PM.",
        posted_date="2026-10-20",
    )


def test_extract_returns_typed_output_and_submits_actual_input(
    monkeypatch: pytest.MonkeyPatch,
    payload: dict[str, object],
    request_data: DraftRequest,
) -> None:
    test_model = TestModel(custom_output_args=payload)
    monkeypatch.setattr(agent, "build_gateway_model", lambda: test_model, raising=False)
    with agent.extraction_agent.override(model=test_model), capture_run_messages() as messages:
        result = asyncio.run(agent.extract_draft(request_data))

    assert result.model_dump() == payload
    assert set(result.model_dump()) == set(payload)
    user_prompts = [
        part.content
        for message in messages
        if isinstance(message, ModelRequest)
        for part in message.parts
        if isinstance(part, UserPromptPart)
    ]
    assert any(
        isinstance(prompt, str)
        and request_data.announcement_text in prompt
        and request_data.posted_date in prompt
        for prompt in user_prompts
    )


@pytest.mark.parametrize("announcement", ["", "   "])
def test_rejects_blank_announcement(announcement: str) -> None:
    with pytest.raises(ValidationError):
        DraftRequest(announcement_text=announcement, posted_date="2026-10-20")


@pytest.mark.parametrize("posted_date", ["", "bad", "2026-02-30", "20261020"])
def test_rejects_invalid_posted_date(posted_date: str) -> None:
    with pytest.raises(ValidationError):
        DraftRequest(announcement_text="Workshop", posted_date=posted_date)


def test_requires_posted_date() -> None:
    with pytest.raises(ValidationError):
        DraftRequest.model_validate({"announcement_text": "Workshop"})


@pytest.fixture
def gateway_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    # Never load the developer's .env or construct a client with its credentials.
    monkeypatch.setenv("PYTHON_DOTENV_DISABLED", "1")
    monkeypatch.setenv("LLM_API_TOKEN", "sentinel-test-secret")
    monkeypatch.setenv("LLM_API_GATEWAY", "https://example.invalid/v1")
    monkeypatch.setenv("LLM_MODEL", "course-model-for-tests")


def test_builds_configured_gateway_model(gateway_settings: None) -> None:
    model = agent.build_gateway_model()

    assert isinstance(model, OpenAIChatModel)
    assert model.model_name == "course-model-for-tests"
    assert str(model.client.base_url).rstrip("/") == "https://example.invalid/v1"
    assert model.client.api_key == "sentinel-test-secret"


@pytest.mark.parametrize("setting", ["LLM_API_TOKEN", "LLM_API_GATEWAY", "LLM_MODEL"])
@pytest.mark.parametrize("value", [None, "", "   "])
def test_missing_settings_raise_safe_configuration_error(
    monkeypatch: pytest.MonkeyPatch,
    gateway_settings: None,
    setting: str,
    value: str | None,
) -> None:
    if value is None:
        monkeypatch.delenv(setting)
    else:
        monkeypatch.setenv(setting, value)
    with pytest.raises(agent.ConfigurationError) as error:
        agent.build_gateway_model()

    assert "sentinel-test-secret" not in str(error.value)


@pytest.mark.parametrize(
    "failure",
    [
        TimeoutError("sentinel-test-secret"),
        RunTimedOut("sentinel-test-secret"),
        ModelHTTPError(500, "test", body="sentinel-test-secret"),
        ModelConnectionError("test", "sentinel-test-secret"),
        UnexpectedModelBehavior("sentinel-test-secret"),
    ],
)
def test_provider_failures_raise_safe_extraction_error(
    monkeypatch: pytest.MonkeyPatch,
    request_data: DraftRequest,
    failure: Exception,
) -> None:
    def fail(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
        raise failure

    test_model = FunctionModel(fail)
    monkeypatch.setattr(agent, "build_gateway_model", lambda: test_model, raising=False)
    with pytest.raises(agent.ExtractionError) as error:
        asyncio.run(agent.extract_draft(request_data))

    assert "sentinel-test-secret" not in str(error.value)


def test_invalid_structured_output_exhaustion_is_safe(
    monkeypatch: pytest.MonkeyPatch, request_data: DraftRequest
) -> None:
    test_model = TestModel(custom_output_args={"title": "sentinel-test-secret"})
    monkeypatch.setattr(agent, "build_gateway_model", lambda: test_model, raising=False)
    with (
        agent.extraction_agent.override(model=test_model),
        pytest.raises(agent.ExtractionError) as error,
    ):
        asyncio.run(agent.extract_draft(request_data))

    assert "sentinel-test-secret" not in str(error.value)


def test_programming_errors_are_not_disguised_as_gateway_failures(
    monkeypatch: pytest.MonkeyPatch, request_data: DraftRequest
) -> None:
    def fail(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
        raise TypeError("a programming bug")

    test_model = FunctionModel(fail)
    monkeypatch.setattr(agent, "build_gateway_model", lambda: test_model, raising=False)
    with pytest.raises(TypeError, match="a programming bug"):
        asyncio.run(agent.extract_draft(request_data))
