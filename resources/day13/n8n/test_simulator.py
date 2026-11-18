"""Checks the simulator against a tiny local server that behaves like a SAFE webhook."""

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

import webhook_simulator

SECRET = "test-secret-value"


class SafeWebhook(BaseHTTPRequestHandler):
    def do_POST(self):  # noqa: N802 (name required by the http.server module)
        import json

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode()
        ok = self.headers.get(webhook_simulator.HEADER_NAME) == SECRET
        try:
            data = json.loads(body)
            ok = (
                ok
                and isinstance(data.get("message"), str)
                and 0 < len(data["message"]) <= 2000
                and "user" in data
            )
        except ValueError:
            ok = False
        self.send_response(200 if ok else 400)
        self.end_headers()

    def log_message(self, *args):
        pass


@pytest.fixture
def server():
    httpd = HTTPServer(("127.0.0.1", 0), SafeWebhook)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{httpd.server_port}/"
    httpd.shutdown()


def test_simulator_passes_against_a_safe_webhook(server, monkeypatch, capsys):
    monkeypatch.setenv("WEBHOOK_URL", server)
    monkeypatch.setenv("WEBHOOK_SECRET", SECRET)
    assert webhook_simulator.main() == 0
    assert "All cases behaved" in capsys.readouterr().out


def test_simulator_without_settings_explains_what_to_do(monkeypatch, capsys):
    monkeypatch.delenv("WEBHOOK_URL", raising=False)
    monkeypatch.delenv("WEBHOOK_SECRET", raising=False)
    assert webhook_simulator.main() == 2
    assert "Set WEBHOOK_URL" in capsys.readouterr().out
