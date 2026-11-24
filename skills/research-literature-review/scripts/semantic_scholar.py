#!/usr/bin/env python3
"""Search and verify papers with Semantic Scholar plus fallback providers.

Discovery may guess. Verification may not. A candidate is accepted only when a
provider returns a title match above the threshold, the paper predates the
cutoff, and an abstract is available (unless --allow-missing-abstract).

Examples:
    python semantic_scholar.py search --title "Attention Is All You Need" --year 2017
    python semantic_scholar.py search --title "AdamW" --targeted --year 2019
    python semantic_scholar.py enrich --candidates candidates.json --out registry.json --cutoff 2024-11
"""

from __future__ import annotations

import argparse
import difflib
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

S2_API_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
S2_FIELDS = (
    "paperId,title,authors,venue,year,abstract,citationCount,journal,"
    "publicationDate,externalIds"
)
ARXIV_API_URL = "https://export.arxiv.org/api/query"
CROSSREF_API_URL = "https://api.crossref.org/works"
CROSSREF_DOI_URL = "https://api.crossref.org/works/{doi}"
DBLP_API_URL = "https://dblp.org/search/publ/api"
USER_AGENT = "paper-orchestra-skills/1.0 (+https://github.com/MinLee0210/paper-orchestra-skills)"
DEFAULT_SOURCES = ("semantic_scholar", "arxiv", "crossref", "dblp")
STOPWORDS = {
    "the", "a", "an", "in", "on", "at", "for", "to", "of", "and", "is",
    "are", "with", "by", "study",
}
ARXIV_NS = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


class ProviderError(RuntimeError):
    pass


def norm_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(title).lower())


def normalize_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def fuzzy(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, str(a).lower(), str(b).lower()).ratio() * 100.0


def clean_text(value) -> str:
    if value is None:
        return ""
    text = html.unescape(str(value))
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return re.sub(r"^abstract[:\s]+", "", text, flags=re.IGNORECASE)


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
    pub = entry.get("publication_date")
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
    # Same year without a parseable month: permissive, reported as a warning.
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


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------


def http_get(url: str, headers: dict | None = None, timeout: int = 20, attempts: int = 2) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code in (429, 500, 502, 503, 504):
                time.sleep(1.5 * (attempt + 1))
                continue
            break
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            time.sleep(1.0 * (attempt + 1))
    raise ProviderError(str(last_error))


def http_get_json(url: str, headers: dict | None = None, timeout: int = 20) -> dict:
    text = http_get(url, headers=headers, timeout=timeout)
    try:
        return json.loads(text)
    except ValueError as exc:
        raise ProviderError(f"invalid JSON: {exc}") from exc


# ---------------------------------------------------------------------------
# Provider normalization
# ---------------------------------------------------------------------------


def normalize_s2(entry: dict) -> dict:
    authors = [a.get("name", "") for a in entry.get("authors", []) if a.get("name")]
    journal = entry.get("journal") or {}
    return {
        "source": "semantic_scholar",
        "paper_id": f"s2:{entry.get('paperId')}" if entry.get("paperId") else "",
        "title": clean_text(entry.get("title")),
        "authors": authors,
        "venue": clean_text(entry.get("venue")) or "arXiv",
        "year": entry.get("year"),
        "abstract": clean_text(entry.get("abstract")),
        "citation_count": entry.get("citationCount") or 0,
        "journal": journal.get("name"),
        "volume": journal.get("volume"),
        "pages": journal.get("pages"),
        "publication_date": entry.get("publicationDate"),
        "doi": (entry.get("externalIds") or {}).get("DOI"),
    }


def search_semantic_scholar(title: str, api_key: str | None, timeout: int = 20) -> list[dict]:
    params = urllib.parse.urlencode({"query": title, "limit": 5, "fields": S2_FIELDS})
    headers = {"X-API-KEY": api_key} if api_key else {}
    payload = http_get_json(f"{S2_API_URL}?{params}", headers=headers, timeout=timeout)
    return [normalize_s2(entry) for entry in payload.get("data", []) or []]


def normalize_arxiv(entry: ET.Element) -> dict:
    title = clean_text(entry.findtext("a:title", default="", namespaces=ARXIV_NS))
    summary = clean_text(entry.findtext("a:summary", default="", namespaces=ARXIV_NS))
    published = entry.findtext("a:published", default="", namespaces=ARXIV_NS)
    raw_id = entry.findtext("a:id", default="", namespaces=ARXIV_NS)
    authors = [
        clean_text(name.text or "")
        for name in entry.findall("a:author/a:name", ARXIV_NS)
        if name.text
    ]
    doi = entry.findtext("arxiv:doi", default="", namespaces=ARXIV_NS)
    paper_id = raw_id.rsplit("/abs/", 1)[-1] if "/abs/" in raw_id else raw_id
    paper_id = re.sub(r"v\d+$", "", paper_id)
    year = int(published[:4]) if published[:4].isdigit() else None
    return {
        "source": "arxiv",
        "paper_id": f"arxiv:{paper_id}" if paper_id else "",
        "title": title,
        "authors": authors,
        "venue": "arXiv",
        "year": year,
        "abstract": summary,
        "citation_count": 0,
        "journal": None,
        "volume": None,
        "pages": None,
        "publication_date": published[:10] if published else None,
        "doi": doi or None,
    }


