#!/usr/bin/env python3
"""Lint a generated LaTeX manuscript before refinement.

Checks:
  * balanced \\begin{...}/\\end{...} environments
  * citation keys against citation_map.json
  * \\includegraphics targets exist
  * references resolve to labels
  * duplicate labels
  * the cleverref typo
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

BEGIN = re.compile(r"\\begin\{([^}]+)\}")
END = re.compile(r"\\end\{([^}]+)\}")
LABEL = re.compile(r"\\label\{([^}]+)\}")
REF = re.compile(r"\\(?:ref|eqref|cref|Cref|autoref)\{([^}]+)\}")
CITE = re.compile(r"\\(?:no)?cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]*)\}")
GRAPHICS = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")


def strip_comments(text: str) -> str:
    lines = []
    for line in text.splitlines():
        out = []
        escaped = False
        for char in line:
            if char == "\\":
                escaped = not escaped
                out.append(char)
                continue
            if char == "%" and not escaped:
                break
            escaped = False
            out.append(char)
        lines.append("".join(out))
    return "\n".join(lines)


def lint(tex_path: Path, citation_map: Path | None) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    text = strip_comments(tex_path.read_text(encoding="utf-8", errors="ignore"))

    # Environments
    stack: list[tuple[str, int]] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for match in BEGIN.finditer(line):
            stack.append((match.group(1), lineno))
        for match in END.finditer(line):
            env = match.group(1)
            if not stack:
                errors.append(f"line {lineno}: \\end{{{env}}} without matching \\begin")
                continue
            open_env, open_line = stack.pop()
            if open_env != env:
                errors.append(
                    f"line {lineno}: \\end{{{env}}} closes \\begin{{{open_env}}} from line {open_line}"
                )
    for env, lineno in stack:
        errors.append(f"line {lineno}: \\begin{{{env}}} is never closed")

    if "cleverref" in text:
        errors.append("found 'cleverref'; the package is 'cleveref'")

    # Labels and references
    labels: dict[str, int] = {}
    for lineno, line in enumerate(text.splitlines(), 1):
        for match in LABEL.finditer(line):
            label = match.group(1)
            if label in labels:
                warnings.append(f"line {lineno}: duplicate label '{label}' (first at line {labels[label]})")
            labels[label] = lineno
    for lineno, line in enumerate(text.splitlines(), 1):
        for match in REF.finditer(line):
            for key in match.group(1).split(","):
                key = key.strip()
                if key and key not in labels:
                    warnings.append(f"line {lineno}: reference to undefined label '{key}'")

    # Citations
    cited: set[str] = set()
    for lineno, line in enumerate(text.splitlines(), 1):
        for match in CITE.finditer(line):
            for key in match.group(1).split(","):
                key = key.strip()
                if key:
                    cited.add(key)
    if citation_map and citation_map.exists():
        try:
            allowed = set(json.loads(citation_map.read_text(encoding="utf-8")))
        except ValueError as exc:
            errors.append(f"cannot parse citation map: {exc}")
            allowed = set()
        if allowed:
            unknown = sorted(cited - allowed)
            if unknown:
                errors.append(f"citations not in citation map: {', '.join(unknown[:20])}")
    elif cited:
        warnings.append("no citation map supplied; citation keys were not checked")

    # Graphics
    base_dirs = [tex_path.parent, tex_path.parent / "figures"]
    for lineno, line in enumerate(text.splitlines(), 1):
        for match in GRAPHICS.finditer(line):
            target = match.group(1).strip()
            if target.startswith(("http://", "https://")):
                warnings.append(f"line {lineno}: remote graphic '{target}'")
                continue
            exists = (tex_path.parent / target).exists() or any((d / Path(target).name).exists() for d in base_dirs)
            if not exists:
                errors.append(f"line {lineno}: missing graphic '{target}'")

    if "\\begin{document}" not in text:
        errors.append("missing \\begin{document}")
    if "\\end{document}" not in text:
        errors.append("missing \\end{document}")
    if "\\documentclass" not in text:
        errors.append("missing \\documentclass")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tex", help="LaTeX file to lint")
    parser.add_argument("--citation-map", help="citation_map.json")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    tex_path = Path(args.tex).expanduser().resolve()
    if not tex_path.exists():
        print(f"error: {tex_path} does not exist", file=sys.stderr)
        return 2
    citation_map = Path(args.citation_map).expanduser() if args.citation_map else None

    errors, warnings = lint(tex_path, citation_map)
    result = {"file": str(tex_path), "ok": not errors, "errors": errors, "warnings": warnings}
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for item in errors:
            print(f"ERROR   {item}")
        for item in warnings:
            print(f"WARNING {item}")
        print("OK" if result["ok"] else "FAILED")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
