#!/usr/bin/env python3
"""Aggregate multiple run summary.json files into one CSV."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=Path("experiments/results/runs"),
        help="Directory that contains per-run folders with summary.json.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("experiments/results/run_comparison.csv"),
        help="Output CSV path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summaries = sorted(args.results_dir.glob("*/summary.json"))
    if not summaries:
        raise SystemExit(f"No summary.json files found under {args.results_dir}")

    rows = []
    for summary_path in summaries:
        payload = json.loads(summary_path.read_text(encoding="utf-8"))
        rows.append(payload)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "run_name",
        "samples",
        "mean_cer",
        "mean_wer",
        "mean_cer_no_punct",
        "proper_noun_misses",
        "proper_noun_total",
        "proper_noun_miss_rate",
        "dataset",
        "hyp_dir",
    ]
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})

    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
