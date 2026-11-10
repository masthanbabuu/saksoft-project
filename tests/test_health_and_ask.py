"""Starter tests. They show the style: one behaviour per test, named
test_<unit>_<condition>_<expected> (Playbook TST-11)."""

from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.main import app

client = TestClient(app)


def test_health_alive_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_no_problems_returns_ready(monkeypatch):
    from app.routers import health as health_router

    monkeypatch.setattr(
        health_router.readiness,
        "check_dependencies",
        lambda: [],
    )

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
    assert response.json() == {
        "error": {
            "code": "validation_error",
            "message": "Request validation failed.",
            "request_id": response.headers["X-Request-ID"],
        }
    }


def test_ask_very_long_question_is_rejected_with_422():
    response = client.post("/ask", json={"question": "x" * 5000})

    assert response.status_code == 422
    assert response.json() == {
        "error": {
            "code": "validation_error",
            "message": "Request validation failed.",
            "request_id": response.headers["X-Request-ID"],
        }
    }


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


def test_unhandled_error_returns_safe_response_with_request_id(monkeypatch):
    from app.routers import ask as ask_router

    def raise_error(question):
        raise RuntimeError("database password must not be exposed")

    monkeypatch.setattr(ask_router.answering, "answer_question", raise_error)

    error_client = TestClient(app, raise_server_exceptions=False)
    response = error_client.post(
        "/ask",
        json={"question": "Test failure"},
        headers={"X-Request-ID": "error-123"},
    )

    assert response.status_code == 500
    assert response.headers["X-Request-ID"] == "error-123"
    assert response.json() == {
        "error": {
            "code": "internal_error",
            "message": "Something went wrong.",
            "request_id": "error-123",
        }
    }
    assert "database password" not in response.text


def test_request_id_is_generated_when_header_is_missing():
    import uuid

    response = client.get("/health")

    request_id = response.headers["X-Request-ID"]
    assert str(uuid.UUID(request_id)) == request_id


def test_api_docs_are_enabled_in_development(monkeypatch):
    from app import main
    from app.config import Settings

    monkeypatch.setattr(main, "get_settings", lambda: Settings(app_environment="development"))
    test_client = TestClient(main.create_app())

    assert test_client.get("/docs").status_code == 200
    assert test_client.get("/openapi.json").status_code == 200


def test_api_docs_are_disabled_in_production(monkeypatch):
    from app import main
    from app.config import Settings

    production_settings = Settings(
        app_environment="production",
        postgres_password=SecretStr("test-only"),
        llm_base_url="https://example.com",
        llm_model="test-model",
        llm_api_key=SecretStr("test-only"),
    )
    monkeypatch.setattr(main, "get_settings", lambda: production_settings)
    test_client = TestClient(main.create_app())

    assert test_client.get("/docs").status_code == 404
    assert test_client.get("/openapi.json").status_code == 404


def test_ready_dependency_failure_returns_503(monkeypatch):
    from app.routers import health as health_router

    monkeypatch.setattr(
        health_router.readiness,
        "check_dependencies",
        lambda: ["database unavailable"],
    )

    response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json() == {
        "status": "not ready",
        "problems": "database unavailable",
    }
