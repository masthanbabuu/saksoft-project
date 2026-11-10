"""Starter tests. They show the style: one behaviour per test, named
test_<unit>_<condition>_<expected> (Playbook TST-11)."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_alive_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_no_problems_returns_ready():
    response = client.get("/health/ready")
    assert response.status_code == 200


def test_request_id_is_returned_and_reused():
    response = client.get("/health", headers={"X-Request-ID": "abc-123"})
    assert response.headers["X-Request-ID"] == "abc-123"


def test_ask_without_sources_says_i_dont_know():
    response = client.post("/ask", json={"question": "What is the loan limit?"})
    assert response.status_code == 200
    assert response.json()["answer"].startswith("I don't know")


def test_ask_empty_question_is_rejected_with_422():
    response = client.post("/ask", json={"question": ""})
    assert response.status_code == 422


def test_ask_very_long_question_is_rejected_with_422():
    response = client.post("/ask", json={"question": "x" * 5000})
    assert response.status_code == 422


def test_ask_response_includes_source_passage(monkeypatch):
    from app.models.schemas import AskResponse, Citation
    from app.routers import ask as ask_router

    expected_passage = "Standard parcels are delivered within 3 working days."

    def fake_answer_question(question):
        return AskResponse(
            answer="Standard parcels take 3 working days.",
            citations=[
                Citation(
                    source="delivery_policy.md",
                    passage=expected_passage,
                )
            ],
        )

    monkeypatch.setattr(
        ask_router.answering,
        "answer_question",
        fake_answer_question,
    )

    response = client.post(
        "/ask",
        json={"question": "How long does delivery take?"},
    )

    assert response.status_code == 200
    assert response.json()["citations"][0]["source"] == "delivery_policy.md"
    assert response.json()["citations"][0]["passage"] == expected_passage
