#!/usr/bin/env python3
"""Inspect the curated public dataset catalog."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "datasets" / "catalog.json"


def load_catalog(path: Path = CATALOG) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def first_run_ids() -> set[str]:
    return {
        "kahrendt_microwakeword_features",
        "google_speech_commands_v0_02",
        "mlcommons_multilingual_spoken_words_microset",
        "fsd50k",
    }


def select_datasets(catalog: dict[str, Any], recommended: str | None) -> list[dict[str, Any]]:
    datasets = list(catalog["datasets"])
    if recommended == "first":
        wanted = first_run_ids()
        return [item for item in datasets if item["id"] in wanted]
    return datasets


def print_table(datasets: list[dict[str, Any]]) -> None:
    for item in datasets:
        roles = ", ".join(item.get("role", []))
        print(f"{item['id']}")
        print(f"  name: {item['name']}")
        print(f"  license: {item['license']}")
        print(f"  role: {roles}")
        print(f"  url: {item['url']}")
        print()


def write_plan(path: Path, datasets: list[dict[str, Any]]) -> None:
    plan = {
        "created_from": "datasets/catalog.json",
        "audio_files_included": False,
        "datasets": [
            {
                "id": item["id"],
                "name": item["name"],
                "url": item["url"],
                "license": item["license"],
                "recommended_for": item.get("recommended_for", []),
                "local_status": "not_downloaded",
            }
            for item in datasets
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print raw JSON for selected datasets")
    parser.add_argument("--recommended", choices=["first"], help="Show a recommended subset")
    parser.add_argument("--write-plan", type=Path, help="Write a local dataset planning manifest")
    args = parser.parse_args()

    catalog = load_catalog()
    datasets = select_datasets(catalog, args.recommended)

    if args.write_plan:
        write_plan(args.write_plan, datasets)
    elif args.json:
        print(json.dumps({"datasets": datasets}, indent=2))
    else:
        print_table(datasets)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