def search_arxiv(title: str, api_key: str | None = None, timeout: int = 20) -> list[dict]:
    query = urllib.parse.urlencode(
        {"search_query": f'ti:"{title}"', "start": 0, "max_results": 5}
    )
    xml_text = http_get(f"{ARXIV_API_URL}?{query}", timeout=timeout)
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        raise ProviderError(f"invalid arXiv XML: {exc}") from exc
    return [normalize_arxiv(entry) for entry in root.findall("a:entry", ARXIV_NS)]


def crossref_date(record: dict) -> str | None:
    for key in ("published-print", "published-online", "issued", "created"):
        parts = (record.get(key) or {}).get("date-parts") or []
        if parts and parts[0] and parts[0][0]:
            values = list(parts[0]) + [1, 1]
            try:
                return f"{int(values[0]):04d}-{int(values[1]):02d}-{int(values[2]):02d}"
            except (ValueError, TypeError):
                continue
    return None


def normalize_crossref(record: dict) -> dict:
    titles = record.get("title") or []
    title = clean_text(titles[0]) if titles else ""
    authors = []
    for author in record.get("author", []) or []:
        name = " ".join(part for part in (author.get("given"), author.get("family")) if part)
        if name:
            authors.append(name)
    containers = record.get("container-title") or []
    journal = clean_text(containers[0]) if containers else None
    pub = crossref_date(record)
    return {
        "source": "crossref",
        "paper_id": f"crossref:{record.get('DOI')}" if record.get("DOI") else "",
        "title": title,
        "authors": authors,
        "venue": journal or clean_text(record.get("type")) or "Crossref",
        "year": int(pub[:4]) if pub else None,
        "abstract": clean_text(record.get("abstract")),
        "citation_count": record.get("is-referenced-by-count") or 0,
        "journal": journal,
        "volume": record.get("volume"),
        "pages": record.get("page"),
        "publication_date": pub,
        "doi": record.get("DOI"),
    }


def search_crossref(title: str, api_key: str | None = None, timeout: int = 20) -> list[dict]:
    params = urllib.parse.urlencode({"query.title": title, "rows": 5})
    payload = http_get_json(f"{CROSSREF_API_URL}?{params}", timeout=timeout)
    items = (payload.get("message") or {}).get("items", []) or []
    return [normalize_crossref(item) for item in items]


def crossref_by_doi(doi: str, timeout: int = 20) -> dict | None:
    if not doi:
        return None
    try:
        url = CROSSREF_DOI_URL.format(doi=urllib.parse.quote(doi, safe="/"))
        payload = http_get_json(url, timeout=timeout)
        return normalize_crossref((payload.get("message") or {}))
    except ProviderError:
        return None


def normalize_dblp(info: dict) -> dict:
    authors_raw = (info.get("authors") or {}).get("author") or []
    if isinstance(authors_raw, dict):
        authors_raw = [authors_raw]
    authors = [
        clean_text(a.get("text", "")) if isinstance(a, dict) else clean_text(a)
        for a in authors_raw
        if a
    ]
    year = info.get("year")
    return {
        "source": "dblp",
        "paper_id": f"dblp:{info.get('key')}" if info.get("key") else "",
        "title": clean_text(info.get("title")),
        "authors": authors,
        "venue": clean_text(info.get("venue")) or "DBLP",
        "year": int(year) if str(year).isdigit() else None,
        "abstract": "",
        "citation_count": 0,
        "journal": None,
        "volume": info.get("volume"),
        "pages": info.get("pages"),
        "publication_date": f"{year}-01-01" if str(year).isdigit() else None,
        "doi": info.get("doi"),
        "url": info.get("ee"),
    }


def search_dblp(title: str, api_key: str | None = None, timeout: int = 20) -> list[dict]:
    params = urllib.parse.urlencode({"q": title, "format": "json", "h": 5})
    payload = http_get_json(f"{DBLP_API_URL}?{params}", timeout=timeout)
    hits = (((payload.get("result") or {}).get("hits") or {}).get("hit")) or []
    if isinstance(hits, dict):
        hits = [hits]
    records = []
    for hit in hits:
        info = hit.get("info") if isinstance(hit, dict) else None
        if info:
            records.append(normalize_dblp(info))
    return records


