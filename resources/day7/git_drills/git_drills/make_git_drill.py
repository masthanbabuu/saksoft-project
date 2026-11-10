"""Builds a throw-away Git repository for the Git drill (day 3 and day 17).

USAGE:   python make_git_drill.py <empty-folder>
It creates a small repository with:
  main            the starting point
  feature/a       changes line 3 of policy.txt one way
  feature/b       changes the SAME line another way   (merging them makes a conflict)
  a fake secret   committed on branch `oops` (for the leaked-secret drill; it is a made-up value)
Then follow DRILL.md in this folder.

Everything is made up and local. Nothing is pushed anywhere. Needs Git installed.
"""

import subprocess
import sys
from pathlib import Path

POLICY = """Library lending policy
=======================
A member may keep a book for 21 days.
A member may borrow up to 5 books at once.
Overdue books cost 0.25 per day.
"""


def git(folder: Path, *args: str) -> None:
    """Run one git command inside the folder; stop with a clear message if it fails."""
    subprocess.run(["git", "-C", str(folder), *args], check=True, capture_output=True, text=True)


def build(folder: Path) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    if any(folder.iterdir()):
        raise SystemExit(f"{folder} is not empty. Use a new, empty folder.")
    git(folder, "init", "-b", "main")
    # A local identity so the drill never changes or depends on your real Git settings.
    git(folder, "config", "user.name", "Drill User")
    git(folder, "config", "user.email", "drill@example.invalid")
    (folder / "policy.txt").write_text(POLICY, encoding="utf-8")
    git(folder, "add", "policy.txt")
    git(folder, "commit", "-m", "Add lending policy")

    for branch, new_line in (("feature/a", "A member may keep a book for 28 days."),
                             ("feature/b", "A member may keep a book for 14 days.")):
        git(folder, "switch", "-c", branch, "main")
        lines = POLICY.splitlines()
        lines[2] = new_line
        (folder / "policy.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        git(folder, "commit", "-am", f"Change lending period on {branch}")

    git(folder, "switch", "-c", "oops", "main")
    (folder / "settings.txt").write_text("api_key = FAKE-NOT-A-REAL-KEY-12345\n", encoding="utf-8")
    git(folder, "add", "settings.txt")
    git(folder, "commit", "-m", "Add settings")
    git(folder, "switch", "main")
    print(f"Drill repository ready in {folder}. Open DRILL.md and start.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python make_git_drill.py <empty-folder>")
    build(Path(sys.argv[1]))
