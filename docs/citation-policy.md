# Citation policy

This is the short version. The operational details live in `skills/research-literature-review/references/citation-policy.md`.

## The rule

A citation exists only after a bibliographic API returns matching metadata. Model memory is allowed to propose a candidate; it is never allowed to write a BibTeX entry.

## Verification thresholds

| Check | Threshold |
|---|---|
| Title similarity (exploration) | > 70 (normalized Levenshtein-style ratio) |
| Title similarity (targeted) | >= 90 plus a year or author check |
| Year match | required for targeted lookups when a year is supplied |
| Abstract | required |
| Publication date | strictly before the cutoff |
| Deduplication | normalized title and Semantic Scholar paper ID |

Verification tries Semantic Scholar, arXiv, Crossref, and DBLP in order. Semantic Scholar rate-limits unauthenticated traffic; set `SEMANTIC_SCHOLAR_API_KEY` before a large run. If one provider is rate-limited or blocked, fall back to the next; do not bypass verification.

## Cutoff

`YYYY-MM` means the first day of that month. Anything on or after that date is concurrent work. When the API returns only a year, an earlier year passes, a later year fails, and the same year passes with a warning because the month is unknown.

## P0 and P1

- **P0 (must-cite):** direct baselines, datasets used, metrics used, and foundational methods the paper builds on or modifies.
- **P1 (good-to-cite):** background, surveys, orthogonal work, and tools mentioned in passing.

The outline must produce a citation hint for every P0 dependency. The evaluation script reports P0 and P1 recall separately.

## Density

- Minimum for a full paper: 20 unique verified papers.
- Healthy: 40–60.
- Cover every P0 dependency and at least two verified papers per Related Work cluster.
- Do not pad to hit an overall percentage. A citation that does not support its sentence is a defect. Overall coverage is reported, not enforced.

## Anti-hallucination

- No invented arXiv IDs, DOIs, pages, volumes, or authors.
- No citation without an abstract.
- No claim of beating a paper that is absent from the experimental log.
- No reconstruction of the source paper's bibliography from memory.

## Failure is acceptable

A missing citation is recoverable. A fabricated one is not. If verification fails for a required dependency, report the gap and let the human decide.
