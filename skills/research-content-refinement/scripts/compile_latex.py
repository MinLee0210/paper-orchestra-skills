#!/usr/bin/env python3
"""Compile a LaTeX paper deterministically.

Runs pdflatex (or xelatex) plus bibtex/biber and enough reruns to settle
references. Writes <name>.compile.json with the command log and any
undefined citation/reference warnings.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

UNDEFINED = re.compile(r"(?:Citation|Reference) [`'][^']*' (?:on page \d+ )?undefined", re.IGNORECASE)


def run(command: list[str], cwd: Path, timeout: int, env: dict) -> dict:
    try:
        result = subprocess.run(
            command, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=env
        )
        return {
            "command": " ".join(command),
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.TimeoutExpired:
        return {"command": " ".join(command), "returncode": None, "error": f"timeout after {timeout}s"}
    except OSError as exc:
        return {"command": " ".join(command), "returncode": None, "error": str(exc)}


def page_count(pdf: Path):
    try:
        import pymupdf  # type: ignore
    except ImportError:
        try:
            import fitz  # type: ignore
            pymupdf = fitz
        except ImportError:
            return None
    try:
        with pymupdf.open(pdf) as doc:
            return doc.page_count
    except Exception:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", help="Directory containing the .tex file")
    parser.add_argument("--name", default="paper", help="Base name without .tex")
    parser.add_argument("--engine", choices=["pdflatex", "xelatex"], default="pdflatex")
    parser.add_argument("--biber", action="store_true", help="Use biber instead of bibtex")
    parser.add_argument("--no-bib", action="store_true", help="Skip the bibliography step")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout per command in seconds")
    parser.add_argument("--strict", action="store_true", help="Fail on undefined citations/references")
    parser.add_argument("--clean", action="store_true", help="Remove aux files after a successful build")
    parser.add_argument("--json", action="store_true", help="Print the compile report to stdout")
    args = parser.parse_args()

    cwd = Path(args.directory).expanduser().resolve()
    tex = cwd / f"{args.name}.tex"
    pdf = cwd / f"{args.name}.pdf"
    if not tex.exists():
        print(f"error: {tex} does not exist", file=sys.stderr)
        return 2

    engine = shutil.which(args.engine)
    if not engine:
        print(f"error: {args.engine} is not installed or not on PATH", file=sys.stderr)
        return 2

    if pdf.exists():
        pdf.unlink()

    env = dict(os.environ)
    for var in ("TEXINPUTS", "TEXMFHOME", "TEXMF", "TEXMFVAR", "TEXMFCONFIG"):
        env.pop(var, None)

    commands: list[list[str]] = [
        [args.engine, "-interaction=nonstopmode", "-halt-on-error", f"{args.name}.tex"]
    ]
    if not args.no_bib:
        commands.append([("biber" if args.biber else "bibtex"), args.name])
    commands.extend(
        [
            [args.engine, "-interaction=nonstopmode", "-halt-on-error", f"{args.name}.tex"],
            [args.engine, "-interaction=nonstopmode", "-halt-on-error", f"{args.name}.tex"],
        ]
    )

    logs = []
    undefined: list[str] = []
    for command in commands:
        log = run(command, cwd, args.timeout, env)
        logs.append(log)
        blob = f"{log.get('stdout', '')}\n{log.get('stderr', '')}"
        # Only the final pass matters; earlier passes legitimately report
        # citations that BibTeX has not resolved yet.
        undefined = []
        for line in UNDEFINED.findall(blob):
            if line not in undefined:
                undefined.append(line)
        if log.get("returncode") not in (0, None):
            # pdflatex may return nonzero on warnings; keep going only if no fatal error.
            if "Fatal error" in blob or "Emergency stop" in blob:
                break

    success = pdf.exists() and pdf.stat().st_size > 0
    report = {
        "tex": str(tex),
        "pdf": str(pdf) if success else None,
        "success": success,
        "pages": page_count(pdf) if success else None,
        "undefined": undefined,
        "commands": logs,
    }
    (cwd / f"{args.name}.compile.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps({k: v for k, v in report.items() if k != "commands"}, indent=2))
    else:
        print(f"Built {pdf}" if success else "Build failed: no PDF produced")
        if report["pages"]:
            print(f"Pages: {report['pages']}")
        if undefined:
            print(f"Undefined citations/references: {len(undefined)}")
            for item in undefined[:10]:
                print(f"  {item}")
        if not success:
            for log in logs:
                if log.get("returncode") not in (0, None) or log.get("error"):
                    print(f"\n---> {log['command']}")
                    if log.get("error"):
                        print(log["error"])
                    tail = (log.get("stdout") or "").strip().splitlines()[-30:]
                    if tail:
                        print("\n".join(tail))

    if args.clean and success:
        for suffix in (".aux", ".blg", ".out", ".toc", ".synctex.gz"):
            candidate = cwd / f"{args.name}{suffix}"
            if candidate.exists():
                candidate.unlink()

    if not success:
        return 1
    if args.strict and undefined:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
