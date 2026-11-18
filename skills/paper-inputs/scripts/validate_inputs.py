#!/usr/bin/env python3
"""Validate PaperOrchestra raw materials and template inputs.

Usage:
    python validate_inputs.py /path/to/paper_project
    python validate_inputs.py /path/to/paper_project --json

Exit codes:
    0  no blocking errors
    1  blocking errors found
    2  usage error
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

CITATION_PATTERNS = [
    (re.compile(r"\\cite[a-zA-Z]*\s*\{"), "LaTeX citation command"),
    (re.compile(r"\[\d+(?:\s*[,;]\s*\d+)*\]"), "bracketed citation such as [12]"),
    (re.compile(r"\barxiv\s*:\s*\d{4}\.\d{4,5}", re.IGNORECASE), "arXiv identifier"),
    (re.compile(r"\bdoi\s*:\s*10\.\d{4,9}", re.IGNORECASE), "DOI"),
    (re.compile(r"https?://", re.IGNORECASE), "URL"),
]

IDENTITY_PATTERNS = [
    (re.compile(r"corresponding author", re.IGNORECASE), "author metadata"),
    (re.compile(r"\bour (?:previous|prior|earlier) work\b", re.IGNORECASE), "self-referential authorship"),
    (re.compile(r"^\s*(?:authors?|affiliations?)\s*:", re.IGNORECASE | re.MULTILINE), "author/affiliation block"),
]

RESULT_REFERENCE_PATTERNS = [
    (re.compile(r"\b(?:Figure|Fig\.)\s*\d+", re.IGNORECASE), "reference to a numbered figure"),
    (re.compile(r"\bTable\s*\d+", re.IGNORECASE), "reference to a numbered table"),
]

UNVERIFIED_PATTERN = re.compile(r"UNVERIFIED\s*:", re.IGNORECASE)


def strip_math(line: str) -> str:
    line = re.sub(r"\$\$.*?\$\$", " ", line)
    line = re.sub(r"\$[^$]*\$", " ", line)
    line = re.sub(r"\\\(.*?\\\)", " ", line)
    line = re.sub(r"\\\[.*?\\\]", " ", line)
    return line


def scan_text(path: Path, patterns, label: str, math_free: bool = False) -> list[dict]:
    issues: list[dict] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [{"level": "error", "file": str(path), "message": f"cannot read: {exc}"}]

    for lineno, line in enumerate(text.splitlines(), 1):
        haystack = strip_math(line) if math_free else line
        for pattern, description in patterns:
            if pattern.search(haystack):
                issues.append(
                    {
                        "level": "warning",
                        "file": str(path),
                        "line": lineno,
                        "message": f"{label}: {description}",
                        "excerpt": line.strip()[:160],
                    }
                )
    return issues


def validate(root: Path) -> dict:
    errors: list[dict] = []
    warnings: list[dict] = []
    info: list[dict] = []

    raw = root / "raw_materials"
    template = root / "latex_template"

    required = {
        "raw_materials/idea.md": raw / "idea.md",
        "raw_materials/experimental_log.md": raw / "experimental_log.md",
        "latex_template/template.tex": template / "template.tex",
        "latex_template/guidelines.md": template / "guidelines.md",
    }
    for label, path in required.items():
        if not path.exists():
            errors.append({"level": "error", "file": str(path), "message": f"missing required file: {label}"})
        elif path.stat().st_size == 0:
            errors.append({"level": "error", "file": str(path), "message": f"empty required file: {label}"})

    for name in ("idea.md", "experimental_log.md"):
        path = raw / name
        if path.exists():
            warnings.extend(scan_text(path, CITATION_PATTERNS, "possible leakage", math_free=True))
            warnings.extend(scan_text(path, IDENTITY_PATTERNS, "possible identity leak"))
            warnings.extend(scan_text(path, RESULT_REFERENCE_PATTERNS, "de-contextualize this reference"))
            if UNVERIFIED_PATTERN.search(path.read_text(encoding="utf-8", errors="ignore")):
                info.append({"level": "info", "file": str(path), "message": "contains UNVERIFIED values; confirm before writing"})

    figures = raw / "figures"
    info_json = figures / "info.json"
    if info_json.exists():
        try:
            entries = json.loads(info_json.read_text(encoding="utf-8"))
        except ValueError as exc:
            errors.append({"level": "error", "file": str(info_json), "message": f"invalid JSON: {exc}"})
            entries = []
        if not isinstance(entries, list):
            errors.append({"level": "error", "file": str(info_json), "message": "info.json must be a list"})
            entries = []
        for idx, entry in enumerate(entries):
            if not isinstance(entry, dict) or "name" not in entry:
                errors.append({"level": "error", "file": str(info_json), "message": f"entry {idx} must contain 'name'"})
                continue
            figure_path = figures / str(entry["name"])
            if not figure_path.exists():
                errors.append({"level": "error", "file": str(figure_path), "message": f"figure listed in info.json does not exist: {entry['name']}"})
            if not entry.get("caption"):
                warnings.append({"level": "warning", "file": str(info_json), "message": f"figure {entry['name']} has no caption"})
    elif figures.exists() and any(p for p in figures.iterdir() if p.is_file()):
        warnings.append({"level": "warning", "file": str(figures), "message": "figures exist but figures/info.json is missing"})

    template_tex = template / "template.tex"
    if template_tex.exists():
        text = template_tex.read_text(encoding="utf-8", errors="ignore")
        if "\\documentclass" not in text:
            errors.append({"level": "error", "file": str(template_tex), "message": "template.tex has no \\documentclass"})
        if "\\begin{document}" not in text:
            errors.append({"level": "error", "file": str(template_tex), "message": "template.tex has no \\begin{document}"})
        if "\\end{document}" not in text:
            errors.append({"level": "error", "file": str(template_tex), "message": "template.tex has no \\end{document}"})

    return {
        "root": str(root),
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "ok": not errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", help="Paper project directory")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    args = parser.parse_args()

    root = Path(args.project).expanduser().resolve()
    if not root.is_dir():
        print(f"error: {root} is not a directory", file=sys.stderr)
        return 2

    result = validate(root)
    if args.strict and result["warnings"]:
        result["ok"] = False

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Validating {result['root']}")
        for item in result["errors"]:
            print(f"ERROR   {item['file']}: {item['message']}")
        for item in result["warnings"]:
            line = f":{item['line']}" if "line" in item else ""
            print(f"WARNING {item['file']}{line}: {item['message']}")
            if item.get("excerpt"):
                print(f"        {item['excerpt']}")
        for item in result["info"]:
            print(f"INFO    {item['file']}: {item['message']}")
        print("OK" if result["ok"] else "FAILED")

    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
