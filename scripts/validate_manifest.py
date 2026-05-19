#!/usr/bin/env python3
"""Validate an ESPHome micro_wake_word model manifest."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_TOP_LEVEL = {
    "type": str,
    "wake_word": str,
    "model": str,
    "trained_languages": list,
    "version": int,
    "micro": dict,
}

REQUIRED_MICRO = {
    "probability_cutoff": (int, float),
    "feature_step_size": int,
    "sliding_window_size": int,
    "tensor_arena_size": int,
}


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("manifest root must be an object")
    return data


def validate_manifest(path: Path, allow_missing_model: bool = False) -> list[str]:
    data = load_json(path)
    errors: list[str] = []

    for key, expected_type in REQUIRED_TOP_LEVEL.items():
        if key not in data:
            errors.append(f"missing top-level field: {key}")
            continue
        if not isinstance(data[key], expected_type):
            errors.append(f"{key} must be {expected_type}")

    if data.get("type") != "micro":
        errors.append("type must be 'micro'")

    micro = data.get("micro")
    if isinstance(micro, dict):
        for key, expected_type in REQUIRED_MICRO.items():
            if key not in micro:
                errors.append(f"missing micro field: {key}")
                continue
            if not isinstance(micro[key], expected_type):
                errors.append(f"micro.{key} must be {expected_type}")

        cutoff = micro.get("probability_cutoff")
        if isinstance(cutoff, (int, float)) and not 0 < float(cutoff) < 1:
            errors.append("micro.probability_cutoff must be between 0 and 1")

    model_name = data.get("model")
    if isinstance(model_name, str):
        model_path = path.parent / model_name
        if not allow_missing_model and not model_path.exists():
            errors.append(f"model file does not exist next to manifest: {model_name}")

    languages = data.get("trained_languages")
    if isinstance(languages, list) and not all(isinstance(item, str) for item in languages):
        errors.append("trained_languages must contain only strings")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--allow-missing-model", action="store_true")
    args = parser.parse_args()

    errors = validate_manifest(args.manifest, args.allow_missing_model)
    if errors:
        print(f"{args.manifest} is not valid:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    data = load_json(args.manifest)
    print(f"OK: {data['wake_word']} ({args.manifest})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
