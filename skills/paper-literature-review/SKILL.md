---
name: paper-literature-review
description: Discover, verify, deduplicate, and cite real academic literature, then write the Introduction and Related Work sections. Use when the user asks for a literature review, related work, citation gathering, bibliography or BibTeX construction, citation coverage, or wants to find and verify papers for a manuscript. Also use when another paper-writing skill needs registry.json, citation_map.json, references.bib, or a cited LaTeX template. Enforces a research cutoff and rejects unverifiable citations.
license: Apache-2.0
---

# Literature review agent

The literature stage has one job that must not be compromised: every citation in the paper must resolve to a real paper whose metadata was fetched from a bibliographic API, and the writing must use only those verified papers.

PaperOrchestra's key finding is that autonomous writers under-cite because they rely on keyword search and model memory. This skill separates **discovery** (broad, parallel, search-grounded) from **verification** (sequential, strict, API-grounded), then writes from the verified registry.

## Inputs

- `outline.json` — especially `intro_related_work_plan` and every `citation_hints` entry in `section_plan`.
- `idea.md`, `experimental_log.md` — for framing and for deciding which dependencies must be cited.
- `template.tex` — the skeleton whose Introduction and Related Work the stage fills.
- `guidelines.md` — citation style, page limit, anonymity.
- Research cutoff `YYYY-MM` — nothing published on or after this date may be treated as prior work.

## Phase 1: Discovery

Collect search tasks from three sources:

1. **Introduction directions** — each `search_directions` entry becomes an exploration task. Context: hook + problem gap.
2. **Related Work queries** — each `limitation_search_queries` entry becomes an exploration task. Context: SOTA mission + limitation hypothesis. Fall back to `<subsection_title> <methodology_cluster>` when a cluster has no queries.
3. **Citation hints** — every hint in `section_plan` becomes a targeted task. A targeted task asks for exactly one paper: the canonical paper that introduced the named dataset, metric, optimizer, baseline, architecture, or model.

Run discovery tasks in parallel (10 concurrent is a good default). For each task, ask a search-grounded model for candidates with title, year, and a one-line reason. Exploration tasks should return 10–15 candidates; do not force results when the task is narrow. Targeted tasks should return exactly one candidate.

Read `references/prompts.md` for the discovery and writing prompts.

## Phase 2: Verification

For every candidate, sequentially:

1. Query the configured providers in order: Semantic Scholar, arXiv, Crossref, then DBLP.
2. Exploration tasks accept a fuzzy title ratio above 70. Targeted tasks (the canonical paper for a dataset, metric, optimizer, baseline, or model) require **>= 90** and a year or author check.
3. Reject if the paper is on or after the cutoff.
4. Reject if there is no abstract; the writer needs the abstract to describe the work accurately. (DBLP records can be enriched by DOI through Crossref.)
5. Fetch authors, venue, year, citation count, journal, volume, pages, and publication date.
6. Deduplicate by normalized title and by provider paper ID.

Use the bundled script:

```bash
# Exploration: wider match, still cutoff-aware
python scripts/semantic_scholar.py search --title "Attention Is All You Need" --year 2017 --cutoff 2024-11

# Targeted: require a high-confidence canonical paper
python scripts/semantic_scholar.py search --title "AdamW" --author "Loshchilov" --year 2019 --targeted --cutoff 2024-11

# Batch: strings are treated as targeted; dicts use "targeted": true or "search_type": "targeted"
python scripts/semantic_scholar.py enrich --candidates candidates.json --out registry.json --cutoff 2024-11
```

Fallback providers are tried in order (`--sources semantic_scholar,arxiv,crossref,dblp`). A provider rate-limit or network block is not a reason to verify from memory; it is a reason to fall back or retry.

`candidates.json` may be a list of strings or objects:

```json
[
  {"title": "Attention Is All You Need", "year": 2017, "section": "Related Work: Efficient Attention", "reason": "Foundational architecture"},
  "research paper or technical report introducing 'AdamW optimizer'"
]
```

