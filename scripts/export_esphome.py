#!/usr/bin/env python3
"""Generate an ESPHome micro_wake_word YAML snippet from a model manifest."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


def load_manifest(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("manifest root must be an object")
    if data.get("type") != "micro":
        raise ValueError("manifest type must be 'micro'")
    if not isinstance(data.get("model"), str):
        raise ValueError("manifest is missing model")
    return data


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    return slug or "wake_word"


def build_snippet(manifest_path: Path, esphome_model_path: str | None) -> str:
    data = load_manifest(manifest_path)
    wake_word = str(data.get("wake_word") or manifest_path.stem)
    model_ref = esphome_model_path or f"/config/esphome/models/{manifest_path.name}"
    model_id = f"{slugify(wake_word)}_wake_word"

    return "\n".join(
        [
            "micro_wake_word:",
            "  models:",
            f"    - model: {model_ref}",
            f"      id: {model_id}",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument(
        "--model-path",
        help="Path ESPHome will use for the JSON manifest, for example /config/esphome/models/hey_komi.json",
    )
    parser.add_argument("--output", type=Path, help="Optional YAML output path")
    args = parser.parse_args()

    try:
        snippet = build_snippet(args.manifest, args.model_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Could not export ESPHome snippet: {exc}", file=sys.stderr)
        return 1

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(snippet, encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        print(snippet)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
