#!/usr/bin/env python3
"""Validate bibliography, citation map, outline candidates, and LaTeX citations."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

BIB_KEY = re.compile(r"@\w+\s*\{\s*([^,\s]+)\s*,")
CITE = re.compile(r"\\(?:no)?cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]*)\}")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


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


def collect_candidates(node, found: list[tuple[str, str]]):
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "citation_candidates" and isinstance(value, list):
                label = node.get("subsection_title") or node.get("section_title") or "unknown"
                for item in value:
                    found.append((str(item), str(label)))
            else:
                collect_candidates(value, found)
    elif isinstance(node, list):
        for item in node:
            collect_candidates(item, found)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dir", required=True, help="Directory with references.bib and citation_map.json")
    parser.add_argument("--outline", help="Outline JSON (outline_v1.json)")
    parser.add_argument("--template", help="LaTeX template to scan for cite commands")
    parser.add_argument("--registry", help="Verified registry JSON")
    parser.add_argument("--cutoff", help="YYYY-MM research cutoff")
    parser.add_argument("--min-papers", type=int, default=20)
    args = parser.parse_args()

    base = Path(args.dir).expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []

    bib_path = base / "references.bib"
    map_path = base / "citation_map.json"
    if not bib_path.exists():
        errors.append(f"missing {bib_path}")
    if not map_path.exists():
        errors.append(f"missing {map_path}")
    if errors:
        for item in errors:
            print(f"ERROR   {item}")
        return 1

    bib_text = bib_path.read_text(encoding="utf-8", errors="ignore")
    bib_keys = BIB_KEY.findall(bib_text)
    bib_set = set(bib_keys)
    if len(bib_keys) != len(bib_set):
        duplicates = sorted({k for k in bib_keys if bib_keys.count(k) > 1})
        errors.append(f"duplicate BibTeX keys: {', '.join(duplicates[:10])}")

    citation_map = load_json(map_path)
    if not isinstance(citation_map, dict):
        errors.append("citation_map.json must be an object keyed by citation key")
        citation_map = {}
    map_set = set(citation_map)

    missing_in_bib = sorted(map_set - bib_set)
    missing_in_map = sorted(bib_set - map_set)
    if missing_in_bib:
        errors.append(f"keys in citation_map but not in references.bib: {', '.join(missing_in_bib[:10])}")
    if missing_in_map:
        errors.append(f"keys in references.bib but not in citation_map: {', '.join(missing_in_map[:10])}")

    for key, meta in citation_map.items():
        if not meta.get("title"):
            warnings.append(f"{key}: missing title")
        if not meta.get("authors"):
            warnings.append(f"{key}: missing authors")
        if not meta.get("year"):
            warnings.append(f"{key}: missing year")
        if not meta.get("abstract"):
            warnings.append(f"{key}: missing abstract; the writer cannot describe it accurately")

    if args.outline:
        try:
            outline = load_json(Path(args.outline).expanduser())
        except (OSError, ValueError) as exc:
            errors.append(f"cannot read outline: {exc}")
            outline = None
        if outline is not None:
            candidates: list[tuple[str, str]] = []
            collect_candidates(outline, candidates)
            bad = [(key, label) for key, label in candidates if key not in map_set]
            if bad:
                for key, label in bad[:20]:
                    errors.append(f"outline candidate '{key}' in '{label}' is not in citation_map")
            if not candidates:
                warnings.append("outline has no citation_candidates; run inject_citations.py first")
            if len({k for k, _ in candidates}) < args.min_papers:
                warnings.append(
                    f"outline uses only {len({k for k, _ in candidates})} unique citation candidates "
                    f"(target >= {args.min_papers} for a full paper)"
                )

    if args.template:
        template = Path(args.template).expanduser()
        if not template.exists():
            errors.append(f"missing template: {template}")
        else:
            text = strip_comments(template.read_text(encoding="utf-8", errors="ignore"))
            cited: set[str] = set()
            for group in CITE.findall(text):
                for key in group.split(","):
                    key = key.strip()
                    if key:
                        cited.add(key)
            unknown = sorted(cited - map_set)
            if unknown:
                errors.append(f"LaTeX cites keys not in citation_map: {', '.join(unknown[:20])}")
            unused = sorted(map_set - cited)
            if unused:
                warnings.append(f"{len(unused)} verified papers are never cited (for example: {', '.join(unused[:10])})")
            if len(cited) < max(1, int(len(map_set) * 0.9)):
                warnings.append(
                    f"only {len(cited)}/{len(map_set)} verified papers are cited; the literature stage targets >= 90%"
                )
            if "cleverref" in text:
                errors.append("template contains 'cleverref'; the package is 'cleveref'")

    if args.registry:
        try:
            registry = load_json(Path(args.registry).expanduser())
        except (OSError, ValueError) as exc:
            errors.append(f"cannot read registry: {exc}")
            registry = []
        if isinstance(registry, dict):
            registry = list(registry.values())
        if isinstance(registry, list):
            titles: dict[str, int] = {}
            for paper in registry:
                if not isinstance(paper, dict):
                    continue
                title = re.sub(r"[^a-z0-9]", "", str(paper.get("title", "")).lower())
                if title:
                    titles[title] = titles.get(title, 0) + 1
            dupes = [t for t, count in titles.items() if count > 1]
            if dupes:
                warnings.append(f"registry has {len(dupes)} duplicated titles after normalization")
            if len(registry) < args.min_papers:
                warnings.append(f"registry has only {len(registry)} papers (target >= {args.min_papers})")
            if args.cutoff:
                try:
                    c_year, c_month = [int(x) for x in args.cutoff.split("-")[:2]]
                except ValueError:
                    errors.append(f"invalid cutoff: {args.cutoff}")
                    c_year = c_month = None
                if c_year is not None:
                    for paper in registry:
                        if not isinstance(paper, dict):
                            continue
                        pub = str(paper.get("publication_date") or "")
                        year = paper.get("year")
                        if pub[:7] and len(pub) >= 7:
                            try:
                                p_year, p_month = int(pub[:4]), int(pub[5:7])
                            except ValueError:
                                continue
                            if (p_year, p_month) >= (c_year, c_month):
                                errors.append(f"paper after cutoff: {paper.get('title')} ({pub})")
                        elif year:
                            try:
                                y = int(year)
                            except (ValueError, TypeError):
                                continue
                            if y > c_year:
                                errors.append(f"paper after cutoff: {paper.get('title')} ({year})")
                            elif y == c_year:
                                warnings.append(f"same-year paper without month: {paper.get('title')} ({year})")

    for item in errors:
        print(f"ERROR   {item}")
    for item in warnings:
        print(f"WARNING {item}")
    print(f"Checked {len(bib_set)} papers")
    print("OK" if not errors else "FAILED")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