SEARCHERS = {
    "semantic_scholar": search_semantic_scholar,
    "arxiv": search_arxiv,
    "crossref": search_crossref,
    "dblp": search_dblp,
}


# ---------------------------------------------------------------------------
# Matching and resolution
# ---------------------------------------------------------------------------


def author_matches(candidate: dict, author_hint: str | None) -> bool | None:
    if not author_hint:
        return None
    hint = normalize_name(author_hint)
    if not hint:
        return None
    return any(hint in normalize_name(author) for author in candidate.get("authors", []))


def pick_match(
    candidates: list[dict],
    title: str,
    year_hint: int | None = None,
    author_hint: str | None = None,
    targeted: bool = False,
    min_ratio: float | None = None,
) -> tuple[dict | None, float, str]:
    threshold = min_ratio if min_ratio is not None else (90.0 if targeted else 70.0)
    best = None
    best_score = -1.0
    best_reason = "no candidate above threshold"

    for candidate in candidates:
        candidate_title = candidate.get("title") or ""
        ratio = fuzzy(title, candidate_title)
        if ratio < threshold:
            continue
        year_ok = None
        if year_hint:
            year = candidate.get("year")
            year_ok = str(year) == str(year_hint) if year is not None else False
        author_ok = author_matches(candidate, author_hint)

        if targeted:
            # A targeted lookup must confirm the identity. Require a year match
            # or an author match when either hint was supplied.
            if year_hint and not year_ok:
                if not (author_hint and author_ok):
                    best_reason = f"year mismatch ({candidate.get('year')} != {year_hint})"
                    continue
            if author_hint and not author_ok:
                if not (year_hint and year_ok):
                    best_reason = "author mismatch"
                    continue

        score = ratio + (3.0 if year_ok else 0.0) + (3.0 if author_ok else 0.0)
        if score > best_score:
            best = candidate
            best_score = score
            best_reason = f"title ratio {ratio:.1f}"
            if year_ok:
                best_reason += ", year match"
            if author_ok:
                best_reason += ", author match"

    return best, best_score if best else 0.0, best_reason


def enrich_missing_abstract(entry: dict, timeout: int = 20) -> dict:
    if entry.get("abstract"):
        return entry
    doi = entry.get("doi")
    if doi:
        record = crossref_by_doi(doi, timeout=timeout)
        if record:
            for field in ("abstract", "authors", "venue", "journal", "volume", "pages"):
                if not entry.get(field) and record.get(field):
                    entry[field] = record[field]
            entry["abstract_source"] = "crossref"
    return entry


def to_registry(entry: dict, section: str, reason: str, ratio: float) -> dict:
    abstract = clean_text(entry.get("abstract"))
    if len(abstract) > 1500:
        abstract = abstract[:1500] + "... [Truncated]"
    return {
        "citation_key": citation_key(entry.get("authors", []), entry.get("year"), entry.get("title", "")),
        "paper_id": entry.get("paper_id"),
        "source": entry.get("source"),
        "title": entry.get("title", ""),
        "authors": entry.get("authors", []),
        "venue": entry.get("venue") or "arXiv",
        "year": entry.get("year"),
        "abstract": abstract,
        "citation_count": entry.get("citation_count") or 0,
        "found_in_section": section,
        "reason": reason,
        "journal": entry.get("journal"),
        "volume": entry.get("volume"),
        "pages": entry.get("pages"),
        "publication_date": entry.get("publication_date"),
        "doi": entry.get("doi"),
        "match_ratio": round(ratio, 2),
        "verification": {"source": entry.get("source"), "matched_title_ratio": round(ratio, 2)},
    }


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


