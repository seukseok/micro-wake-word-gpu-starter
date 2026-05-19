#!/usr/bin/env python3
"""Validate wake word audio folders and write a small dataset manifest."""

from __future__ import annotations

import argparse
import json
import sys
import wave
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


AUDIO_EXTENSIONS = {".wav", ".mp3", ".flac", ".ogg", ".m4a", ".aac", ".opus", ".webm"}


def display_path(path: Path) -> str:
    return path.as_posix()


@dataclass
class AudioIssue:
    path: str
    issue: str


@dataclass
class WavInfo:
    path: str
    frames: int
    sample_rate: int
    channels: int
    sample_width_bytes: int
    duration_seconds: float


def iter_audio_files(path: Path) -> Iterable[Path]:
    if not path.exists():
        return []
    return sorted(
        file
        for file in path.rglob("*")
        if file.is_file() and file.suffix.lower() in AUDIO_EXTENSIONS
    )


def inspect_wav(path: Path) -> tuple[WavInfo | None, AudioIssue | None]:
    if path.suffix.lower() != ".wav":
        return None, AudioIssue(display_path(path), "not a WAV file; convert with ffmpeg first")

    try:
        with wave.open(str(path), "rb") as wav:
            frames = wav.getnframes()
            sample_rate = wav.getframerate()
            channels = wav.getnchannels()
            sample_width = wav.getsampwidth()
    except wave.Error as exc:
        return None, AudioIssue(display_path(path), f"invalid WAV: {exc}")

    duration = frames / sample_rate if sample_rate else 0.0
    info = WavInfo(
        path=display_path(path),
        frames=frames,
        sample_rate=sample_rate,
        channels=channels,
        sample_width_bytes=sample_width,
        duration_seconds=round(duration, 3),
    )

    problems: list[str] = []
    if sample_rate != 16000:
        problems.append(f"sample rate is {sample_rate}, expected 16000")
    if channels != 1:
        problems.append(f"channels is {channels}, expected mono")
    if sample_width != 2:
        problems.append(f"sample width is {sample_width} bytes, expected 2")
    if duration <= 0:
        problems.append("duration is zero")

    if problems:
        return info, AudioIssue(str(path), "; ".join(problems))
    return info, None


def summarize(label: str, folder: Path) -> dict:
    files = list(iter_audio_files(folder))
    wavs: list[WavInfo] = []
    issues: list[AudioIssue] = []

    for file in files:
        info, issue = inspect_wav(file)
        if info:
            wavs.append(info)
        if issue:
            issues.append(issue)

    return {
        "label": label,
        "folder": display_path(folder),
        "audio_files": len(files),
        "valid_wavs": sum(1 for item in wavs if item.sample_rate == 16000 and item.channels == 1 and item.sample_width_bytes == 2),
        "duration_seconds": round(sum(item.duration_seconds for item in wavs), 3),
        "files": [asdict(item) for item in wavs],
        "issues": [asdict(item) for item in issues],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("positive_dir", type=Path, help="Folder with positive wake phrase samples")
    parser.add_argument("negative_dir", type=Path, help="Folder with negative or false-wake samples")
    parser.add_argument("--manifest", type=Path, default=Path("data/dataset_manifest.json"))
    parser.add_argument("--allow-empty", action="store_true", help="Do not fail when no WAV files exist")
    args = parser.parse_args()

    manifest = {
        "positive": summarize("positive", args.positive_dir),
        "negative": summarize("negative", args.negative_dir),
    }

    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    issues = manifest["positive"]["issues"] + manifest["negative"]["issues"]
    valid_total = manifest["positive"]["valid_wavs"] + manifest["negative"]["valid_wavs"]

    print(f"Wrote {args.manifest}")
    print(f"Valid WAV files: {valid_total}")
    print(f"Issues: {len(issues)}")

    if issues:
        for issue in issues[:20]:
            print(f"- {issue['path']}: {issue['issue']}", file=sys.stderr)

    if not args.allow_empty and manifest["positive"]["valid_wavs"] == 0:
        print("No valid positive WAV files found.", file=sys.stderr)
        return 1

    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
