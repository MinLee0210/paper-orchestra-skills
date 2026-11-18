---
name: paper-evaluation
description: Evaluate a generated research paper against a ground-truth paper, a baseline, or a benchmark. Use when the user asks to score, benchmark, compare, or ablate paper-writing quality, measure citation precision/recall/F1, judge literature reviews, compute side-by-side win rates, or reproduce PaperWritingBench-style evaluation. Also use after generation to report objective metrics instead of impressions.
license: Apache-2.0
---

# Paper evaluation

Evaluation is what separates a demo from a system. This skill defines four measurements used in PaperOrchestra and gives deterministic scripts where the metric allows it.

| Metric | What it answers | Script or rubric |
|---|---|---|
| Citation F1 | Did the paper find and cite the works that matter? | `scripts/citation_f1.py` |
| Literature review quality | Is the Introduction/Related Work analytical and well positioned? | `references/lit-review-rubric.md` |
| Overall quality | Would a reviewer accept the manuscript? | `references/agentreview.md` |
| Side-by-side | Which of two manuscripts is better? | `references/sxs-prompts.md`, `scripts/aggregate_sxs.py` |

## Citation F1

Compare a generated registry against a ground-truth registry. Papers are matched by normalized title (and by Semantic Scholar ID when present).

```bash
python scripts/citation_f1.py --gt gt_registry.json --gen generated_registry.json
python scripts/citation_f1.py --gt gt.json --gen gen.json --json > metrics/citation_f1.json
```

The script reports precision, recall, and F1 for:

- the full reference set,
- **P0** must-cite papers (baselines, datasets, metrics, foundational methods),
- **P1** good-to-cite papers (background, orthogonal work).

A registry can mark priority per paper:

```json
{"title": "...", "priority": "P0"}
```

Or provide explicit ID sets:

```json
{"p0_ids": ["..."], "p1_ids": ["..."]}
```

Interpretation matters. A system that cites 12 obvious papers can have a competitive overall F1 while P1 recall is near zero. Always report the citation count alongside F1. PaperOrchestra's baseline comparison showed exactly this failure mode: shallow citation sets inflate precision and hide missing coverage.

## Literature review quality

Use the six-axis rubric in `references/lit-review-rubric.md`. It scores 0–100 with anti-inflation caps:

- coverage and completeness
- relevance and focus
- critical analysis and synthesis
- positioning and novelty
- organization and writing
- citation practices and rigor

Ground the score against the venue's average citation count. A review that lists papers without synthesis is capped at 60 on critical analysis. A novelty claim without a close comparison is capped at 60 on positioning.

## Overall quality

Use the AgentReview rubric in `references/agentreview.md`: Overall 1–10 plus sub-axes, strengths, weaknesses, questions, and an accept/reject decision. For stability, use three reviews and a meta-review. Report the mean overall and the simulated acceptance rate across papers.

## Side-by-side

Compare two manuscripts produced from the same idea. Evaluate each pair in both orderings to cancel positional bias.

Aggregate the outcomes:

```bash
python scripts/aggregate_sxs.py results.json
```

Input:

```json
[
  {"candidate": "ours", "baseline": "ai-scientist-v2", "winner": "candidate"},
  {"candidate": "ours", "baseline": "ai-scientist-v2", "winner": "tie"}
]
```

Output: candidate wins, baseline wins, ties, and win rate excluding ties. A pair counts as a win when both orderings favor the candidate, or one favors it and the other ties. A loss is the mirror. One win and one loss is a tie.

## Reporting

Write one JSON file per metric under `metrics/`, plus a short `metrics/summary.md`:

- number of papers evaluated
- mean and standard deviation per axis
- citation count mean and F1
- simulated acceptance rate
- side-by-side win/tie/loss counts
- judge model and temperature

Never report a metric without saying what produced it. An LLM score without the model name, rubric, and temperature is not reproducible.

## Honest limitations

- LLM judges reward explicit structure over nuanced narrative. Treat literature-review scores as a relative ranking, not an absolute truth.
- Citation F1 depends on registry quality and title matching. Report unmatched counts.
- Overall quality and acceptance rate are simulations, not peer review.
- Human evaluation remains the gold standard. Use these metrics to catch regressions, not to certify a paper.

## Files

- `scripts/citation_f1.py` — set-based P/R/F1 with optional P0/P1.
- `scripts/aggregate_sxs.py` — side-by-side win/tie/loss aggregation.
- `references/lit-review-rubric.md` — six-axis 0–100 rubric.
- `references/agentreview.md` — reviewer rubric and ensemble protocol.
- `references/sxs-prompts.md` — literature and full-paper SxS prompts.
