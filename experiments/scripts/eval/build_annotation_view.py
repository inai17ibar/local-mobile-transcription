#!/usr/bin/env python3
"""Build a Markdown annotation view that shows audio/ref/hyp paths and current text."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True, type=Path, help="Dataset CSV manifest.")
    parser.add_argument("--hyp-dir", required=True, type=Path, help="Directory with hypothesis text files.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("experiments/data/annotation_view.md"),
        help="Markdown output path.",
    )
    parser.add_argument("--limit", type=int, default=None, help="Optional max number of rows.")
    parser.add_argument(
        "--audio-id",
        action="append",
        default=[],
        help="Restrict output to specific audio_id values. Repeat as needed.",
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


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


def main() -> None:
    args = parse_args()
    rows = read_rows(args.dataset)
    selected_ids = set(args.audio_id)
    if selected_ids:
        rows = [row for row in rows if row["audio_id"] in selected_ids]
    rows.sort(key=sort_key)
    if args.limit is not None:
        rows = rows[: args.limit]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Annotation View", ""]

    for row in rows:
        audio_id = row["audio_id"]
        hyp_path = args.hyp_dir / f"{audio_id}.txt"
        ref_path = Path(row["ref_path"])
        hyp_text = read_text(hyp_path)
        ref_text = read_text(ref_path)

        lines.extend(
            [
                f"## {audio_id}",
                "",
                f"- audio: `{row['audio_path']}`",
                f"- hyp: `{hyp_path.as_posix()}`",
                f"- ref: `{ref_path.as_posix()}`",
                f"- time: `{row.get('start_sec', '')} - {row.get('end_sec', '')}`",
                f"- tags: `{row.get('tags', '')}`",
                f"- proper_nouns: `{row.get('proper_nouns', '')}`",
                f"- notes: `{row.get('notes', '')}`",
                "",
                "### Hyp",
                "",
                "```text",
                hyp_text,
                "```",
                "",
                "### Ref",
                "",
                "```text",
                ref_text,
                "```",
                "",
            ]
        )

    args.output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote annotation view: {args.output}")


if __name__ == "__main__":
    main()
