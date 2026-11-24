#!/usr/bin/env python3
"""Turn a user-supplied BibTeX file into verification candidates.

A starting bibliography is never copied into the paper. Each entry becomes a
*targeted* candidate (title, year, first-author surname) that the literature
stage re-verifies with semantic_scholar.py. Only entries that verify reach the
final references.bib, so a wrong or invented entry in the user's file cannot
leak into the paper.

Example:
    python bib_to_candidates.py raw_materials/references.bib --out candidates.json
    python semantic_scholar.py enrich --candidates candidates.json --out registry.json --cutoff 2024-11
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ENTRY_START = re.compile(r"@(\w+)\s*([{(])\s*([^,\s]+)\s*,", re.IGNORECASE)
FIELD_START = re.compile(r"(\w+)\s*=\s*", re.IGNORECASE)
SKIP_TYPES = {"comment", "string", "preamble"}


def balanced(text: str, start: int, open_ch: str, close_ch: str) -> int:
    """Return the index just past the group that opens at text[start]."""
    depth = 0
    for index in range(start, len(text)):
        char = text[index]
        if char == "\\":
            continue
        if char == open_ch:
            depth += 1
        elif char == close_ch:
            depth -= 1
            if depth == 0:
                return index + 1
    return len(text)


def parse_fields(body: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    pos = 0
    while True:
        match = FIELD_START.search(body, pos)
        if not match:
            return fields
        name = match.group(1).lower()
        cursor = match.end()
        if cursor >= len(body):
            return fields
        if body[cursor] == "{":
            end = balanced(body, cursor, "{", "}")
            value = body[cursor + 1 : end - 1]
        elif body[cursor] == '"':
            end = body.find('"', cursor + 1)
            end = len(body) if end == -1 else end + 1
            value = body[cursor + 1 : end - 1]
        else:
            end = cursor
            while end < len(body) and body[end] not in ",\n":
                end += 1
            value = body[cursor:end]
        fields.setdefault(name, value.strip())
        pos = max(end, match.end())


def clean(value: str) -> str:
    value = re.sub(r"\\[a-zA-Z]+\*?", " ", value)  # \emph, \textbf, ...
    value = re.sub(r"[{}$\\]", "", value)
    return re.sub(r"\s+", " ", value).strip()


def surname(authors: str) -> str | None:
    first = re.split(r"\s+and\s+", authors.strip(), maxsplit=1)[0].strip()
    if not first:
        return None
    first = clean(first)
    if "," in first:
        last = first.split(",", 1)[0]
    else:
        last = first.split()[-1] if first.split() else ""
    last = re.sub(r"[^A-Za-z'\u00c0-\u024f -]", "", last).strip()
    return last or None


def parse_bib(text: str) -> tuple[list[dict], list[str]]:
    candidates: list[dict] = []
    skipped: list[str] = []
    for match in ENTRY_START.finditer(text):
        entry_type, opener, key = match.group(1).lower(), match.group(2), match.group(3)
        if entry_type in SKIP_TYPES:
            continue
        closer = "}" if opener == "{" else ")"
        end = balanced(text, match.start(2), opener, closer)
        fields = parse_fields(text[match.end() : end - 1])
        title = clean(fields.get("title", ""))
        if not title:
            skipped.append(f"{key}: no title")
            continue
        item: dict = {
            "title": title,
            "targeted": True,
            "section": "User-supplied bibliography",
            "reason": f"from user references.bib ({key})",
        }
        year = re.search(r"(1[89]|20)\d{2}", fields.get("year", "") or fields.get("date", ""))
        if year:
            item["year"] = int(year.group(0))
        author = surname(fields.get("author", ""))
        if author:
            item["author"] = author
        if "year" not in item and "author" not in item:
            skipped.append(f"{key}: no year or author, a targeted lookup could not confirm identity")
            continue
        candidates.append(item)
    return candidates, skipped


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("bib", help="BibTeX file supplied by the user")
    parser.add_argument("--out", help="Write candidates JSON here (default: stdout)")
    args = parser.parse_args()

    try:
        text = Path(args.bib).expanduser().read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        print(f"error: cannot read {args.bib}: {exc}", file=sys.stderr)
        return 2

    candidates, skipped = parse_bib(text)
    payload = json.dumps(candidates, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        out = Path(args.out).expanduser()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload, encoding="utf-8")
        print(f"Wrote {len(candidates)} candidates to {out}", file=sys.stderr)
    else:
        print(payload, end="")
    for item in skipped:
        print(f"  skip: {item}", file=sys.stderr)
    return 0 if candidates else 1


if __name__ == "__main__":
    raise SystemExit(main())
