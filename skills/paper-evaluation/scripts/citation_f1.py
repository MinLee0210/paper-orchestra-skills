#!/usr/bin/env python3
"""Compute citation precision, recall, and F1 between two registries.

Matching is by Semantic Scholar ID first, then by normalized title. P0/P1
recall is reported when priority labels or explicit ID sets are available.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


@dataclass
class Record:
    paper_id: str
    title: str
    title_key: str
    priority: str | None


def load_records(path: Path) -> tuple[list[Record], bool]:
    data = json.loads(path.read_text(encoding="utf-8"))
    p0_ids: list = []
    p1_ids: list = []

    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        p0_ids = data.get("p0_ids", []) or []
        p1_ids = data.get("p1_ids", []) or []
        items = data.get("papers") or data.get("citation_info") or []
        if not items and not p0_ids and not p1_ids:
            items = list(data.values())
    else:
        raise ValueError("registry must be a JSON array or object")

    p0_norm = {norm(token) for token in p0_ids if str(token).strip()}
    p1_norm = {norm(token) for token in p1_ids if str(token).strip()}

    records: list[Record] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or item.get("fetched_paper_title") or "")
        pid = str(item.get("paper_id") or item.get("paperId") or item.get("fetched_paper_id") or "")
        priority = item.get("priority")
        if priority not in {"P0", "P1"}:
            tokens = {norm(pid), norm(title)} - {""}
            if tokens & p0_norm:
                priority = "P0"
            elif tokens & p1_norm:
                priority = "P1"
            elif p0_norm and not p1_norm:
                priority = "P1"
            else:
                priority = None
        records.append(Record(pid, title, norm(title), priority))
    return records, bool(p0_norm or p1_norm)


def match(gt: list[Record], gen: list[Record]) -> dict[int, int]:
    pairs: dict[int, int] = {}
    gen_used: set[int] = set()

    # Pass 1: IDs
    for gi, g in enumerate(gt):
        if not g.paper_id:
            continue
        for gj, h in enumerate(gen):
            if gj in gen_used or not h.paper_id:
                continue
            if g.paper_id == h.paper_id:
                pairs[gi] = gj
                gen_used.add(gj)
                break

    # Pass 2: normalized titles
    for gi, g in enumerate(gt):
        if gi in pairs or not g.title_key:
            continue
        for gj, h in enumerate(gen):
            if gj in gen_used or not h.title_key:
                continue
            if g.title_key == h.title_key:
                pairs[gi] = gj
                gen_used.add(gj)
                break

    return pairs


def prf(tp: int, predicted: int, actual: int) -> dict:
    precision = tp / predicted if predicted else 0.0
    recall = tp / actual if actual else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "tp": tp,
        "predicted": predicted,
        "actual": actual,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gt", required=True, help="Ground-truth registry")
    parser.add_argument("--gen", required=True, help="Generated registry")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        gt, gt_explicit = load_records(Path(args.gt).expanduser())
        gen, _ = load_records(Path(args.gen).expanduser())
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    pairs = match(gt, gen)
    overall = prf(len(pairs), len(gen), len(gt))

    result: dict = {
        "gt_count": len(gt),
        "gen_count": len(gen),
        "matched": len(pairs),
        "overall": overall,
        "unmatched_gt": [g.title for i, g in enumerate(gt) if i not in pairs][:15],
        "unmatched_gen": [h.title for j, h in enumerate(gen) if j not in {v for v in pairs.values()}][:15],
    }

    has_priority = any(g.priority for g in gt) or gt_explicit
    if has_priority:
        for label in ("P0", "P1"):
            gt_indices = [i for i, g in enumerate(gt) if g.priority == label]
            matched = [i for i in gt_indices if i in pairs]
            result[label] = {
                "recall": round(len(matched) / len(gt_indices), 4) if gt_indices else 0.0,
                "matched": len(matched),
                "actual": len(gt_indices),
            }
        # Count how many generated papers map back to must-cite ground truth.
        matched_p0 = sum(1 for i in pairs if gt[i].priority == "P0")
        result["P0_share_of_matches"] = round(matched_p0 / len(pairs), 4) if pairs else 0.0

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"GT papers: {result['gt_count']}   Generated: {result['gen_count']}   Matched: {result['matched']}")
        print(f"Overall  P={overall['precision']:.3f}  R={overall['recall']:.3f}  F1={overall['f1']:.3f}")
        if has_priority:
            print(f"P0 recall: {result['P0']['recall']:.3f} ({result['P0']['matched']}/{result['P0']['actual']})")
            print(f"P1 recall: {result['P1']['recall']:.3f} ({result['P1']['matched']}/{result['P1']['actual']})")
        if result["unmatched_gt"]:
            print("\nUnmatched ground-truth papers (first 15):")
            for title in result["unmatched_gt"]:
                print(f"  - {title}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
