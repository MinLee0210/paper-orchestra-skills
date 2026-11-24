---
name: research-inputs
description: Prepare, normalize, and audit raw materials for automated research-paper writing. Use whenever a user is starting a paper project, has messy notes or experiment outputs, needs an idea.md or experimental_log.md, wants to remove citations, author identities, or leaked paper metadata before generation, or needs figures/info.json. Also use when the research-orchestra pipeline fails its input gate.
license: Apache-2.0
---

# Raw materials for paper generation

The writing pipeline is only as good as its inputs. This skill turns whatever the user has — notes, a repo, a results table, a draft — into the two documents the rest of the pipeline treats as ground truth.

## Why the constraints exist

PaperOrchestra generates a paper *from materials*, not from the model's memory. If the idea file already contains the final claims, the writer merely paraphrases. If the log is missing a number, the writer invents one. If either file still names the original paper, its authors, or its citations, the model can reconstruct memorized text and the evaluation becomes meaningless. The rules below protect the reconstruction from all three failure modes.

## Required inputs

```text
raw_materials/
├── idea.md                 # what the method is and why it should work
├── experimental_log.md     # what was actually run and measured
└── figures/                # optional existing figures
    ├── fig_example.png
    └── info.json           # optional: [{"name": "...", "caption": "..."}]
latex_template/
├── template.tex
├── guidelines.md
└── *.sty / *.bst
```

## `idea.md`

Write it as a self-contained technical brief. It should include:

1. **Problem** — the specific gap, scoped to the datasets and evaluations that exist.
2. **Method** — the mechanism, notation, and any equations the paper must preserve.
3. **Contributions** — 3–5 claims the experiments can actually support.
4. **Assumptions and scope** — what the method does *not* claim.
5. **Prior approaches** — conceptual alternatives, described without citation keys.

Do not include:

- Result numbers or table values (those belong in the log).
- Citation keys, URLs, arXiv IDs, or paper titles from the source paper.
- Author names, affiliations, acknowledgements, or "our previous work" phrasing.
- Claims that the experiments do not test.

Use `assets/idea_template.md` as a starting point.

## `experimental_log.md`

This file is the *only* source of numbers. It should include:

1. **Setup** — datasets with sizes and splits, metrics, baselines, implementation details, hardware if known.
2. **Main results** — exact values, preferably as a markdown table with the same columns the paper will use.
3. **Ablations** — one row per variant, with the variable that changed.
4. **Qualitative observations** — what the authors noticed, written as standalone facts rather than references to a figure ("the baseline degrades sharply after 8 frames" rather than "see Figure 3").
5. **Failed runs and caveats** — optional but valuable; they prevent overclaiming.

Do not include:

- Figure or table numbers from an existing paper ("Table 2 shows...").
- Citations or comparisons framed as "unlike [12]".
- Rounded or invented values. If a number is uncertain, write `UNVERIFIED: <value>` and tell the user.

Use `assets/experimental_log_template.md` as a starting point.

## Figures

If the user already has figures, copy them into `raw_materials/figures/` and write `info.json`:

```json
[
  {"name": "fig_architecture.png", "caption": "Overview of the proposed pipeline."},
  {"name": "fig_ablation.pdf", "caption": "Ablation on the number of blocks."}
]
```

Rules:

- Use the filename exactly, including extension.
- One figure per file; do not combine panels that the paper should reference separately.
- Captions describe what is visible. Do not claim a trend the plot does not show.
- If a figure is a PDF, the writing stage can include it but a vision-based reviewer cannot inspect it. Render a PNG copy when possible.

If there are no figures, that is fine: the plotting stage generates them.

## Leakage audit

Run the validator before any expensive stage:

```bash
python scripts/validate_inputs.py /path/to/paper_project
```

It treats leakage as a **blocking error**, not a warning. It detects:

- LaTeX citations, bracketed citations, arXiv IDs, DOIs, and URLs;
- author-year citations, `et al.` citations, and named attributions such as "by John Doe";
- author, affiliation, institution, and company markers;
- result leakage in `idea.md`: percentages, metric values, improvement claims, and mean/variance pairs.

The experimental log is the place for numbers, so result-number patterns are applied only to `idea.md`. Numbered figure/table references remain warnings because they are easy to de-contextualize. Use `--warn-only` when you want an audit without blocking, and `--source-title "..."` when you know the source paper title and want an exact check.

The validator is heuristic. Read the excerpts it prints; a false positive is cheaper than a leaked paper.

## Normalization tips

- Convert tables to Markdown so every row is visible to the writer.
- Put one fact per bullet; long prose hides numbers.
- Spell out metric definitions once (`Jaccard index J`, `F-score F`) and use the same symbol everywhere.
- Keep units and precision stable (`45.2`, not sometimes `45.20` and sometimes `~45`).
- If the user supplies a paper draft, extract the method and the results separately. Never copy the draft's Introduction or Related Work into `idea.md`; those sections must be regenerated from verified literature.

## Handoff

When the inputs pass, tell the orchestrator:

- project path
- research cutoff (`YYYY-MM`)
- whether figures were supplied
- any `UNVERIFIED` values the user must confirm
