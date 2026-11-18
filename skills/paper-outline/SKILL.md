---
name: paper-outline
description: Build the machine-readable plan for an AI research paper: figure plan, intro/related-work search strategy, section outline, and exhaustive citation hints. Use before drafting whenever the user has an idea and experimental log and needs an outline, story, figure plan, paper structure, or search plan, or when another paper-writing skill needs outline.json. Also use to repair or expand an existing outline.
license: Apache-2.0
---

# Outline agent

The outline is the contract for every later stage. It decides which figures to make, what literature to search for, what each section must establish, and which external dependencies must be cited. A good outline is specific enough that a writer can follow it without inventing content.

## Inputs

- `idea.md` — method, contributions, scope.
- `experimental_log.md` — setup, numbers, ablations, observations.
- `template.tex` — the section skeleton to mirror.
- `guidelines.md` — audience, page limit, mandatory sections, formatting.
- Research cutoff date `YYYY-MM` — the newest literature allowed.

Read `references/outline-schema.md` for the exact output shape. Read `references/prompt.md` when you want the full directive text to paste into a subagent.

## Process

1. **Read all four documents.** Do not plan from the idea alone; the experimental log determines which claims and figures are supportable.
2. **Choose the story.** State the hook and the gap in one sentence each, scoped to the datasets and evaluations that exist. A gap the experiments do not test is a hallucination risk.
3. **Plan figures.** For each piece of evidence that is essential to the argument, decide whether it is a data plot or a conceptual diagram. Specify the data source, the chart type, the objective, and an aspect ratio.
4. **Plan the literature search.** Separate macro context (Introduction: foundational work, surveys, impact) from micro comparisons (Related Work: SOTA baselines, benchmarks, limitation evidence). Give concrete queries, not topics.
5. **Plan the sections.** Mirror the template's section commands. For every subsection, write content bullets that name the source material ("formalize the routing loss using Eq. 3 from idea.md"), not vague verbs ("describe the method").
6. **Enumerate citation hints.** Every dataset, metric, optimizer, baseline, architecture, and foundation model that appears in the inputs gets a hint. Use `Author (Exact Title)` when certain, otherwise `research paper or technical report introducing '<Exact Name>'`. Never guess an author.
7. **Validate** with `python scripts/validate_outline.py outline.json`.

## Quality bar

- `plotting_plan` has 2–6 entries for a full paper. Each figure earns its place by supporting a claim.
- Introduction strategy has 3–5 search directions covering impact, surveys, and foundations.
- Related Work has 2–4 methodology clusters. Each cluster has a SOTA mission, a limitation hypothesis, 2–4 narrow queries, and a bridge back to the method.
- Every section in the template appears in `section_plan`, except references and appendix.
- Subsections are not orphaned: if `X.1` exists, `X.2` exists.
- No result number is invented. The outline may point at a number ("report the 4.2-point gain from the log") but must not restate a value it cannot see.

## Output

Write `outline.json` with exactly three top-level keys:

```json
{
  "plotting_plan": [],
  "intro_related_work_plan": {"introduction_strategy": {}, "related_work_strategy": {}},
  "section_plan": []
}
```

Do not add commentary outside the JSON.

## Anti-leakage

Append this constraint to every outline prompt:

> Build the outline exclusively from the provided materials. Do not recall or reconstruct any existing publication, author list, or venue. Do not use external facts or prior familiarity with the work. If a claim is not supported by the inputs, leave it out.

## Files

- `references/outline-schema.md` — field-by-field schema and a full example.
- `references/prompt.md` — the complete outline directive.
- `scripts/validate_outline.py` — structural checks and coverage heuristics.
