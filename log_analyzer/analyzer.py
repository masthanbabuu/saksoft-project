import argparse
import json
import logging
import sys
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TypedDict

logger = logging.getLogger(__name__)

LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR"}
TOP_ERROR_LIMIT = 5


class LogParseError(ValueError):
    """Raised when a log line does not match the expected format."""


class LogFileError(Exception):
    """Raised when a log file cannot be read."""


@dataclass(frozen=True)
class LogEntry:
    timestamp: datetime
    level: str
    module: str
    message: str


class ErrorCount(TypedDict):
    message: str
    count: int


class TimeRange(TypedDict):
    start: str | None
    end: str | None


class Summary(TypedDict):
    total_lines: int
    valid_lines: int
    malformed_lines: int
    levels: dict[str, int]
    modules: dict[str, int]
    top_errors: list[ErrorCount]
    time_range: TimeRange


def parse_line(line: str) -> LogEntry:
    """Parse one log line or raise LogParseError."""
    if "\x00" in line:
        raise LogParseError("line contains binary data")

    parts = line.strip().split(maxsplit=3)
    if len(parts) != 4:
        raise LogParseError("expected timestamp, level, module and message")

    timestamp_text, level, module, message = parts

    try:
        timestamp = datetime.fromisoformat(timestamp_text)
    except ValueError as exc:
        raise LogParseError("invalid timestamp") from exc

    if level not in LEVELS:
        raise LogParseError(f"unknown log level: {level}")
    if not module or not message:
        raise LogParseError("module and message must not be empty")

    return LogEntry(timestamp, level, module, message)


def analyze_lines(lines: Iterable[str]) -> Summary:
    """Analyse log lines and return a JSON-compatible summary."""
    levels: Counter[str] = Counter()
    modules: Counter[str] = Counter()
    errors: Counter[str] = Counter()
    timestamps: list[datetime] = []
    total_lines = 0
    valid_lines = 0

    for line_number, line in enumerate(lines, start=1):
        total_lines += 1
        try:
            entry = parse_line(line)
        except LogParseError as exc:
            logger.warning("Malformed log line %d: %s", line_number, exc)
            continue

        valid_lines += 1
        levels[entry.level] += 1
        modules[entry.module] += 1
        timestamps.append(entry.timestamp)

        if entry.level == "ERROR":
            errors[entry.message] += 1

    top_errors: list[ErrorCount] = [
        {"message": message, "count": count}
        for message, count in sorted(errors.items(), key=lambda item: (-item[1], item[0]))[
            :TOP_ERROR_LIMIT
        ]
    ]

    return {
        "total_lines": total_lines,
        "valid_lines": valid_lines,
        "malformed_lines": total_lines - valid_lines,
        "levels": dict(sorted(levels.items())),
        "modules": dict(sorted(modules.items())),
        "top_errors": top_errors,
        "time_range": {
            "start": min(timestamps).isoformat() if timestamps else None,
            "end": max(timestamps).isoformat() if timestamps else None,
        },
    }


def read_log_file(path: str) -> list[str]:
    """Read a log file, translating filesystem errors into LogFileError."""
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        raise LogFileError(f"Cannot read file: {path}") from exc


def main(argv: list[str] | None = None) -> int:
    """Read a log file and write its JSON summary."""
    parser = argparse.ArgumentParser(description="Analyse application log files.")
    parser.add_argument("log_file", help="Path to the input log file")
    parser.add_argument("-o", "--output", help="Path to the JSON summary")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.WARNING,
        format="%(levelname)s: %(message)s",
    )

    try:
        summary = analyze_lines(read_log_file(args.log_file))
    except LogFileError as exc:
        sys.stderr.write(f"{exc}\n")
        return 1

    output = json.dumps(summary, indent=2) + "\n"

    if args.output:
        try:
            Path(args.output).write_text(output, encoding="utf-8")
        except OSError:
            sys.stderr.write(f"Cannot write file: {args.output}\n")
            return 1
    else:
        sys.stdout.write(output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
