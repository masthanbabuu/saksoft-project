import argparse
import logging
import re
import sys
from collections import Counter
from pathlib import Path

logger = logging.getLogger(__name__)


def count_words(text: str) -> Counter[str]:
    words = re.findall(r"[^\W\d_]+(?:['-][^\W\d_]+)*", text.casefold())
    return Counter(words)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Count the most frequent words in a text file.")
    parser.add_argument("file", type=Path, help="Text file to read")
    parser.add_argument("-n", "--top", type=int, default=10, help="Number of words to display")
    args = parser.parse_args(argv)

    if args.top < 1:
        parser.error("--top must be at least 1")

    try:
        text = args.file.read_text(encoding="utf-8")
    except OSError:
        sys.stderr.write(f"Cannot read file: {args.file}\n")
        return 1

    counts = count_words(text)
    for word, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[: args.top]:
        sys.stdout.write(f"{word}: {count}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
