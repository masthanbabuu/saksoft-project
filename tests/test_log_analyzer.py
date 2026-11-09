import json

from log_analyzer.analyzer import analyze_lines, main


def test_counts_valid_entries():
    result = analyze_lines(
        [
            "2026-03-02T08:00:12 INFO auth login ok user=u101",
            "2026-03-02T08:01:00 ERROR billing payment failed",
        ]
    )
    assert result["total_lines"] == 2
    assert result["valid_lines"] == 2
    assert result["malformed_lines"] == 0


def test_counts_each_log_level():
    result = analyze_lines(
        [
            "2026-03-02T08:00:00 DEBUG auth debug message",
            "2026-03-02T08:01:00 INFO auth info message",
            "2026-03-02T08:02:00 WARNING api warning message",
            "2026-03-02T08:03:00 ERROR db error message",
        ]
    )
    assert result["levels"] == {
        "DEBUG": 1,
        "INFO": 1,
        "WARNING": 1,
        "ERROR": 1,
    }


def test_counts_modules():
    result = analyze_lines(
        [
            "2026-03-02T08:00:00 INFO auth login ok",
            "2026-03-02T08:01:00 ERROR api request failed",
            "2026-03-02T08:02:00 INFO auth logout ok",
        ]
    )
    assert result["modules"] == {"auth": 2, "api": 1}


def test_counts_malformed_lines():
    result = analyze_lines(
        [
            "2026-03-02T08:00:00 INFO auth login ok",
            "not a log line",
            "2026-03-02T08:01:00 LOUD api invalid level",
            "",
        ]
    )
    assert result["total_lines"] == 4
    assert result["valid_lines"] == 1
    assert result["malformed_lines"] == 3


def test_rejects_invalid_timestamp():
    result = analyze_lines(
        [
            "not-a-timestamp INFO auth login ok",
        ]
    )
    assert result["malformed_lines"] == 1


def test_preserves_spaces_in_message():
    result = analyze_lines(
        [
            "2026-03-02T08:00:00 INFO auth user login completed successfully",
        ]
    )
    assert result["valid_lines"] == 1


def test_handles_binary_junk():
    result = analyze_lines(
        [
            "2026-03-02T08:00:00 INFO auth login ok",
            "\x00\x00binary junk\x00",
        ]
    )
    assert result["valid_lines"] == 1
    assert result["malformed_lines"] == 1


def test_empty_file(tmp_path):
    log_file = tmp_path / "empty.log"
    log_file.write_bytes(b"")

    result = main([str(log_file)])
    assert result == 0


def test_writes_json_summary(tmp_path):
    log_file = tmp_path / "sample.log"
    output_file = tmp_path / "summary.json"
    log_file.write_text(
        "2026-03-02T08:00:00 INFO auth login ok\n",
        encoding="utf-8",
    )

    assert main([str(log_file), "-o", str(output_file)]) == 0

    summary = json.loads(output_file.read_text(encoding="utf-8"))
    assert summary["valid_lines"] == 1
    assert summary["levels"]["INFO"] == 1


def test_missing_file_returns_error(tmp_path, capsys):
    result = main([str(tmp_path / "missing.log")])
    assert result == 1
    assert "Cannot read file" in capsys.readouterr().err
