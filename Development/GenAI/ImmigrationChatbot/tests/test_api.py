import pytest
from fastapi.testclient import TestClient

from immigration_chatbot.api import app
from immigration_chatbot.memory import init_db, reset_backend_cache


@pytest.fixture(autouse=True)
def setup_env(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.setenv("LLM_ENABLED", "false")
    monkeypatch.setenv("MEMORY_BACKEND", "sql")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/test_chatbot.db")
    monkeypatch.setenv("API_AUTH_ENABLED", "false")
    reset_backend_cache()
    init_db()


def test_health_endpoint() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_chat_endpoint_returns_reply_and_history(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    # keep references to fixture params for explicitness in this test signature
    assert monkeypatch is not None
    assert tmp_path is not None

    payload = {
        "session_id": "test-session",
        "message": "I am waiting for my visa update and feeling anxious",
    }

    with TestClient(app) as client:
        response = client.post("/api/chat", json=payload)
        assert response.status_code == 200

    body = response.json()
    assert body["session_id"] == "test-session"
    assert body["source"] == "rule_based"
    assert isinstance(body["reply"], str) and len(body["reply"]) > 0
    assert len(body["history"]) >= 2
    assert body["history"][0]["role"] == "user"
    assert body["history"][1]["role"] == "assistant"


def test_stream_endpoint_returns_sse_done_event() -> None:
    payload = {
        "session_id": "stream-session",
        "message": "Can you help me with visa timeline anxiety?",
    }

    with TestClient(app) as client:
        with client.stream("POST", "/api/chat/stream", json=payload) as response:
            assert response.status_code == 200
            text = "".join(response.iter_text())

    assert "event: token" in text
    assert "event: done" in text


def test_auth_rejects_when_enabled_and_missing_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("API_AUTH_ENABLED", "true")
    monkeypatch.setenv("API_AUTH_KEY", "secret123")

    payload = {
        "session_id": "auth-session",
        "message": "Need help drafting employer message",
    }

    with TestClient(app) as client:
        response = client.post("/api/chat", json=payload)

    assert response.status_code == 401


def test_auth_accepts_correct_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("API_AUTH_ENABLED", "true")
    monkeypatch.setenv("API_AUTH_KEY", "secret123")

    payload = {
        "session_id": "auth-ok-session",
        "message": "Need clarity on conflicting information",
    }

    with TestClient(app) as client:
        response = client.post(
            "/api/chat",
            json=payload,
            headers={"X-API-Key": "secret123"},
        )

    assert response.status_code == 200
