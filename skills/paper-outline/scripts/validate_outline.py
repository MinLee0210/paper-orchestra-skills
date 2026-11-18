#!/usr/bin/env python3
"""Structural validation for PaperOrchestra outline.json."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ASPECT_RATIOS = {
    "1:1", "1:4", "2:3", "3:2", "3:4", "4:1", "4:3",
    "4:5", "5:4", "9:16", "16:9", "21:9",
}


def validate(data: object) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(data, dict):
        return ["outline must be a JSON object"], warnings

    for key in ("plotting_plan", "intro_related_work_plan", "section_plan"):
        if key not in data:
            errors.append(f"missing top-level key: {key}")

    plan = data.get("plotting_plan", [])
    if not isinstance(plan, list):
        errors.append("plotting_plan must be an array")
    else:
        if not plan:
            warnings.append("plotting_plan is empty")
        for idx, fig in enumerate(plan):
            if not isinstance(fig, dict):
                errors.append(f"plotting_plan[{idx}] must be an object")
                continue
            for field in ("figure_id", "title", "plot_type", "data_source", "objective", "aspect_ratio"):
                if not fig.get(field):
                    errors.append(f"plotting_plan[{idx}] missing {field}")
            if fig.get("plot_type") not in {"plot", "diagram"}:
                errors.append(f"plotting_plan[{idx}].plot_type must be 'plot' or 'diagram'")
            if fig.get("data_source") not in {"idea.md", "experimental_log.md", "both"}:
                errors.append(f"plotting_plan[{idx}].data_source has invalid value")
            if fig.get("aspect_ratio") not in ASPECT_RATIOS:
                errors.append(f"plotting_plan[{idx}].aspect_ratio has invalid value")
            if "figure" in str(fig.get("figure_id", "")).lower():
                warnings.append(f"plotting_plan[{idx}].figure_id contains the word 'figure'")

    intro = data.get("intro_related_work_plan", {})
    if not isinstance(intro, dict):
        errors.append("intro_related_work_plan must be an object")
        intro = {}
    intro_strat = intro.get("introduction_strategy", {})
    if not isinstance(intro_strat, dict):
        errors.append("introduction_strategy must be an object")
        intro_strat = {}
    for field in ("hook_hypothesis", "problem_gap_hypothesis"):
        if not intro_strat.get(field):
            errors.append(f"introduction_strategy missing {field}")
    directions = intro_strat.get("search_directions", [])
    if not isinstance(directions, list) or len(directions) < 3:
        warnings.append("introduction_strategy should have at least 3 search_directions")
    rw = intro.get("related_work_strategy", {})
    if not isinstance(rw, dict):
        errors.append("related_work_strategy must be an object")
        rw = {}
    clusters = rw.get("subsections", [])
    if not isinstance(clusters, list) or not clusters:
        errors.append("related_work_strategy.subsections must be a non-empty array")
        clusters = []
    for idx, cluster in enumerate(clusters):
        if not isinstance(cluster, dict):
            errors.append(f"related_work_strategy.subsections[{idx}] must be an object")
            continue
        for field in (
            "subsection_title", "methodology_cluster", "sota_investigation_mission",
            "limitation_hypothesis", "bridge_to_our_method",
        ):
            if not cluster.get(field):
                errors.append(f"related_work_strategy.subsections[{idx}] missing {field}")
        if len(cluster.get("limitation_search_queries", []) or []) < 2:
            warnings.append(f"related_work_strategy.subsections[{idx}] should have at least 2 queries")

    sections = data.get("section_plan", [])
    if not isinstance(sections, list) or not sections:
        errors.append("section_plan must be a non-empty array")
        sections = []
    hint_count = 0
    for idx, section in enumerate(sections):
        if not isinstance(section, dict):
            errors.append(f"section_plan[{idx}] must be an object")
            continue
        if not section.get("section_title"):
            errors.append(f"section_plan[{idx}] missing section_title")
        subsections = section.get("subsections", [])
        if not isinstance(subsections, list) or not subsections:
            errors.append(f"section_plan[{idx}] must have at least one subsection")
            continue
        for j, sub in enumerate(subsections):
            if not isinstance(sub, dict):
                errors.append(f"section_plan[{idx}].subsections[{j}] must be an object")
                continue
            if not sub.get("subsection_title"):
                errors.append(f"section_plan[{idx}].subsections[{j}] missing subsection_title")
            if not isinstance(sub.get("content_bullets"), list) or not sub.get("content_bullets"):
                errors.append(f"section_plan[{idx}].subsections[{j}] needs content_bullets")
            hints = sub.get("citation_hints", [])
            if not isinstance(hints, list):
                errors.append(f"section_plan[{idx}].subsections[{j}].citation_hints must be an array")
            else:
                hint_count += len(hints)

    if hint_count == 0:
        warnings.append("no citation_hints anywhere; the literature stage will have nothing targeted to verify")
    elif hint_count < 10:
        warnings.append(f"only {hint_count} citation hints; full papers usually need more")

    titles = {str(s.get("section_title", "")).lower() for s in sections if isinstance(s, dict)}
    if not any("introduction" in title for title in titles):
        warnings.append("no Introduction section in section_plan")
    if not any("related work" in title or "related" in title for title in titles):
        warnings.append("no Related Work section in section_plan")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("outline", help="Path to outline.json")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    path = Path(args.outline).expanduser().resolve()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"error: cannot read {path}: {exc}", file=sys.stderr)
        return 2

    errors, warnings = validate(data)
    result = {"file": str(path), "ok": not errors, "errors": errors, "warnings": warnings}
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Validating {path}")
        for item in errors:
            print(f"ERROR   {item}")
        for item in warnings:
            print(f"WARNING {item}")
        print("OK" if result["ok"] else "FAILED")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
