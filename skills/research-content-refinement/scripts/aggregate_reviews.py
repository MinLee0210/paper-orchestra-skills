#!/usr/bin/env python3
"""Aggregate independent reviewer samples into one robust review.

Example:
    python aggregate_reviews.py review_a.json review_b.json review_c.json --out review_v0.json

Numeric axes use the mean by default; `--stat median` uses the median. Lists
are unioned in first-seen order. Decision is the majority, with ties rejected.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

AXES = [
    "Overall", "Confidence", "Originality", "Quality", "Clarity",
    "Significance", "Soundness", "Presentation", "Contribution",
]
LIST_FIELDS = ["Strengths", "Weaknesses", "Questions", "Limitations"]


def load(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: review must be an object")
    return data


def numeric(data: dict, key: str):
    for candidate in (key, key.lower()):
        if candidate in data:
            try:
                return float(data[candidate])
            except (TypeError, ValueError):
                return None
    return None


def union_lists(reviews: list[dict], key: str) -> list[str]:
    seen: set[str] = set()
    values: list[str] = []
    for review in reviews:
        raw = review.get(key) or []
        if isinstance(raw, str):
            raw = [raw]
        for item in raw:
            text = str(item).strip()
            if text and text.lower() not in seen:
                seen.add(text.lower())
                values.append(text)
    return values


def aggregate(reviews: list[dict], stat: str = "mean") -> dict:
    if not reviews:
        raise ValueError("at least one review is required")

    result: dict = {}
    ensemble: dict = {"count": len(reviews), "axes": {}}

    for axis in AXES:
        values = [value for review in reviews if (value := numeric(review, axis)) is not None]
        if not values:
            continue
        mean = statistics.fmean(values)
        median = statistics.median(values)
        chosen = mean if stat == "mean" else median
        result[axis] = round(chosen, 2)
        ensemble["axes"][axis] = {
            "mean": round(mean, 3),
            "median": round(median, 3),
            "stdev": round(statistics.stdev(values), 3) if len(values) > 1 else 0.0,
            "values": values,
        }

    for key in LIST_FIELDS:
        result[key] = union_lists(reviews, key)

    summaries = []
    for review in reviews:
        summary = str(review.get("Summary") or "").strip()
        if summary and summary not in summaries:
            summaries.append(summary)
    result["Summary"] = " ".join(summaries) if summaries else ""

    decisions = [str(review.get("Decision") or "").strip().capitalize() for review in reviews]
    accepts = sum(1 for decision in decisions if decision == "Accept")
    rejects = sum(1 for decision in decisions if decision == "Reject")
    result["Decision"] = "Accept" if accepts > rejects else "Reject"
    result["ensemble"] = ensemble
    result["individual_decisions"] = decisions
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reviews", nargs="+", help="Review JSON files")
    parser.add_argument("--out", help="Write the aggregated review here")
    parser.add_argument("--stat", choices=["mean", "median"], default="mean")
    args = parser.parse_args()

    reviews = []
    try:
        for path in args.reviews:
            reviews.append(load(Path(path).expanduser()))
        result = aggregate(reviews, stat=args.stat)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    text = json.dumps(result, indent=2)
    if args.out:
        out = Path(args.out).expanduser()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
        print(f"Wrote aggregated review to {out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
