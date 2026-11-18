#!/usr/bin/env python3
"""Report the state of a PaperOrchestra project and the next runnable stage.

This script is intentionally read-only and dependency-free. It inspects the
artifact layout described in the paper-orchestra skill and prints a table plus
the next action. Exit code is 0 when the pipeline is complete, 2 when work
remains, and 1 when the project looks malformed.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def exists(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 0


def valid_json(path: Path) -> bool:
    try:
        json.loads(path.read_text(encoding="utf-8"))
        return True
    except (OSError, ValueError):
        return False


def inspect(root: Path) -> tuple[list[tuple[str, bool, str]], str]:
    raw = root / "raw_materials"
    template = root / "latex_template"
    lit = root / "literature_agent_output"
    writeup = root / "latex_writeup"
    refine = root / "content_refinement_workdir"

    checks: list[tuple[str, bool, str]] = [
        ("idea.md", exists(raw / "idea.md"), str(raw / "idea.md")),
        ("experimental_log.md", exists(raw / "experimental_log.md"), str(raw / "experimental_log.md")),
        ("template.tex", exists(template / "template.tex"), str(template / "template.tex")),
        ("guidelines.md", exists(template / "guidelines.md"), str(template / "guidelines.md")),
        ("outline.json", exists(root / "outline.json") and valid_json(root / "outline.json"), str(root / "outline.json")),
        ("literature registry", exists(lit / "registry.json") and valid_json(lit / "registry.json"), str(lit / "registry.json")),
        ("citation map", exists(lit / "citation_map.json") and valid_json(lit / "citation_map.json"), str(lit / "citation_map.json")),
        ("references.bib", exists(lit / "references.bib"), str(lit / "references.bib")),
        ("figures info", exists(root / "figures" / "info.json") and valid_json(root / "figures" / "info.json"), str(root / "figures" / "info.json")),
        ("merged template", exists(writeup / "template.tex"), str(writeup / "template.tex")),
        ("raw draft", exists(writeup / "raw_draft_paper.tex"), str(writeup / "raw_draft_paper.tex")),
        ("refinement workdir", refine.is_dir(), str(refine)),
        ("final tex", exists(root / "final_paper.tex"), str(root / "final_paper.tex")),
        ("final pdf", exists(root / "final_paper.pdf"), str(root / "final_paper.pdf")),
        ("metrics", any((root / "metrics").glob("*.json")) if (root / "metrics").is_dir() else False, str(root / "metrics")),
    ]

    status = {name: ok for name, ok, _ in checks}

    if not (status["idea.md"] and status["experimental_log.md"] and status["template.tex"]):
        return checks, "Stage 0: fix inputs, then run `paper-inputs`."

    if not status["outline.json"]:
        return checks, "Stage 1: run `paper-outline` to create outline.json."

    if not (status["literature registry"] and status["citation map"] and status["references.bib"]):
        return checks, "Stage 2a: run `paper-literature-review`."

    if not status["figures info"]:
        return checks, "Stage 2b: run `paper-plotting` (or supply raw_materials/figures/info.json)."

    if not status["merged template"]:
        return checks, "Merge: copy outline_v1.json, updated_template.tex, references.bib, and figures into latex_writeup/."

    if not status["raw draft"]:
        return checks, "Stage 3: run `paper-section-writing`."

    if not status["refinement workdir"]:
        return checks, "Stage 4: run `paper-content-refinement`."

    if not (status["final tex"] and status["final pdf"]):
        return checks, "Stage 4 incomplete: refine until final_paper.tex and final_paper.pdf exist."

    if not status["metrics"]:
        return checks, "Pipeline complete. Optional: run `paper-evaluation` for metrics."

    return checks, "Pipeline complete with metrics."


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", help="Path to the paper project directory")
    args = parser.parse_args()

    root = Path(args.project).expanduser().resolve()
    if not root.is_dir():
        print(f"error: {root} is not a directory", file=sys.stderr)
        return 1

    checks, next_action = inspect(root)
    print(f"PaperOrchestra project: {root}\n")
    width = max(len(name) for name, _, _ in checks)
    for name, ok, path in checks:
        mark = "PASS" if ok else "----"
        print(f"  [{mark}] {name:<{width}}  {path}")

    print(f"\nNext: {next_action}")
    return 0 if next_action.startswith("Pipeline complete") else 2


if __name__ == "__main__":
    raise SystemExit(main())
