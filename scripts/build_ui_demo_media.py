#!/usr/bin/env python3
"""Build README media from captured trainer UI frames."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FRAMES = ROOT / ".tools" / "trainer-ui-frames"
DEFAULT_ASSETS = ROOT / "docs" / "assets"
FPS = 10
GIF_WIDTH = 960


def load_frames(frame_dir: Path) -> list[Image.Image]:
    paths = sorted(frame_dir.glob("frame_*.png"))
    if not paths:
        raise FileNotFoundError(f"No frames found in {frame_dir}")

    frames: list[Image.Image] = []
    for path in paths:
        frame = Image.open(path).convert("RGB")
        ratio = GIF_WIDTH / frame.width
        height = int(frame.height * ratio)
        if height % 2:
            height -= 1
        resized = frame.resize((GIF_WIDTH, height), Image.Resampling.LANCZOS)
        frames.append(resized)
    return frames


def save_gif(frames: list[Image.Image], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        output,
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / FPS),
        loop=0,
        optimize=True,
    )


def save_mp4(frames: list[Image.Image], output: Path) -> bool:
    try:
        import imageio_ffmpeg  # type: ignore
    except Exception:
        return False

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        for idx, frame in enumerate(frames):
            frame.save(tmp / f"frame_{idx:04d}.png")
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-framerate",
                str(FPS),
                "-i",
                str(tmp / "frame_%04d.png"),
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
                str(output),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frame-dir", type=Path, default=DEFAULT_FRAMES)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_ASSETS)
    args = parser.parse_args()

    frames = load_frames(args.frame_dir)
    gif = args.out_dir / "trainer-ui-demo.gif"
    mp4 = args.out_dir / "trainer-ui-demo.mp4"

    save_gif(frames, gif)
    print(f"Wrote {gif.relative_to(ROOT).as_posix()}")
    if save_mp4(frames, mp4):
        print(f"Wrote {mp4.relative_to(ROOT).as_posix()}")
    else:
        print("Skipped MP4: install imageio-ffmpeg to enable MP4 export", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
