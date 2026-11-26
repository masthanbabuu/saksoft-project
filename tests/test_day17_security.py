from fastapi.testclient import TestClient

from app.main import create_app


def test_security_headers():
    client = TestClient(create_app())
    response = client.get("/health/live")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "Content-Security-Policy" in response.headers


def test_cors_allowed():
    client = TestClient(create_app())
    response = client.get(
        "/health/live",
        headers={"Origin": "http://localhost:8000"},
    )
    assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:8000"


def test_cors_denied():
    client = TestClient(create_app())
    response = client.get(
        "/health/live",
        headers={"Origin": "https://untrusted.example"},
    )
    assert "Access-Control-Allow-Origin" not in response.headers


def test_request_size():
    client = TestClient(create_app())
    response = client.post("/ask", content=b"x" * (6 * 1024 * 1024))
    assert response.status_code == 413


def test_rate_limit():
    client = TestClient(create_app())
    for _ in range(60):
        response = client.get("/rate-limit-check")
        assert response.status_code != 429

    response = client.get("/rate-limit-check")
    assert response.status_code == 429
    assert int(response.headers["Retry-After"]) > 0
