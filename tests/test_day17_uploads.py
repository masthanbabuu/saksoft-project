from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.routers import uploads

client = TestClient(app)


def test_valid_upload(tmp_path, monkeypatch):
    monkeypatch.setattr(uploads, "UPLOAD_DIR", tmp_path)

    response = client.post(
        "/upload",
        files={"file": ("../../sample.pdf", b"%PDF-1.4\n", "application/pdf")},
    )

    assert response.status_code == 201
    filename = response.json()["filename"]
    assert Path(filename).name == filename
    assert filename != "sample.pdf"
    assert (tmp_path / filename).exists()


def test_invalid_type():
    response = client.post(
        "/upload",
        files={"file": ("test.exe", b"test", "application/octet-stream")},
    )
    assert response.status_code == 415


def test_fake_pdf():
    response = client.post(
        "/upload",
        files={"file": ("fake.pdf", b"invalid", "application/pdf")},
    )
    assert response.status_code == 415


def test_oversized_upload():
    response = client.post(
        "/upload",
        files={
            "file": (
                "large.pdf",
                b"%PDF-" + b"x" * (3 * 1024 * 1024),
                "application/pdf",
            )
        },
    )
    assert response.status_code == 413
