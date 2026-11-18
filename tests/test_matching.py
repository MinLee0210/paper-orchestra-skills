from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import date

import pytest

from conftest import load_script

ss = load_script("skills/paper-literature-review/scripts/semantic_scholar.py")
ARXIV_NS = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


def candidate(**overrides):
    data = {
        "source": "fake",
        "paper_id": "fake:1",
        "title": "Attention Is All You Need",
        "authors": ["Ashish Vaswani"],
        "venue": "NeurIPS",
        "year": 2017,
        "abstract": "A transformer architecture.",
        "citation_count": 100,
        "journal": None,
        "volume": None,
        "pages": None,
        "publication_date": "2017-06-12",
        "doi": None,
    }
    data.update(overrides)
    return data


def test_fuzzy_and_cutoff():
    assert ss.fuzzy("Attention Is All You Need", "Attention Is All You Need") == 100.0
    assert 70 < ss.fuzzy("Attention Is All You Need", "Attention Is All You Need for Vision") < 90
    assert ss.before_cutoff(candidate(), date(2024, 11, 1))
    assert not ss.before_cutoff(candidate(year=2025, publication_date="2025-01-01"), date(2024, 11, 1))


def test_targeted_requires_year_or_author():
    match, _, _ = ss.pick_match([candidate()], "Attention Is All You Need", 2017, targeted=True)
    assert match is not None

    match, _, _ = ss.pick_match([candidate()], "Attention Is All You Need", 2020, targeted=True)
    assert match is None

    match, _, _ = ss.pick_match(
        [candidate()], "Attention Is All You Need", 2020, author_hint="Vaswani", targeted=True
    )
    assert match is not None
    assert match["year"] == 2017


def test_targeted_threshold_rejects_near_title():
    near = candidate(title="Attention Is All You Need for Vision", year=2017)
    match, _, _ = ss.pick_match([near], "Attention Is All You Need", 2017, targeted=True, min_ratio=90)
    assert match is None
    match, _, _ = ss.pick_match([near], "Attention Is All You Need", 2017, min_ratio=70)
    assert match is not None


def test_provider_normalizers():
    xml = """<feed xmlns="http://www.w3.org/2005/Atom">
      <entry>
        <id>http://arxiv.org/abs/1706.03762v5</id>
        <published>2017-06-12T00:00:00Z</published>
        <title>Attention Is All You Need</title>
        <summary>The dominant sequence transduction models.</summary>
        <author><name>Ashish Vaswani</name></author>
      </entry>
    </feed>"""
    entry = ET.fromstring(xml).find("a:entry", ARXIV_NS)
    arxiv = ss.normalize_arxiv(entry)
    assert arxiv["paper_id"] == "arxiv:1706.03762"
    assert arxiv["year"] == 2017

    crossref = ss.normalize_crossref(
        {
            "DOI": "10.1/x",
            "title": ["A Paper"],
            "author": [{"given": "Jane", "family": "Doe"}],
            "container-title": ["Journal"],
            "issued": {"date-parts": [[2020, 5, 1]]},
            "abstract": "<jats:p>Hello abstract.</jats:p>",
            "is-referenced-by-count": 4,
        }
    )
    assert crossref["abstract"] == "Hello abstract."
    assert crossref["publication_date"] == "2020-05-01"
    assert crossref["paper_id"] == "crossref:10.1/x"

    dblp = ss.normalize_dblp(
        {
            "key": "conf/x/1",
            "title": "A Paper.",
            "authors": {"author": [{"text": "Jane Doe"}]},
            "year": "2020",
            "venue": "Conf",
        }
    )
    assert dblp["authors"] == ["Jane Doe"]
    assert dblp["year"] == 2020


def test_resolve_falls_back_and_caches(monkeypatch, tmp_path):
    calls = []

    def failing(title, api_key, timeout=20):
        calls.append("fail")
        raise ss.ProviderError("429")

    def working(title, api_key, timeout=20):
        calls.append("work")
        return [candidate(source="fallback")]

    monkeypatch.setitem(ss.SEARCHERS, "fail", failing)
    monkeypatch.setitem(ss.SEARCHERS, "work", working)

    cache = ss.Cache(tmp_path / "cache.json")
    entry, attempts = ss.resolve(
        "Attention Is All You Need", 2017, None, None, None, cache, 0,
        sources=("fail", "work"), targeted=True, min_ratio=90,
    )
    assert entry is not None
    assert entry["source"] == "fallback"
    assert entry["match_ratio"] == 100.0
    assert attempts[0]["status"].startswith("error")

    entry2, attempts2 = ss.resolve(
        "Attention Is All You Need", 2017, None, None, None, cache, 0,
        sources=("fail", "work"), targeted=True, min_ratio=90,
    )
    assert entry2 is not None
    assert attempts2[0]["source"] == "cache"
    assert calls == ["fail", "work"]


def test_missing_abstract_can_be_enriched(monkeypatch):
    monkeypatch.setattr(ss, "crossref_by_doi", lambda doi, timeout=20: {"abstract": "Fetched abstract."})
    entry = ss.enrich_missing_abstract(candidate(abstract="", doi="10.1/x"))
    assert entry["abstract"] == "Fetched abstract."
    assert entry["abstract_source"] == "crossref"
