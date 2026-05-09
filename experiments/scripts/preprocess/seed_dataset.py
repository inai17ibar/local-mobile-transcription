#!/usr/bin/env python3
"""Create a fixed-size evaluation set from a long recording by evenly sampling segments."""

from __future__ import annotations

import argparse
import csv
import math
import shutil
import subprocess
from pathlib import Path


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def audio_duration(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(result.stdout.strip())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Source audio file.")
    parser.add_argument("--output-dir", required=True, type=Path, help="Directory for sampled audio segments.")
    parser.add_argument("--dataset", required=True, type=Path, help="Dataset CSV output path.")
    parser.add_argument("--count", type=int, default=24, help="Number of sampled segments to create.")
    parser.add_argument("--segment-seconds", type=int, default=30, help="Length of each sampled segment.")
    parser.add_argument("--start-padding", type=float, default=60.0, help="Seconds to skip at the start.")
    parser.add_argument("--end-padding", type=float, default=60.0, help="Seconds to skip at the end.")
    parser.add_argument("--prefix", default="sample_eval", help="Output audio_id prefix.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing segments and dataset.")
    return parser.parse_args()


def ensure_tools() -> None:
    for binary in ("ffmpeg", "ffprobe"):
        if shutil.which(binary) is None:
            raise SystemExit(f"{binary} is required but was not found in PATH.")


def evenly_spaced_starts(total_duration: float, count: int, segment_seconds: int, start_padding: float, end_padding: float) -> list[float]:
    usable_start = start_padding
    usable_end = total_duration - end_padding - segment_seconds
    if usable_end <= usable_start:
        raise SystemExit("Audio is too short for the requested padding and segment length.")
    if count == 1:
        return [usable_start]

    span = usable_end - usable_start
    return [usable_start + (span * index / (count - 1)) for index in range(count)]


def extract_segment(source: Path, destination: Path, start_sec: float, segment_seconds: int, overwrite: bool) -> None:
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y" if overwrite else "-n",
        "-ss",
        f"{start_sec:.3f}",
        "-i",
        str(source),
        "-t",
        str(segment_seconds),
        "-c",
        "copy",
        str(destination),
    ]
    run(cmd)


def main() -> None:
    args = parse_args()
    ensure_tools()

    total_duration = audio_duration(args.input)
    starts = evenly_spaced_starts(
        total_duration=total_duration,
        count=args.count,
        segment_seconds=args.segment_seconds,
        start_padding=args.start_padding,
        end_padding=args.end_padding,
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.dataset.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    digits = max(3, math.ceil(math.log10(args.count + 1)))
    for index, start_sec in enumerate(starts, start=1):
        audio_id = f"{args.prefix}_{index:0{digits}d}"
        audio_path = args.output_dir / f"{audio_id}.m4a"
        extract_segment(args.input, audio_path, start_sec, args.segment_seconds, args.overwrite)
        end_sec = start_sec + args.segment_seconds
        rows.append(
            {
                "audio_id": audio_id,
                "audio_path": audio_path.as_posix(),
                "ref_path": f"experiments/data/ref/{audio_id}.txt",
                "notes": f"seed_from={args.input.name}; review_time={int(start_sec // 60):02d}:{int(start_sec % 60):02d}-{int(end_sec // 60):02d}:{int(end_sec % 60):02d}",
                "tags": "seed|needs_transcript|needs_annotation|single_source",
                "proper_nouns": "",
                "start_sec": f"{start_sec:.3f}",
                "end_sec": f"{end_sec:.3f}",
                "duration_sec": f"{args.segment_seconds:.3f}",
                "source_audio": args.input.as_posix(),
            }
        )

    with args.dataset.open("w", newline="", encoding="utf-8") as handle:
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
        writer.writerows(rows)

    print(f"Wrote {len(rows)} sampled segments to {args.output_dir}")
    print(f"Wrote dataset manifest to {args.dataset}")
    print(f"Source duration: {total_duration:.1f}s")


if __name__ == "__main__":
    main()
