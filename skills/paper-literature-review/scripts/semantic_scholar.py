#!/usr/bin/env python3
"""Search and verify papers with the Semantic Scholar Graph API.

Examples:
    python semantic_scholar.py search --title "Attention Is All You Need" --year 2017
    python semantic_scholar.py enrich --candidates candidates.json --out registry.json --cutoff 2024-11

The registry format is documented in the paper-literature-review skill.
"""

from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

API_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
FIELDS = "paperId,title,authors,venue,year,abstract,citationCount,journal,publicationDate,externalIds"
USER_AGENT = "paper-orchestra-skills/1.0 (+https://github.com/MinLee0210/paper-orchestra-skills)"
STOPWORDS = {
    "the", "a", "an", "in", "on", "at", "for", "to", "of", "and", "is",
    "are", "with", "by", "study",
}


def norm_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]", "", title.lower())


def fuzzy(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio() * 100.0


def parse_cutoff(value: str | None) -> date | None:
    if not value:
        return None
    parts = value.split("-")
    if len(parts) < 2:
        raise ValueError("cutoff must be YYYY-MM")
    return date(int(parts[0]), int(parts[1]), 1)


def before_cutoff(entry: dict, cutoff: date | None) -> bool:
    if cutoff is None:
        return True
    pub = entry.get("publicationDate")
    if pub:
        try:
            parts = [int(p) for p in str(pub).split("-")]
            while len(parts) < 3:
                parts.append(1)
            return date(parts[0], parts[1], parts[2]) < cutoff
        except (ValueError, TypeError):
            pass
    year = entry.get("year")
    if not year:
        return True
    try:
        year = int(year)
    except (ValueError, TypeError):
        return True
    if year < cutoff.year:
        return True
    if year > cutoff.year:
        return False
    # Same year without a parseable month: permissive, documented in citation-policy.md.
    return True


def citation_key(authors: list, year, title: str) -> str:
    if authors:
        first = authors[0].split()[-1] if authors[0].split() else "Unknown"
    else:
        first = "Unknown"
    clean_author = re.sub(r"[^a-zA-Z]", "", first).capitalize() or "Unknown"
    year_str = str(year) if year else "2024"
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", "", (title or "Paper").lower())
    words = [w.capitalize() for w in cleaned.split() if w not in STOPWORDS]
    title_part = "".join(words[:2]) or "Paper"
    return f"{clean_author}{year_str}{title_part}"


def to_registry(entry: dict, section: str, reason: str) -> dict:
    authors = [a.get("name", "") for a in entry.get("authors", []) if a.get("name")]
    journal = entry.get("journal") or {}
    abstract = entry.get("abstract") or ""
    if len(abstract) > 1500:
        abstract = abstract[:1500] + "... [Truncated]"
    return {
        "citation_key": citation_key(authors, entry.get("year"), entry.get("title", "")),
        "paper_id": entry.get("paperId"),
        "title": entry.get("title", ""),
        "authors": authors,
        "venue": entry.get("venue") or "arXiv",
        "year": entry.get("year"),
        "abstract": abstract,
        "citation_count": entry.get("citationCount") or 0,
        "found_in_section": section,
        "reason": reason,
        "journal": journal.get("name"),
        "volume": journal.get("volume"),
        "pages": journal.get("pages"),
        "publication_date": entry.get("publicationDate"),
    }


def request_search(title: str, api_key: str | None, timeout: int = 20) -> list[dict]:
    params = urllib.parse.urlencode(
        {"query": title, "limit": 5, "fields": FIELDS}
    )
    request = urllib.request.Request(
        f"{API_URL}?{params}",
        headers={
            "User-Agent": USER_AGENT,
            **({"X-API-KEY": api_key} if api_key else {}),
        },
    )
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
            return payload.get("data", []) or []
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code == 429:
                time.sleep(2 * (attempt + 1))
                continue
            break
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            last_error = exc
            time.sleep(1.5 * (attempt + 1))
    if last_error:
        print(f"warning: Semantic Scholar search failed for {title!r}: {last_error}", file=sys.stderr)
    return []


def best_match(title: str, year_hint, results: list[dict], cutoff: date | None) -> tuple[dict | None, float]:
    best = None
    best_ratio = 0.0
    for entry in results:
        candidate_title = entry.get("title")
        if not candidate_title:
            continue
        ratio = fuzzy(title, candidate_title)
        if year_hint and str(entry.get("year")) == str(year_hint):
            ratio += 10
        if ratio > best_ratio:
            best_ratio = ratio
            best = entry
    if best is None or best_ratio <= 70:
        return None, best_ratio

    # If the top match fails the cutoff, try the next-best match that passes.
    ordered = sorted(
        results,
        key=lambda e: fuzzy(title, e.get("title", "")) + (10 if year_hint and str(e.get("year")) == str(year_hint) else 0),
        reverse=True,
    )
    for entry in ordered:
        ratio = fuzzy(title, entry.get("title", "")) + (
            10 if year_hint and str(entry.get("year")) == str(year_hint) else 0
        )
        if ratio > 70 and before_cutoff(entry, cutoff):
            return entry, ratio
    return None, best_ratio


class Cache:
    def __init__(self, path: Path | None):
        self.path = path
        self.data: dict = {}
        if path and path.exists():
            try:
                self.data = json.loads(path.read_text(encoding="utf-8"))
            except ValueError:
                self.data = {}

    def get(self, key: str):
        return self.data.get(key)

    def put(self, key: str, value):
        self.data[key] = value
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(self.data, indent=2), encoding="utf-8")


