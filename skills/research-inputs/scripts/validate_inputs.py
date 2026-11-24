#!/usr/bin/env python3
"""Validate PaperOrchestra raw materials and template inputs.

Leakage checks are blocking by default: a citation, an author identity, or a
result number in `idea.md` makes the validator exit non-zero. Use
`--warn-only` to audit without blocking.

Usage:
    python validate_inputs.py /path/to/paper_project
    python validate_inputs.py /path/to/paper_project --json
    python validate_inputs.py /path/to/paper_project --source-title "..."
    python validate_inputs.py /path/to/paper_project --warn-only

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
    (
        re.compile(r"\b[A-Z][A-Za-z'’-]+(?:\s+(?:and|&)\s+[A-Z][A-Za-z'’-]+)?\s+et\s+al\.?", re.IGNORECASE),
        "author citation with 'et al.'",
    ),
    (
        re.compile(r"\bet\s+al\.?\s*\(?\s*(?:19|20)\d{2}"),
        "author-year citation with 'et al.'",
    ),
    (
        re.compile(r"\b[A-Z][A-Za-z'’-]+(?:\s+(?:and|&)\s+[A-Z][A-Za-z'’-]+)?\s*,?\s*\(?\s*(?:19|20)\d{2}\s*\)?"),
        "author-year citation",
    ),
    (
        re.compile(r"\b(?:according to|proposed by|introduced by|by)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b"),
        "named author or attribution",
    ),
]

IDENTITY_PATTERNS = [
    (re.compile(r"corresponding author", re.IGNORECASE), "author metadata"),
    (re.compile(r"\bour (?:previous|prior|earlier) work\b", re.IGNORECASE), "self-referential authorship"),
    (re.compile(r"^\s*(?:authors?|affiliations?)\s*:", re.IGNORECASE | re.MULTILINE), "author/affiliation block"),
    (
        re.compile(r"\b(?:University|Institute|Laboratory|Department|Inc\.|Corporation)\b"),
        "institution or company name",
    ),
]

RESULT_LEAK_PATTERNS = [
    (re.compile(r"\b\d+(?:\.\d+)?\s*%"), "percentage result"),
    (
        re.compile(
            r"\b(?:accuracy|perplexity|exact[- ]match|win[- ]rate|pass@\d+)\b"
            r"[^.\n]{0,50}?\b\d+(?:\.\d+)?\b",
            re.IGNORECASE,
        ),
        "metric near a number",
    ),
    (
        re.compile(
            r"\b(?:mAP|mIoU|IoU|BLEU|ROUGE|METEOR|PSNR|SSIM|AUC|F1|f1)\b"
            r"[^.\n]{0,50}?\b\d+(?:\.\d+)?\b"
        ),
        "metric near a number",
    ),
    (
        re.compile(
            r"\b(?:achiev(?:e|es|ed|ing)|reach(?:es|ed)?|obtain(?:s|ed)?|improv(?:e|es|ed|ing)|"
            r"gain(?:s|ed)?|outperform(?:s|ed)?|surpass(?:es|ed)?|reduce(?:s|d)?|increase(?:s|d)?)\b"
            r"[^.\n]{0,40}?\b\d+(?:\.\d+)?\b",
            re.IGNORECASE,
        ),
        "result claim near a number",
    ),
    (re.compile(r"\b\d+(?:\.\d+)?\s*(?:±|\+/-)\s*\d+(?:\.\d+)?\b"), "mean and variance result"),
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


def scan_text(
    path: Path,
    patterns,
    label: str,
    level: str = "error",
    math_free: bool = False,
) -> list[dict]:
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
                        "level": level,
                        "file": str(path),
                        "line": lineno,
                        "message": f"{label}: {description}",
                        "excerpt": line.strip()[:160],
                    }
                )
    return issues


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def validate(root: Path, source_title: str | None = None) -> dict:
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

    idea = raw / "idea.md"
    log = raw / "experimental_log.md"

    if idea.exists():
        # Citations and identities are always leakage. Result numbers are only
        # leakage in the idea file; the experimental log is the place for them.
        errors.extend(scan_text(idea, CITATION_PATTERNS, "leakage", "error", math_free=True))
        errors.extend(scan_text(idea, IDENTITY_PATTERNS, "identity leak", "error"))
        errors.extend(scan_text(idea, RESULT_LEAK_PATTERNS, "result leakage", "error"))
        warnings.extend(scan_text(idea, RESULT_REFERENCE_PATTERNS, "de-contextualize this reference", "warning"))
        if source_title:
            if normalize(source_title) in normalize(idea.read_text(encoding="utf-8", errors="ignore")):
                errors.append(
                    {
                        "level": "error",
                        "file": str(idea),
                        "message": "source paper title appears in idea.md",
                    }
                )

    if log.exists():
        errors.extend(scan_text(log, CITATION_PATTERNS, "leakage", "error", math_free=True))
        errors.extend(scan_text(log, IDENTITY_PATTERNS, "identity leak", "error"))
        warnings.extend(scan_text(log, RESULT_REFERENCE_PATTERNS, "de-contextualize this reference", "warning"))
        if source_title:
            if normalize(source_title) in normalize(log.read_text(encoding="utf-8", errors="ignore")):
                errors.append(
                    {
                        "level": "error",
                        "file": str(log),
                        "message": "source paper title appears in experimental_log.md",
                    }
                )

    for path in (idea, log):
        if path.exists() and UNVERIFIED_PATTERN.search(path.read_text(encoding="utf-8", errors="ignore")):
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
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("project", help="Paper project directory")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    parser.add_argument("--warn-only", action="store_true", help="Downgrade errors to warnings and exit 0")
    parser.add_argument("--source-title", help="Source paper title to detect inside the inputs")
    args = parser.parse_args()

    root = Path(args.project).expanduser().resolve()
    if not root.is_dir():
        print(f"error: {root} is not a directory", file=sys.stderr)
        return 2

    result = validate(root, source_title=args.source_title)

    if args.warn_only:
        result["warnings"] = result["errors"] + result["warnings"]
        result["errors"] = []
        result["ok"] = True

    if args.strict and result["warnings"] and not args.warn_only:
        result["ok"] = False

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Validating {result['root']}")
        for item in result["errors"]:
            line = f":{item['line']}" if "line" in item else ""
            print(f"ERROR   {item['file']}{line}: {item['message']}")
            if item.get("excerpt"):
                print(f"        {item['excerpt']}")
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
