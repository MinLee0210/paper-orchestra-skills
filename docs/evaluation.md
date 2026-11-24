# Evaluation

Four measurements are supported. Each has a deterministic script or a fixed rubric, so results are comparable across runs.

## Citation F1

```bash
python skills/research-evaluation/scripts/citation_f1.py \
  --gt ground_truth_registry.json \
  --gen generated_registry.json
```

Matching is by Semantic Scholar ID first, then by normalized title. The output contains:

- overall precision, recall, F1, and matched count;
- P0 recall (must-cite coverage);
- P1 recall (breadth);
- unmatched titles from both sides.

P0 and P1 come from per-paper `priority` labels or from explicit `p0_ids`/`p1_ids` sets.

### Interpretation

A low citation count can produce a high F1 because precision dominates. Always report the generated citation count next to F1. PaperOrchestra's baseline comparison showed systems citing 9–14 papers with competitive F1 but near-zero P1 recall.

## Literature review quality

Use `skills/research-evaluation/references/lit-review-rubric.md`. Six axes, 0–100, with anti-inflation caps:

| Axis | Weight |
|---|---:|
| Coverage and completeness | 20% |
| Relevance and focus | 15% |
| Critical analysis and synthesis | 25% |
| Positioning and novelty | 25% |
| Organization and writing | 10% |
| Citation practices and rigor | 5% |

Caps matter: a descriptive review cannot score above 60 on synthesis, and an unsupported novelty claim cannot score above 60 on positioning. Ground the volume score against the venue's average citation count.

## Overall quality

Use `skills/research-evaluation/references/agentreview.md`. Overall 1–10, sub-axes, strengths, weaknesses, questions, and accept/reject. For stability, use three independent reviews at temperature 0.75 and aggregate them:

```bash
python skills/research-content-refinement/scripts/aggregate_reviews.py   review_a.json review_b.json review_c.json --out review.json
```

The default is the mean; `--stat median` is available. The aggregate records per-axis standard deviation, so a high-variance score is visible rather than hidden.

Report the mean overall score and the simulated acceptance rate. Both are simulations, not peer review.

## Side-by-side

Use `skills/research-evaluation/references/sxs-prompts.md` for the two comparison prompts. Evaluate each pair in both orderings, then aggregate:

```bash
python skills/research-evaluation/scripts/aggregate_sxs.py results.json
```

A pair is a candidate win when both orderings favor it, or one favors it and the other ties. A loss is the mirror. One win and one loss is a tie.

## Reporting template

```text
Papers: 20
Judge: <model>, temperature 0.0 (SxS), 0.75 (AgentReview)
Citation count: 46.2 ± 7.8
Overall citation F1: 0.41
P0 recall: 0.64   P1 recall: 0.17
Literature review overall: 76.3
Simulated acceptance rate: 81%
SxS vs baseline: 14 wins, 4 ties, 2 losses (70% excluding ties)
```

Every number needs its judge, rubric, and sampling. An LLM score without that context is not reproducible.

## Known limitations

- LLM judges reward explicit formatting over nuanced narrative. Use them for relative comparisons.
- Citation F1 depends on registry quality; report unmatched counts.
- Acceptance rates are simulated.
- Human evaluation remains the gold standard.

Use these metrics to catch regressions and compare pipelines. Do not use them to certify a paper.
