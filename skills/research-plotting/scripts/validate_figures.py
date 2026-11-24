#!/usr/bin/env python3
"""Validate generated figures and their manifest."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

IMAGE_SUFFIXES = {".pdf", ".png", ".jpg", ".jpeg", ".svg"}


def check(root: Path, figures_dir: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    info_path = figures_dir / "info.json"
    entries = []
    if info_path.exists():
        try:
            entries = json.loads(info_path.read_text(encoding="utf-8"))
        except ValueError as exc:
            errors.append(f"{info_path}: invalid JSON: {exc}")
            entries = []
        if not isinstance(entries, list):
            errors.append(f"{info_path}: must be a list")
            entries = []
    else:
        errors.append(f"{info_path}: missing (the writer needs name/caption pairs)")

    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"{info_path}[{idx}]: must be an object")
            continue
        name = entry.get("name")
        if not name:
            errors.append(f"{info_path}[{idx}]: missing name")
            continue
        path = figures_dir / name
        if not path.exists():
            errors.append(f"missing figure file: {path}")
        elif path.stat().st_size == 0:
            errors.append(f"empty figure file: {path}")
        if path.suffix.lower() not in IMAGE_SUFFIXES:
            warnings.append(f"unusual figure extension: {path.suffix}")
        if not entry.get("caption"):
            warnings.append(f"figure has no caption: {name}")
        if path.suffix.lower() == ".pdf":
            preview = path.with_suffix(".png")
            if not preview.exists():
                warnings.append(f"no PNG preview for review: {preview.name}")

    results_path = root / "plotting_results.json"
    if results_path.exists():
        try:
            results = json.loads(results_path.read_text(encoding="utf-8"))
        except ValueError as exc:
            errors.append(f"{results_path}: invalid JSON: {exc}")
            results = []
        if not isinstance(results, list):
            errors.append(f"{results_path}: must be a list")
        else:
            for idx, item in enumerate(results):
                if isinstance(item, dict) and item.get("status") == "skipped" and not item.get("notes"):
                    warnings.append(f"plotting_results[{idx}] skipped without a reason")

    if not entries and not errors:
        warnings.append("no figures registered")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", help="Paper project directory")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path(args.project).expanduser().resolve()
    figures_dir = root / "figures"
    if not root.is_dir():
        print(f"error: {root} is not a directory", file=sys.stderr)
        return 2
    if not figures_dir.is_dir():
        print(f"error: {figures_dir} does not exist", file=sys.stderr)
        return 2

    errors, warnings = check(root, figures_dir)
    result = {"root": str(root), "ok": not errors, "errors": errors, "warnings": warnings}
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
