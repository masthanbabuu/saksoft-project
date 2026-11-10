from unittest.mock import MagicMock

import psycopg

from app.services import readiness


def test_database_check_succeeds(monkeypatch):
    connection = MagicMock()
    connection.__enter__.return_value = connection

    connect = MagicMock(return_value=connection)
    monkeypatch.setattr(readiness.psycopg, "connect", connect)

    assert readiness.check_dependencies() == []

    connect.assert_called_once()
    assert connect.call_args.kwargs["connect_timeout"] == 3
    connection.execute.assert_called_once_with("SELECT 1")


def test_database_check_failure_returns_safe_message(monkeypatch):
    def fail_connection(**kwargs):
        raise psycopg.OperationalError("sensitive connection details")

    monkeypatch.setattr(readiness.psycopg, "connect", fail_connection)

    assert readiness.check_dependencies() == ["database unavailable"]
