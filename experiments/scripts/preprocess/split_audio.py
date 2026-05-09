#!/usr/bin/env python3
"""Split a long audio file into fixed-length segments and write a manifest CSV."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
from pathlib import Path


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def ffprobe_json(path: Path) -> dict:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_format",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def audio_duration(path: Path) -> float:
    payload = ffprobe_json(path)
    return float(payload["format"]["duration"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Source audio file.")
    parser.add_argument("--output-dir", required=True, type=Path, help="Segment output directory.")
    parser.add_argument("--manifest", required=True, type=Path, help="Output CSV manifest path.")
    parser.add_argument("--segment-seconds", type=int, default=30, help="Segment length in seconds.")
    parser.add_argument("--output-format", default="m4a", help="Output file extension.")
    parser.add_argument("--start-seconds", type=float, default=0.0, help="Trim start time before split.")
    parser.add_argument("--max-seconds", type=float, default=None, help="Optional duration cap after start.")
    parser.add_argument("--audio-filter", default=None, help="Optional ffmpeg audio filter chain.")
    parser.add_argument("--sample-rate", type=int, default=None, help="Optional output sample rate.")
    parser.add_argument("--mono", action="store_true", help="Force mono output.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files.")
    return parser.parse_args()


def ensure_ffmpeg() -> None:
    for binary in ("ffmpeg", "ffprobe"):
        if shutil.which(binary) is None:
            raise SystemExit(f"{binary} is required but was not found in PATH.")


def build_ffmpeg_command(args: argparse.Namespace, output_pattern: str) -> list[str]:
    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y" if args.overwrite else "-n",
    ]
    if args.start_seconds > 0:
        command += ["-ss", str(args.start_seconds)]
    command += ["-i", str(args.input)]
    if args.max_seconds is not None:
        command += ["-t", str(args.max_seconds)]
    command += ["-f", "segment", "-segment_time", str(args.segment_seconds), "-reset_timestamps", "1"]
    passthrough_copy = (
        args.sample_rate is None
        and not args.mono
        and not args.audio_filter
        and args.output_format.lower() == args.input.suffix.lstrip(".").lower()
    )
    if passthrough_copy:
        command += ["-c", "copy"]
    if args.sample_rate is not None:
        command += ["-ar", str(args.sample_rate)]
    if args.mono:
        command += ["-ac", "1"]
    if args.audio_filter:
        command += ["-af", args.audio_filter]
    command.append(output_pattern)
    return command


def main() -> None:
    args = parse_args()
    ensure_ffmpeg()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)

    stem = args.input.stem
    output_pattern = str(args.output_dir / f"{stem}_%03d.{args.output_format}")
    run(build_ffmpeg_command(args, output_pattern))

    segments = sorted(args.output_dir.glob(f"{stem}_*.{args.output_format}"))
    if not segments:
        raise SystemExit("No segments were generated.")

    start_offset = args.start_seconds
    with args.manifest.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "audio_id",
                "audio_path",
                "ref_path",
                "notes",
                "tags",
                "proper_nouns",
                "start_sec",
                "end_sec",
                "duration_sec",
                "source_audio",
            ],
        )
        writer.writeheader()
        current_start = start_offset
        for segment in segments:
            duration = audio_duration(segment)
            audio_id = segment.stem
            writer.writerow(
                {
                    "audio_id": audio_id,
                    "audio_path": segment.as_posix(),
                    "ref_path": f"experiments/data/ref/{audio_id}.txt",
                    "notes": "",
                    "tags": "",
                    "proper_nouns": "",
                    "start_sec": f"{current_start:.3f}",
                    "end_sec": f"{current_start + duration:.3f}",
                    "duration_sec": f"{duration:.3f}",
                    "source_audio": args.input.as_posix(),
                }
            )
            current_start += duration

    total_duration = sum(audio_duration(path) for path in segments)
    print(f"Generated {len(segments)} segments in {args.output_dir}")
    print(f"Manifest: {args.manifest}")
    print(f"Covered duration: {total_duration:.1f}s")


if __name__ == "__main__":
    main()
