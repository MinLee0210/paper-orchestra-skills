#!/usr/bin/env python3
"""Build references.bib and citation_map.json from a verified registry."""

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


def unique_key(base: str, seen: set[str]) -> str:
    if base not in seen:
        seen.add(base)
        return base
    for index in range(1, 1000):
        suffix = chr(ord("a") + index - 1) if index <= 26 else str(index)
        candidate = f"{base}{suffix}"
        if candidate not in seen:
            seen.add(candidate)
            return candidate
    raise RuntimeError(f"cannot uniquify citation key {base}")


def clean(value) -> str:
    return str(value or "").replace("\n", " ").strip()


def bib_entry(paper: dict) -> str:
    key = paper["citation_key"]
    authors = " and ".join(clean(a) for a in paper.get("authors", []) if clean(a)) or "Unknown"
    title = clean(paper.get("title"))
    year = clean(paper.get("year"))
    journal = clean(paper.get("journal"))
    venue = clean(paper.get("venue")) or "arXiv"
    entry_type = "article" if journal else "inproceedings"

    fields = [
        f"  title = {{{title}}}",
        f"  author = {{{authors}}}",
    ]
    if journal:
        fields.append(f"  journal = {{{journal}}}")
    else:
        fields.append(f"  booktitle = {{{venue}}}")
    fields.append(f"  year = {{{year}}}")
    if paper.get("volume"):
        fields.append(f"  volume = {{{clean(paper['volume'])}}}")
    if paper.get("pages"):
        fields.append(f"  pages = {{{clean(paper['pages'])}}}")
    return f"@{entry_type}{{{key},\n" + ",\n".join(fields) + "\n}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", required=True, help="Verified registry JSON")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--require-abstract", action="store_true", help="Drop papers without an abstract")
    args = parser.parse_args()

    try:
        papers = as_list(json.loads(Path(args.registry).expanduser().read_text(encoding="utf-8")))
    except (OSError, ValueError) as exc:
        print(f"error: cannot read registry: {exc}", file=sys.stderr)
        return 2

    seen: set[str] = set()
    entries: list[str] = []
    citation_map: dict[str, dict] = {}
    dropped = 0

    for paper in papers:
        if args.require_abstract and not paper.get("abstract"):
            dropped += 1
            continue
        base = paper.get("citation_key")
        if not base:
            print(f"warning: skipping paper without citation_key: {paper.get('title')}", file=sys.stderr)
            continue
        paper["citation_key"] = unique_key(base, seen)
        entries.append(bib_entry(paper))
        citation_map[paper["citation_key"]] = {
            "citation_key": paper["citation_key"],
            "title": clean(paper.get("title")),
            "authors": paper.get("authors", []),
            "venue": clean(paper.get("venue")),
            "year": paper.get("year"),
            "abstract": clean(paper.get("abstract")),
            "source": paper.get("source"),
            "doi": paper.get("doi"),
        }

    out = Path(args.out).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    (out / "references.bib").write_text("\n\n".join(entries) + ("\n" if entries else ""), encoding="utf-8")
    (out / "citation_map.json").write_text(json.dumps(citation_map, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Wrote {len(entries)} entries to {out / 'references.bib'}")
    print(f"Wrote {len(citation_map)} keys to {out / 'citation_map.json'}")
    if dropped:
        print(f"Dropped {dropped} papers without abstracts")
    return 0 if entries else 1


if __name__ == "__main__":
    raise SystemExit(main())