def resolve(title: str, year_hint, cutoff, api_key, cache: Cache, sleep: float) -> dict | None:
    cache_key = f"{norm_title(title)}|{year_hint or ''}|{cutoff.isoformat() if cutoff else ''}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached or None
    results = request_search(title, api_key)
    if results:
        entry, _ = best_match(title, year_hint, results, cutoff)
        if entry and before_cutoff(entry, cutoff):
            resolved = to_registry(entry, "", "")
            cache.put(cache_key, resolved)
            if sleep:
                time.sleep(sleep)
            return resolved
    cache.put(cache_key, {})
    if sleep:
        time.sleep(sleep)
    return None


def cmd_search(args) -> int:
    cutoff = parse_cutoff(args.cutoff)
    cache = Cache(Path(args.cache).expanduser() if args.cache else None)
    match = resolve(args.title, args.year, cutoff, args.api_key, cache, args.sleep)
    print(json.dumps({"query": args.title, "year_hint": args.year, "cutoff": args.cutoff, "match": match}, indent=2))
    return 0 if match else 3


def cmd_enrich(args) -> int:
    cutoff = parse_cutoff(args.cutoff)
    cache = Cache(Path(args.cache).expanduser() if args.cache else None)
    source = Path(args.candidates).expanduser()
    try:
        candidates = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"error: cannot read candidates: {exc}", file=sys.stderr)
        return 2
    if not isinstance(candidates, list):
        print("error: candidates must be a list", file=sys.stderr)
        return 2

    registry: list[dict] = []
    seen_titles: set[str] = set()
    seen_ids: set[str] = set()
    failures: list[str] = []

    for idx, item in enumerate(candidates, 1):
        if isinstance(item, str):
            title, year, section, reason = item, None, "General", ""
        elif isinstance(item, dict):
            title = item.get("title") or item.get("focus")
            year = item.get("year")
            section = item.get("section") or item.get("found_in_section") or "General"
            reason = item.get("reason") or ""
        else:
            failures.append(f"candidate {idx}: unsupported type")
            continue
        if not title:
            failures.append(f"candidate {idx}: missing title")
            continue

        print(f"[{idx}/{len(candidates)}] {title}", file=sys.stderr)
        match = resolve(str(title), year, cutoff, args.api_key, cache, args.sleep)
        if not match:
            failures.append(f"{title}: no verified match")
            continue
        if not match.get("abstract"):
            failures.append(f"{title}: matched but has no abstract")
            continue
        nt = norm_title(match["title"])
        pid = str(match.get("paper_id") or "")
        if nt in seen_titles or (pid and pid in seen_ids):
            continue
        match["found_in_section"] = section
        match["reason"] = reason or match.get("reason", "")
        registry.append(match)
        seen_titles.add(nt)
        if pid:
            seen_ids.add(pid)

    registry.sort(key=lambda r: (r.get("found_in_section", ""), r.get("title", "")))

    if args.out:
        out = Path(args.out).expanduser()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(registry, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Wrote {len(registry)} verified papers to {out}", file=sys.stderr)
    else:
        print(json.dumps(registry, indent=2, ensure_ascii=False))

    for failure in failures:
        print(f"  skip: {failure}", file=sys.stderr)
    return 0 if registry else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--api-key", default=os.environ.get("SEMANTIC_SCHOLAR_API_KEY"))
    common.add_argument("--cache", help="Optional JSON cache path")
    common.add_argument("--sleep", type=float, default=1.1, help="Seconds between API calls (default 1.1)")
    sub = parser.add_subparsers(dest="command", required=True)

    search = sub.add_parser("search", parents=[common], help="Resolve one title")
    search.add_argument("--title", required=True)
    search.add_argument("--year", type=int)
    search.add_argument("--cutoff", help="YYYY-MM; papers on or after this are rejected")
    search.set_defaults(func=cmd_search)

    enrich = sub.add_parser("enrich", parents=[common], help="Resolve a candidate list into a registry")
    enrich.add_argument("--candidates", required=True)
    enrich.add_argument("--out")
    enrich.add_argument("--cutoff", help="YYYY-MM; papers on or after this are rejected")
    enrich.set_defaults(func=cmd_enrich)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
