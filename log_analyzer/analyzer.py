import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import TypedDict


class Summary(TypedDict):
    total_lines: int
    valid_lines: int
    malformed_lines: int
    levels: dict[str, int]
    modules: dict[str, int]


LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR"}


def analyze_lines(lines: list[str]) -> Summary:
    """Count valid log entries and malformed lines."""
    levels: Counter[str] = Counter()
    modules: Counter[str] = Counter()
    total_lines = 0
    valid_lines = 0

    for line in lines:
        total_lines += 1
        parts = line.strip().split(maxsplit=3)

        if len(parts) != 4:
            continue

        timestamp, level, module, message = parts

        try:
            datetime.fromisoformat(timestamp)
        except ValueError:
            continue

        if level not in LEVELS or not module or not message:
            continue

        valid_lines += 1
        levels[level] += 1
        modules[module] += 1

    return {
        "total_lines": total_lines,
        "valid_lines": valid_lines,
        "malformed_lines": total_lines - valid_lines,
        "levels": dict(sorted(levels.items())),
        "modules": dict(sorted(modules.items())),
    }


def main(argv: list[str] | None = None) -> int:
    """Read a log file and write its JSON summary."""
    parser = argparse.ArgumentParser(description="Analyse application log files.")
    parser.add_argument("log_file", help="Path to the input log file")
    parser.add_argument("-o", "--output", help="Path to the JSON summary")
    args = parser.parse_args(argv)

    try:
        with Path(args.log_file).open(encoding="utf-8", errors="replace") as file:
            summary = analyze_lines(file.readlines())
    except OSError:
        sys.stderr.write(f"Cannot read file: {args.log_file}\n")
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