def resolve(
    title: str,
    year_hint,
    author_hint,
    cutoff,
    api_key,
    cache: Cache,
    sleep: float,
    sources: tuple[str, ...] = DEFAULT_SOURCES,
    targeted: bool = False,
    min_ratio: float | None = None,
    allow_missing_abstract: bool = False,
    timeout: int = 20,
) -> tuple[dict | None, list[dict]]:
    cache_key = "|".join(
        [
            norm_title(title),
            str(year_hint or ""),
            normalize_name(author_hint or ""),
            cutoff.isoformat() if cutoff else "",
            "targeted" if targeted else "explore",
            str(min_ratio if min_ratio is not None else ""),
            ",".join(sources),
        ]
    )
    cached = cache.get(cache_key)
    if cached is not None:
        return (cached or None), [{"source": "cache", "status": "hit" if cached else "miss"}]

    attempts: list[dict] = []
    for source in sources:
        searcher = SEARCHERS.get(source)
        if searcher is None:
            attempts.append({"source": source, "status": "unknown provider"})
            continue
        try:
            candidates = searcher(title, api_key, timeout=timeout)
        except (ProviderError, OSError, ValueError) as exc:
            attempts.append({"source": source, "status": f"error: {exc}"})
            continue

        match, score, reason = pick_match(
            candidates, title, year_hint, author_hint, targeted=targeted, min_ratio=min_ratio
        )
        attempts.append(
            {
                "source": source,
                "candidates": len(candidates),
                "best_score": round(score, 2),
                "status": reason,
            }
        )
        if not match:
            continue
        if not before_cutoff(match, cutoff):
            attempts[-1]["status"] = "matched but after cutoff"
            continue
        match = enrich_missing_abstract(match, timeout=timeout)
        if not match.get("abstract") and not allow_missing_abstract:
            attempts[-1]["status"] = "matched but no abstract"
            continue

        title_ratio = fuzzy(title, match.get("title", ""))
        registry = to_registry(match, "", "", title_ratio)
        cache.put(cache_key, registry)
        if sleep:
            time.sleep(sleep)
        return registry, attempts

    cache.put(cache_key, {})
    if sleep:
        time.sleep(sleep)
    return None, attempts


def parse_sources(value: str) -> tuple[str, ...]:
    sources = tuple(part.strip() for part in value.split(",") if part.strip())
    if not sources:
        raise ValueError("at least one source is required")
    unknown = [source for source in sources if source not in SEARCHERS]
    if unknown:
        raise ValueError(f"unknown sources: {', '.join(unknown)}. Available: {', '.join(SEARCHERS)}")
    return sources


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def cmd_search(args) -> int:
    cutoff = parse_cutoff(args.cutoff)
    cache = Cache(Path(args.cache).expanduser() if args.cache else None)
    match, attempts = resolve(
        args.title,
        args.year,
        args.author,
        cutoff,
        args.api_key,
        cache,
        args.sleep,
        args.sources,
        targeted=args.targeted,
        min_ratio=args.min_ratio,
        allow_missing_abstract=args.allow_missing_abstract,
    )
    result = {
        "query": args.title,
        "year_hint": args.year,
        "author_hint": args.author,
        "cutoff": args.cutoff,
        "targeted": args.targeted,
        "min_ratio": args.min_ratio,
        "match": match,
        "attempts": attempts,
    }
    print(json.dumps(result, indent=2))
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
            title, year, author, section, reason = item, None, None, "General", ""
            targeted = True
        elif isinstance(item, dict):
            title = item.get("title") or item.get("focus")
            year = item.get("year")
            author = item.get("author")
            section = item.get("section") or item.get("found_in_section") or "General"
            reason = item.get("reason") or ""
            targeted = bool(item.get("targeted")) or item.get("search_type") == "targeted"
        else:
            failures.append(f"candidate {idx}: unsupported type")
            continue
        if not title:
            failures.append(f"candidate {idx}: missing title")
            continue

        print(f"[{idx}/{len(candidates)}] {'targeted' if targeted else 'explore'} {title}", file=sys.stderr)
        match, attempts = resolve(
            str(title),
            year,
            author,
            cutoff,
            args.api_key,
            cache,
            args.sleep,
            args.sources,
            targeted=targeted or args.targeted,
            min_ratio=args.min_ratio,
            allow_missing_abstract=args.allow_missing_abstract,
        )
        if args.debug:
            for attempt in attempts:
                print(f"    {attempt}", file=sys.stderr)
        if not match:
            failures.append(f"{title}: no verified match ({attempts[-1].get('status') if attempts else 'no providers'})")
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
    common.add_argument("--sleep", type=float, default=1.1, help="Seconds between resolutions (default 1.1)")
    common.add_argument(
        "--sources",
        default=",".join(DEFAULT_SOURCES),
        help="Comma-separated provider order (default: semantic_scholar,arxiv,crossref,dblp)",
    )
    common.add_argument("--min-ratio", type=float, help="Override title similarity threshold")
    common.add_argument("--targeted", action="store_true", help="Require a high-confidence single-paper match")
    common.add_argument("--allow-missing-abstract", action="store_true", help="Accept metadata-only matches")
    common.add_argument("--debug", action="store_true", help="Print provider attempts to stderr")
    sub = parser.add_subparsers(dest="command", required=True)

    search = sub.add_parser("search", parents=[common], help="Resolve one title")
    search.add_argument("--title", required=True)
    search.add_argument("--year", type=int)
    search.add_argument("--author", help="Expected author surname or full name")
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
        args.sources = parse_sources(args.sources)
        return args.func(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
