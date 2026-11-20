import json
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from pydantic_ai import capture_run_messages
from pydantic_ai.messages import ModelRequest, UserPromptPart
from pydantic_ai.models.test import TestModel

from app import agent
from app.main import app, get_extractor
from app.models import DraftRequest, DraftResponse, SourceQuotes


@pytest.fixture
def client() -> Iterator[TestClient]:
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def request_body() -> dict[str, str]:
    return {
        "announcement_text": "  Intro to Git workshop\nJoin us!  ",
        "posted_date": "2026-10-20",
    }


@pytest.fixture
def extracted() -> DraftResponse:
    return DraftResponse(
        title="Intro to Git", description="Join our Git workshop.",
        date="  ", time="\t", location="", sig="", kind="Workshop",
        missing_fields=[], uncertain_fields=["location"],
        source_quotes=SourceQuotes(
            title="Intro to Git", description="Intro to Git workshop",
            date="", time="", location="", sig="", kind="workshop",
        ),
    )


def test_draft_uses_actual_input_and_merges_python_missing_flags(
    client: TestClient, request_body: dict[str, str], extracted: DraftResponse
) -> None:
    requests: list[DraftRequest] = []

    async def extract(request: DraftRequest) -> DraftResponse:
        requests.append(request)
        return extracted

    app.dependency_overrides[get_extractor] = lambda: extract
    successful_response = client.post("/draft", json=request_body)

    assert successful_response.status_code == 200
    assert successful_response.json()["missing_fields"] == ["date", "time"]
    assert successful_response.json()["title"] == "Intro to Git"
    assert successful_response.json()["date"] == ""
    assert successful_response.json()["time"] == ""
    assert successful_response.json()["uncertain_fields"] == ["location"]
    assert successful_response.json()["source_quotes"]["title"] == "Intro to Git"
    assert [request.model_dump() for request in requests] == [request_body]


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"announcement_text": "", "posted_date": "2026-10-20"},
        {"announcement_text": "  ", "posted_date": "2026-10-20"},
        {"announcement_text": "Workshop", "posted_date": ""},
        {"announcement_text": "Workshop", "posted_date": "bad"},
        {"announcement_text": "Workshop", "posted_date": "2026-02-30"},
    ],
)
def test_invalid_body_never_calls_extractor(
    client: TestClient, body: dict[str, str], extracted: DraftResponse
) -> None:
    extractor_calls_for_invalid_body: list[DraftRequest] = []

    async def extract(request: DraftRequest) -> DraftResponse:
        extractor_calls_for_invalid_body.append(request)
        return extracted

    app.dependency_overrides[get_extractor] = lambda: extract
    invalid_body_response = client.post("/draft", json=body)

    assert invalid_body_response.status_code == 422
    assert extractor_calls_for_invalid_body == []


def test_missing_configuration_returns_503_but_page_still_loads(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, request_body: dict[str, str]
) -> None:
    monkeypatch.setenv("PYTHON_DOTENV_DISABLED", "1")
    for name in ("LLM_API_TOKEN", "LLM_API_GATEWAY", "LLM_MODEL"):
        monkeypatch.delenv(name, raising=False)

    missing_config_response = client.post("/draft", json=request_body)

    assert missing_config_response.status_code == 503
    assert isinstance(missing_config_response.json()["detail"], str)
    assert client.get("/").status_code == 200


@pytest.mark.parametrize(
    ("failure", "status"),
    [
        (agent.ConfigurationError("sentinel-secret"), 503),
        (agent.ExtractionError("sentinel-secret"), 502),
    ],
)
def test_route_errors_use_safe_detail(
    client: TestClient, request_body: dict[str, str], failure: Exception, status: int
) -> None:
    async def extract(request: DraftRequest) -> DraftResponse:
        raise failure

    app.dependency_overrides[get_extractor] = lambda: extract
    gateway_failure_response = client.post("/draft", json=request_body)

    assert gateway_failure_response.status_code == status
    assert "sentinel-secret" not in gateway_failure_response.text
    assert isinstance(gateway_failure_response.json()["detail"], str)
    assert gateway_failure_response.json()["detail"]


def test_route_agent_rule_chain_with_simulated_model(
    client: TestClient, monkeypatch: pytest.MonkeyPatch,
    request_body: dict[str, str], extracted: DraftResponse,
) -> None:
    test_model = TestModel(custom_output_args=extracted.model_dump())
    monkeypatch.setattr(agent, "build_gateway_model", lambda: test_model)

    with capture_run_messages() as messages:
        response = client.post("/draft", json=request_body)

    assert response.status_code == 200
    assert response.json()["title"] == "Intro to Git"
    assert response.json()["kind"] == "Workshop"
    assert response.json()["source_quotes"]["kind"] == "workshop"
    assert response.json()["date"] == ""
    assert response.json()["time"] == ""
    assert response.json()["missing_fields"] == ["date", "time"]
    prompts = [
        json.loads(part.content)
        for message in messages
        if isinstance(message, ModelRequest)
        for part in message.parts
        if isinstance(part, UserPromptPart) and isinstance(part.content, str)
    ]
    assert request_body in prompts


def test_invalid_model_output_returns_safe_502(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, request_body: dict[str, str]
) -> None:
    test_model = TestModel(custom_output_args={"title": "sentinel-secret"})
    monkeypatch.setattr(agent, "build_gateway_model", lambda: test_model)

    gateway_failure_response = client.post("/draft", json=request_body)

    assert gateway_failure_response.status_code == 502
    assert "sentinel-secret" not in gateway_failure_response.text
