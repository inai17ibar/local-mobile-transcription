#!/usr/bin/env python3
"""Evaluate transcription hypotheses against references and write CSV/JSON results."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from text_metrics import cer, cer_without_punctuation, normalize_text, proper_noun_misses, wer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True, type=Path, help="Dataset CSV manifest.")
    parser.add_argument("--hyp-dir", required=True, type=Path, help="Directory with hypothesis text files.")
    parser.add_argument(
        "--run-name",
        required=True,
        help="Run name used to create experiments/results/runs/<run-name>/ outputs.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("experiments/results/runs"),
        help="Base directory for run outputs.",
    )
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def parse_proper_nouns(raw_value: str) -> list[str]:
    if not raw_value:
        return []
    return [item.strip() for item in raw_value.split("|") if item.strip()]


def main() -> None:
    args = parse_args()
    run_dir = args.output_root / args.run_name
    run_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = run_dir / "metrics.csv"
    summary_path = run_dir / "summary.json"

    rows: list[dict[str, str]] = []
    with args.dataset.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows.extend(reader)

    per_file_rows: list[dict[str, object]] = []
    sum_cer = 0.0
    sum_wer = 0.0
    sum_cer_no_punct = 0.0
    total_noun_misses = 0
    total_nouns = 0

    for row in rows:
        audio_id = row["audio_id"]
        ref_path = Path(row["ref_path"])
        hyp_path = args.hyp_dir / f"{audio_id}.txt"
        if not ref_path.exists():
            raise SystemExit(f"Reference file not found: {ref_path}")
        if not hyp_path.exists():
            raise SystemExit(f"Hypothesis file not found: {hyp_path}")

        reference = read_text(ref_path)
        hypothesis = read_text(hyp_path)
        proper_nouns = parse_proper_nouns(row.get("proper_nouns", ""))
        noun_misses, noun_total = proper_noun_misses(reference, hypothesis, proper_nouns)

        cer_value = cer(reference, hypothesis)
        wer_value = wer(reference, hypothesis)
        cer_no_punct_value = cer_without_punctuation(reference, hypothesis)
        sum_cer += cer_value
        sum_wer += wer_value
        sum_cer_no_punct += cer_no_punct_value
        total_noun_misses += noun_misses
        total_nouns += noun_total

        per_file_rows.append(
            {
                "audio_id": audio_id,
                "cer": f"{cer_value:.6f}",
                "wer": f"{wer_value:.6f}",
                "cer_no_punct": f"{cer_no_punct_value:.6f}",
                "proper_noun_misses": noun_misses,
                "proper_noun_total": noun_total,
                "ref_chars": len(normalize_text(reference)),
                "hyp_chars": len(normalize_text(hypothesis)),
                "tags": row.get("tags", ""),
                "notes": row.get("notes", ""),
            }
        )

    count = len(per_file_rows)
    if count == 0:
        raise SystemExit("Dataset is empty.")

    with metrics_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "audio_id",
                "cer",
                "wer",
                "cer_no_punct",
                "proper_noun_misses",
                "proper_noun_total",
                "ref_chars",
                "hyp_chars",
                "tags",
                "notes",
            ],
        )
        writer.writeheader()
        writer.writerows(per_file_rows)

    summary = {
        "run_name": args.run_name,
        "dataset": args.dataset.as_posix(),
        "hyp_dir": args.hyp_dir.as_posix(),
        "samples": count,
        "mean_cer": round(sum_cer / count, 6),
        "mean_wer": round(sum_wer / count, 6),
        "mean_cer_no_punct": round(sum_cer_no_punct / count, 6),
        "proper_noun_misses": total_noun_misses,
        "proper_noun_total": total_nouns,
        "proper_noun_miss_rate": round(total_noun_misses / total_nouns, 6) if total_nouns else 0.0,
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {metrics_path}")
    print(f"Wrote {summary_path}")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
