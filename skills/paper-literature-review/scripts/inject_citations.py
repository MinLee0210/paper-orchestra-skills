#!/usr/bin/env python3
"""Attach verified citation keys to an outline and remove raw citation hints."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def as_list(data) -> list[dict]:
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        return [x for x in data.values() if isinstance(x, dict)]
    raise ValueError("registry must be a JSON array or object")


def group_keys(registry: list[dict]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {}
    for paper in registry:
        section = paper.get("found_in_section") or "General"
        key = paper.get("citation_key")
        if key:
            grouped.setdefault(section, []).append(key)
    return grouped


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outline", required=True)
    parser.add_argument("--registry", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    try:
        outline = json.loads(Path(args.outline).expanduser().read_text(encoding="utf-8"))
        registry = as_list(json.loads(Path(args.registry).expanduser().read_text(encoding="utf-8")))
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not isinstance(outline, dict):
        print("error: outline must be an object", file=sys.stderr)
        return 2

    grouped = group_keys(registry)
    empty_sections: list[str] = []
    used_sections: set[str] = set()

    plan = outline.get("intro_related_work_plan", {}) or {}
    intro = plan.get("introduction_strategy", {}) or {}
    intro_keys = sorted(set(grouped.get("Introduction", [])))
    intro["citation_candidates"] = intro_keys
    used_sections.add("Introduction")
    if not intro_keys:
        empty_sections.append("Introduction")

    related = plan.get("related_work_strategy", {}) or {}
    for sub in related.get("subsections", []) or []:
        title = sub.get("subsection_title", "General")
        keys = sorted(set(grouped.get(f"Related Work: {title}", [])))
        sub["citation_candidates"] = keys
        used_sections.add(f"Related Work: {title}")
        if not keys:
            empty_sections.append(f"Related Work: {title}")

    for section in outline.get("section_plan", []) or []:
        section_title = section.get("section_title", "Unknown Section")
        for sub in section.get("subsections", []) or []:
            sub_title = sub.get("subsection_title", "General")
            keys = sorted(set(grouped.get(f"{section_title} - {sub_title}", [])))
            sub["citation_candidates"] = keys
            used_sections.add(f"{section_title} - {sub_title}")
            sub.pop("citation_hints", None)
            if not keys:
                empty_sections.append(f"{section_title} - {sub_title}")

    out = Path(args.out).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(outline, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    used = sum(len(v) for v in grouped.values())
    print(f"Attached {used} citation keys across {len(grouped)} sections to {out}")
    if empty_sections:
        print("Sections with no verified citations:")
        for name in empty_sections:
            print(f"  - {name}")
    unused = sorted(set(grouped) - used_sections)
    if unused:
        print("Registry sections that matched no outline node (check title spelling):")
        for name in unused:
            print(f"  - {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
