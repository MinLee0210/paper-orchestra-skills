#!/usr/bin/env python3
"""Copy a bundled conference template into a project directory."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets" / "templates"
REQUIRED = ["template.tex", "guidelines.md", "references.bib"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--venue", help="Template key, e.g. cvpr2025")
    parser.add_argument("--out", help="Destination directory")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing non-empty directory")
    parser.add_argument("--list", action="store_true", help="List bundled venues and exit")
    args = parser.parse_args()

    if args.list:
        for path in sorted(ASSETS.iterdir()) if ASSETS.is_dir() else []:
            if path.is_dir():
                print(path.name)
        return 0

    if not args.venue or not args.out:
        parser.error("--venue and --out are required unless --list is used")

    source = ASSETS / args.venue
    if not source.is_dir():
        available = ", ".join(sorted(p.name for p in ASSETS.iterdir() if p.is_dir()))
        print(f"error: unknown venue '{args.venue}'. Available: {available}", file=sys.stderr)
        return 2

    dest = Path(args.out).expanduser().resolve()
    if dest.exists() and any(dest.iterdir()) and not args.force:
        print(f"error: {dest} is not empty (use --force to overwrite)", file=sys.stderr)
        return 2

    dest.mkdir(parents=True, exist_ok=True)

    if args.force and dest.exists():
        for child in dest.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()

    for item in sorted(source.iterdir()):
        target = dest / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)

    missing = [name for name in REQUIRED if not (dest / name).exists()]
    print(f"Copied {args.venue} -> {dest}")
    for item in sorted(dest.iterdir()):
        print(f"  {item.name}")
    if missing:
        print(f"error: missing required files: {', '.join(missing)}", file=sys.stderr)
        return 1
    print("Template contract satisfied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
