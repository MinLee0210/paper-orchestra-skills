#!/usr/bin/env python3
"""Apply PaperOrchestra's accept/reject rule to two review JSONs.

Accept when Overall increases, or when Overall ties and sub-axis gains are at
least as large as drops. Reject when Overall decreases, or when a tie hides a
net sub-axis degradation.

Exit codes: 0 accept, 3 reject, 2 invalid input.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

AXES = [
    "Originality", "Quality", "Clarity", "Significance", "Soundness",
    "Presentation", "Contribution",
]


def load(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("review must be a JSON object")
    return data


def number(data: dict, key: str) -> float | None:
    for candidate in (key, key.lower()):
        if candidate in data:
            try:
                return float(data[candidate])
            except (TypeError, ValueError):
                return None
    return None


def decide(before: dict, after: dict) -> dict:
    b_overall = number(before, "Overall")
    a_overall = number(after, "Overall")
    if b_overall is None or a_overall is None:
        raise ValueError("both reviews need an Overall score")

    deltas = {}
    gain = 0.0
    drop = 0.0
    for axis in AXES:
        b = number(before, axis)
        a = number(after, axis)
        if b is None or a is None:
            continue
        delta = a - b
        deltas[axis] = delta
        if delta > 0:
            gain += delta
        elif delta < 0:
            drop += abs(delta)

    if a_overall > b_overall:
        decision = "ACCEPT"
        reason = "overall score increased"
    elif a_overall < b_overall:
        decision = "REJECT"
        reason = "overall score decreased"
    elif drop > gain:
        decision = "REJECT"
        reason = "overall tied but sub-axes degraded (drop > gain)"
    else:
        decision = "ACCEPT"
        reason = "overall tied with non-negative sub-axis progress"

    return {
        "decision": decision,
        "reason": reason,
        "overall_before": b_overall,
        "overall_after": a_overall,
        "deltas": deltas,
        "total_gain": gain,
        "total_drop": drop,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", required=True)
    parser.add_argument("--after", required=True)
    args = parser.parse_args()

    try:
        before = load(Path(args.before).expanduser())
        after = load(Path(args.after).expanduser())
        result = decide(before, after)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2))
    return 0 if result["decision"] == "ACCEPT" else 3


if __name__ == "__main__":
    raise SystemExit(main())
