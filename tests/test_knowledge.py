"""Acceptance tests for the Knowledge Assistant page."""

import re

import pytest
from fastapi.testclient import TestClient

from app import main
from app.models.schemas import AskResponse, Citation


def test_knowledge_page_loads_with_csrf_token():
    client = TestClient(main.app)

    response = client.get("/knowledge")

    assert response.status_code == 200
    assert "Knowledge Assistant" in response.text
    assert 'name="csrf_token"' in response.text
    assert 'id="question"' in response.text


def test_knowledge_page_has_accessibility_features():
    client = TestClient(main.app)

    response = client.get("/knowledge")

    assert '<label for="question">' in response.text
    assert 'aria-live="polite"' in response.text
    assert 'id="answer"' in response.text

    css = client.get("/static/knowledge.css")
    assert css.status_code == 200
    assert ":focus-visible" in css.text


def test_knowledge_page_has_security_headers():
    client = TestClient(main.app)

    response = client.get("/knowledge")

    assert "default-src 'self'" in response.headers["content-security-policy"]
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"


def test_knowledge_rejects_invalid_csrf_token():
    client = TestClient(main.app)
    client.get("/knowledge")

    response = client.post(
        "/knowledge/ask",
        data={
            "question": "What is the company policy?",
            "csrf_token": "invalid-token",
        },
    )

    assert response.status_code == 403


def test_knowledge_returns_answer_and_citations(monkeypatch):
    client = TestClient(main.app)
    page = client.get("/knowledge")

    token_match = re.search(
        r'name="csrf_token"\s+value="([^"]+)"',
        page.text,
    )
    assert token_match is not None

    def fake_answer_question(question):
        assert question == "What is the company policy?"
        return AskResponse(
            answer="The policy allows remote work.",
            citations=[
                Citation(
                    source="Employee Handbook",
                    passage="Remote work is permitted.",
                )
            ],
        )

    monkeypatch.setattr(
        main.knowledge.answering,
        "answer_question",
        fake_answer_question,
    )

    response = client.post(
        "/knowledge/ask",
        data={
            "question": "What is the company policy?",
            "csrf_token": token_match.group(1),
        },
    )

    assert response.status_code == 200
    assert "The policy allows remote work." in response.text
    assert "Employee Handbook" in response.text
    assert "Remote work is permitted." in response.text


def test_knowledge_escapes_script_tags(monkeypatch):
    client = TestClient(main.app)
    page = client.get("/knowledge")

    token_match = re.search(
        r'name="csrf_token"\s+value="([^"]+)"',
        page.text,
    )
    assert token_match is not None

    script_payload = "<script>alert('xss')</script>"

    def fake_answer_question(question):
        return AskResponse(answer=script_payload, citations=[])

    monkeypatch.setattr(
        main.knowledge.answering,
        "answer_question",
        fake_answer_question,
    )

    response = client.post(
        "/knowledge/ask",
        data={
            "question": "Show test content",
            "csrf_token": token_match.group(1),
        },
    )

    assert response.status_code == 200
    assert "&lt;script&gt;" in response.text
    assert "<script>alert('xss')</script>" not in response.text


@pytest.fixture(autouse=True)
def authenticated_test_user():
    from app.main import app
    from app.services.auth_security import (
        AuthenticatedUser,
        get_current_user,
    )

    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(id=1, role="reader")

    try:
        yield
    finally:
        app.dependency_overrides.pop(get_current_user, None)