Semantic Scholar rate-limits unauthenticated requests aggressively. If the API returns 429, set `SEMANTIC_SCHOLAR_API_KEY` and retry; do not replace the verification step with model memory. Discovery can continue while verification waits.

Do not proceed with a candidate whose metadata you could only obtain from model memory. If the API fails, retry later or drop the candidate; never hand-write a BibTeX entry from recall.

## Phase 3: Build the bibliography and citation map

```bash
python scripts/build_bib.py --registry registry.json --out literature_agent_output
```

This writes `references.bib` and `citation_map.json`, uniquifies citation keys, and preserves abstracts for the writer. Then inject the verified candidates into the outline:

```bash
python scripts/inject_citations.py --outline outline.json --registry registry.json --out literature_agent_output/outline_v1.json
```

Each subsection gains `citation_candidates` and loses `citation_hints`. Clusters with zero candidates are reported so they can be searched again.

## Phase 4: Write Introduction and Related Work

Write only those two sections. Leave every other section untouched.

Rules:

- Cite only keys from `citation_map.json`. A citation key not in the map is a bug.
- Cover every P0 dependency: baselines, datasets, metrics, and foundational methods. In Related Work, cite at least two verified papers per methodology cluster.
- Do not pad to hit an overall percentage. A citation that does not support its sentence is a defect, not coverage.
- Introduction: macro context, impact, foundational work, surveys, and the gap. Cite statistics and broad claims.
- Related Work: micro comparisons, grouped by methodology cluster. Use comparative sentences ("Several methods [A, B] reduce ... but assume ...") rather than a list of summaries.
- Treat papers after the cutoff as concurrent work, never as baselines the method beats.
- Never claim state of the art over a cited paper unless that paper appears as a baseline in `experimental_log.md`.
- Preserve the template's preamble, packages, and already-filled sections.
- Do not change `\usepackage[capitalize]{cleveref}` to `cleverref`.
- Return the full updated `template.tex`, not a diff.

Save as `updated_template.tex` in the output directory.

## Phase 5: Validate

```bash
python scripts/validate_literature.py \
  --dir literature_agent_output \
  --outline literature_agent_output/outline_v1.json \
  --template literature_agent_output/updated_template.tex
```

Checks:

- every key in `citation_map.json` exists in `references.bib` and vice versa;
- every `\cite{...}` in the template resolves;
- every `citation_candidates` key in the outline exists in the map;
- every Related Work cluster has at least two verified candidates;
- no duplicate keys, missing titles, missing authors, or missing years;
- paper count and per-cluster coverage are plausible for a full paper. Overall citation percentage is reported, not enforced as a quota.

Treat 20 unique papers as the minimum for a full research paper and 40+ as healthy. A thin registry is a reason to rerun discovery, not a reason to lower the bar.

## Non-negotiable rules

- **No invented citations.** A plausible-looking BibTeX entry is worse than a missing one.
- **Cutoff is strict.** If the venue deadline is November 2024, a December 2024 paper is concurrent work, not prior art.
- **Abstracts are evidence.** If you cannot retrieve an abstract, you cannot describe the paper accurately; drop it.
- **No leakage.** Do not reconstruct the source paper's reference list from memory. Discover from the outline's tasks.
- **No silent gaps.** If a cluster has no verified papers, say so in the handoff instead of writing a vague paragraph.

## Files

- `references/prompts.md` — discovery, targeted search, and Introduction/Related Work prompts.
- `references/citation-policy.md` — verification thresholds, cutoff logic, and P0/P1 definitions.
- `scripts/semantic_scholar.py` — Semantic Scholar plus arXiv/Crossref/DBLP fallback, targeted matching, deduplication, and key generation.
- `scripts/build_bib.py` — registry to BibTeX and citation map.
- `scripts/inject_citations.py` — attach verified keys to the outline.
- `scripts/validate_literature.py` — consistency checks before writing.
