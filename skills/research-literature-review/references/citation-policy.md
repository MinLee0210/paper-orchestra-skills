# Citation policy

## Discovery versus verification

Discovery may use web search and model judgment. Verification may not. A candidate becomes a citation only after a bibliographic API returns its metadata.

| Step | Allowed sources | Output |
|---|---|---|
| Discovery | web search, search-grounded model | candidate title, year, reason |
| Verification | Semantic Scholar, then arXiv, Crossref, DBLP | paper ID, authors, venue, year, abstract, dates |
| Writing | verified registry only | LaTeX with `\cite{...}` |

## Acceptance thresholds

- Exploration tasks require a fuzzy title similarity **greater than 70** (Levenshtein-style ratio).
- Targeted tasks require **>= 90** plus a year or author check, because a near-title match can be a different paper.
- A year mismatch or author mismatch rejects a targeted match unless the other check confirms identity.
- The paper must have an abstract. Without one, the writer cannot describe it accurately.
- The paper must strictly predate the cutoff.
- Duplicate candidates are removed by normalized title and by paper ID.

Semantic Scholar rate-limits unauthenticated requests. Set `SEMANTIC_SCHOLAR_API_KEY` for a large run. A 429 is a reason to wait and retry, never a reason to verify from memory.

## Cutoff semantics

The cutoff is the first day of the stated month. A venue deadline of November 2024 means `2024-11-01`; anything on or after that date is concurrent work, not prior art.

When the API returns a full publication date, compare it directly. When it returns only a year:

- an earlier year passes;
- a later year fails;
- the same year without a month passes, but is reported as a warning because the month is unknown.

If the user needs strict cutoff behavior, require full publication dates and drop year-only records.

## Priority classes

PaperOrchestra's evaluator separates references into two classes. The same distinction is useful when deciding what the paper must cite:

- **P0 (must-cite):** direct experimental baselines, datasets used, metrics used, and foundational methods the paper builds on or modifies.
- **P1 (good-to-cite):** general background, orthogonal work, surveys, and tools mentioned in passing.

The outline's `citation_hints` should cover every P0 dependency exhaustively. If a dataset or optimizer appears in the experimental log and has no hint, the outline is incomplete.

## Citation density

- Minimum for a full research paper: 20 unique verified papers.
- Healthy range: 40–60, depending on the field.
- Cover every P0 dependency. In Related Work, cite at least two verified papers per methodology cluster.
- Do not pad to hit an overall percentage. A citation that does not support the sentence it is attached to is a defect, not coverage. Overall coverage is reported for review, not enforced.

## Anti-hallucination rules

- Never generate a BibTeX entry from memory. No exceptions.
- Never invent an arXiv ID, DOI, page range, volume, or author.
- Never cite a paper whose abstract you have not retrieved.
- Never claim a comparison against a paper that is absent from the experimental log.
- If verification fails for a required dependency, report the gap. A missing citation is recoverable; a fabricated one is not.

## Where the bibliography comes from

`registry.json` → `build_bib.py` → `references.bib` + `citation_map.json`.

The registry is the source of truth. If the `.bib` and the registry disagree, rebuild the `.bib`; do not hand-edit it.
