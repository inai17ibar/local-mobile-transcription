#!/usr/bin/env python3
"""Seed reference transcripts from hypothesis files and write an annotation queue."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True, type=Path, help="Dataset CSV manifest.")
    parser.add_argument("--hyp-dir", required=True, type=Path, help="Directory with hypothesis text files.")
    parser.add_argument(
        "--queue-out",
        type=Path,
        default=Path("experiments/data/annotation_queue.csv"),
        help="CSV output path for the annotation work queue.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional max number of rows to include, after sorting by start_sec.",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Do not overwrite non-empty ref files.",
    )
    parser.add_argument(
        "--audio-id",
        action="append",
        default=[],
        help="Restrict processing to specific audio_id values. Repeat as needed.",
    )
    return parser.parse_args()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sort_key(row: dict[str, str]) -> tuple[float, str]:
    try:
        return (float(row.get("start_sec", "")), row["audio_id"])
    except ValueError:
        return (float("inf"), row["audio_id"])


def ref_exists_with_content(path: Path) -> bool:
    return path.exists() and path.read_text(encoding="utf-8").strip() != ""


def main() -> None:
    args = parse_args()
    rows = read_rows(args.dataset)
    selected_ids = set(args.audio_id)
    if selected_ids:
        rows = [row for row in rows if row["audio_id"] in selected_ids]
    rows.sort(key=sort_key)
    if args.limit is not None:
        rows = rows[: args.limit]

    args.queue_out.parent.mkdir(parents=True, exist_ok=True)

    queue_rows: list[dict[str, str]] = []
    drafted = 0
    skipped = 0

    for row in rows:
        audio_id = row["audio_id"]
        ref_path = Path(row["ref_path"])
        hyp_path = args.hyp_dir / f"{audio_id}.txt"
        if not hyp_path.exists():
            raise SystemExit(f"Hypothesis file not found: {hyp_path}")

        ref_path.parent.mkdir(parents=True, exist_ok=True)
        if args.skip_existing and ref_exists_with_content(ref_path):
            skipped += 1
        else:
            ref_path.write_text(hyp_path.read_text(encoding="utf-8"), encoding="utf-8")
            drafted += 1

        queue_rows.append(
            {
                "audio_id": audio_id,
                "audio_path": row["audio_path"],
                "hyp_path": hyp_path.as_posix(),
                "ref_path": ref_path.as_posix(),
                "start_sec": row.get("start_sec", ""),
                "end_sec": row.get("end_sec", ""),
                "duration_sec": row.get("duration_sec", ""),
                "tags": row.get("tags", ""),
                "proper_nouns": row.get("proper_nouns", ""),
                "notes": row.get("notes", ""),
                "status": "seeded_from_hyp",
            }
        )

    with args.queue_out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "audio_id",
                "audio_path",
                "hyp_path",
                "ref_path",
                "start_sec",
                "end_sec",
                "duration_sec",
                "tags",
                "proper_nouns",
                "notes",
                "status",
            ],
        )
        writer.writeheader()
        writer.writerows(queue_rows)

    print(f"Drafted {drafted} ref files")
    if args.skip_existing:
        print(f"Skipped {skipped} existing non-empty ref files")
    print(f"Wrote annotation queue: {args.queue_out}")


if __name__ == "__main__":
    main()
