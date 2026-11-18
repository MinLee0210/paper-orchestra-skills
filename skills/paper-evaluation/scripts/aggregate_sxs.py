#!/usr/bin/env python3
"""Aggregate side-by-side comparison outcomes into wins, ties, and losses."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CANDIDATE = {"candidate", "ours", "paper_1", "paper1", "a"}
BASELINE = {"baseline", "other", "paper_2", "paper2", "b"}
TIE = {"tie", "draw", "equal"}


def classify(winner: str) -> str | None:
    value = str(winner).strip().lower()
    if value in CANDIDATE:
        return "candidate"
    if value in BASELINE:
        return "baseline"
    if value in TIE:
        return "tie"
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", help="JSON list of comparison records")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        data = json.loads(Path(args.results).expanduser().read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if not isinstance(data, list):
        print("error: results must be a JSON list", file=sys.stderr)
        return 2

    counts = {"candidate": 0, "baseline": 0, "tie": 0}
    invalid = 0
    for item in data:
        if not isinstance(item, dict):
            invalid += 1
            continue
        winner = item.get("winner")
        label = classify(winner)
        if label is None:
            invalid += 1
            continue
        counts[label] += 1

    decided = counts["candidate"] + counts["baseline"]
    result = {
        "comparisons": len(data),
        "candidate_wins": counts["candidate"],
        "baseline_wins": counts["baseline"],
        "ties": counts["tie"],
        "invalid": invalid,
        "win_rate_excluding_ties": round(counts["candidate"] / decided, 4) if decided else None,
        "win_rate_including_ties": round(counts["candidate"] / len(data), 4) if data else None,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Comparisons: {result['comparisons']}")
        print(f"Candidate wins: {result['candidate_wins']}")
        print(f"Baseline wins:  {result['baseline_wins']}")
        print(f"Ties:           {result['ties']}")
        if result["win_rate_excluding_ties"] is not None:
            print(f"Win rate (excl. ties): {result['win_rate_excluding_ties']:.1%}")
        if invalid:
            print(f"Invalid records ignored: {invalid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
