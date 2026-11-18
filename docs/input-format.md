# Input format

The pipeline treats two documents as ground truth: `idea.md` and `experimental_log.md`. Everything else is scaffolding.

## Project layout

```text
my-project/
├── raw_materials/
│   ├── idea.md
│   ├── experimental_log.md
│   └── figures/
│       ├── fig_example.pdf
│       ├── fig_example.png
│       └── info.json
└── latex_template/
    ├── template.tex
    ├── guidelines.md
    ├── references.bib
    └── *.sty / *.bst
```

## `idea.md`

Purpose: explain the method well enough that a writer can formalize it without guessing.

Required sections:

| Section | What it must contain |
|---|---|
| Problem | the specific gap, scoped to the datasets and evaluations in the log |
| Method | mechanism, notation, equations that must survive |
| Contributions | 3–5 claims the experiments can support |
| Assumptions and scope | what is not claimed |
| Alternative approaches | conceptual alternatives, without citations |

Forbidden content:

- result numbers
- citation keys, URLs, arXiv IDs, or the source paper's title
- author names, affiliations, acknowledgements
- claims the experiments do not test

## `experimental_log.md`

Purpose: the only source of numbers in the paper.

Required sections:

| Section | What it must contain |
|---|---|
| Setup | datasets, sizes, splits, metrics, baselines, implementation details |
| Main results | exact values in markdown tables |
| Ablations | one row per variant with the variable that changed |
| Qualitative observations | standalone facts, no "see Figure 3" |
| Failed runs and caveats | optional but valuable |

Rules:

- One fact per bullet.
- Stable precision and units.
- If a value is uncertain, write `UNVERIFIED: <value>` and surface it to the user.
- Never round a value to make a story cleaner.

## Figures

`info.json` is a list of `{"name": "...", "caption": "..."}`. The `name` must match a file in the same directory, including the extension.

Use PDF for vector figures and PNG for raster previews. One figure per file. Do not combine panels the paper should reference separately.

## Template

Required: `template.tex`, `guidelines.md`, `references.bib`. The template must compile before generation. Section placeholders can be empty `\section{...}` commands or explicit `% TODO` comments.

See the `paper-template` skill and `skills/paper-template/references/template-contract.md`.

## Validation

```bash
python skills/paper-inputs/scripts/validate_inputs.py my-project
python skills/paper-outline/scripts/validate_outline.py my-project/outline.json
python skills/paper-literature-review/scripts/validate_literature.py \
  --dir my-project/literature_agent_output \
  --outline my-project/outline.json \
  --template my-project/literature_agent_output/updated_template.tex
```

The input validator blocks on leaked citations, `et al.` and author-year citations, named authors, institutions, and result numbers in `idea.md`. Numbered figure/table references are warnings. It is heuristic, so read the excerpts; use `--warn-only` for a non-blocking audit and `--source-title` to check for a known source title.

## Research cutoff

The cutoff is the venue's submission deadline in `YYYY-MM`. It decides which papers count as prior work. A November 2024 cutoff means a December 2024 paper is concurrent work, not a baseline.

Record the cutoff in `run_report.json` and pass the same value to discovery and verification. Do not change it mid-run.

## Minimal synthetic example

The repository includes `examples/paper-project/` with a matching idea, log, and template scaffold. It is synthetic and exists to exercise the workflow, not to demonstrate research results.

```bash
python skills/paper-inputs/scripts/validate_inputs.py examples/paper-project
```
