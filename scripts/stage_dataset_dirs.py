#!/usr/bin/env python3
"""Create the recommended local data staging folders."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FOLDERS = [
    ROOT / "data" / "positive",
    ROOT / "data" / "negative" / "speech_commands",
    ROOT / "data" / "negative" / "mswc",
    ROOT / "data" / "negative" / "fsd50k",
    ROOT / "data" / "negative" / "local_false_wakes",
]


def main() -> int:
    for folder in FOLDERS:
        folder.mkdir(parents=True, exist_ok=True)
        print(folder.relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
