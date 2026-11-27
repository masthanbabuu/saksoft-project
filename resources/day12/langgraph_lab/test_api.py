"""Test the web layer with a fake model."""

import pytest
from fastapi.testclient import TestClient

import api
import tools
from llm import ScriptedChat, final_answer, tool_call


@pytest.fixture
def client(monkeypatch):
    tools.CREATED_TICKETS.clear()
    model = ScriptedChat([tool_call("create_ticket", {"title": "Broken chair"}), final_answer("Created.")])
    monkeypatch.setattr(api, "_graph", None)
    monkeypatch.setattr(api, "get_model", lambda: model)
    return TestClient(api.app)


def test_chat_pauses_then_approve_finishes(client):
    first = client.post("/chat", json={"question": "Create a ticket"}).json()
    assert first["status"] == "needs_approval"
    assert tools.CREATED_TICKETS == []
    second = client.post("/approve", json={"thread_id": first["thread_id"], "approved": True}).json()
    assert second["status"] == "done"
    assert len(tools.CREATED_TICKETS) == 1


def test_empty_question_is_rejected(client):
    assert client.post("/chat", json={"question": ""}).status_code == 422


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}
