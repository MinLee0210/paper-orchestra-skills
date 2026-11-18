# Offline demo paper

This directory is a complete, synthetic end-to-end run of the skills. It is
here to show the shape of every artifact and to give the tests something real
to check. It is **not** a real publication and the numbers are illustrative.

## What is included

| Path | What it is |
|---|---|
| `raw_materials/` | idea and experimental log |
| `outline.json` | final outline with citation candidates |
| `literature_agent_output/` | 12 cached citation fixtures, BibTeX, citation map, cited template |
| `figures/` | two data plots and one vector schematic, plus `info.json` |
| `latex_writeup/raw_draft_paper.tex` | compiled 5-page draft |
| `content_refinement_workdir/` | draft v0, v1, three-review ensembles, worklogs, page screenshots |
| `final_paper.tex`, `final_paper.pdf` | accepted output |
| `run_report.json` | stage-by-stage record and warnings |

Open `final_paper.pdf` to inspect the output.

## Honest caveats

- The citation registry is a **cached local fixture** so the demo works offline.
  Run `paper-literature-review` against Semantic Scholar, arXiv, Crossref, or
  DBLP before using this workflow for a real paper.
- The reviewer scores are illustrative samples from the demo, not independent
  human reviews.
- The paper is about two synthetic tasks. It does not claim real benchmark
  results.

## Regenerate the deterministic parts

```bash
python skills/paper-inputs/scripts/validate_inputs.py examples/paper-project
python skills/paper-literature-review/scripts/build_bib.py \
  --registry examples/paper-project/literature_agent_output/registry.json \
  --out examples/paper-project/literature_agent_output
python skills/paper-literature-review/scripts/inject_citations.py \
  --outline examples/paper-project/literature_agent_output/outline_plan.json \
  --registry examples/paper-project/literature_agent_output/registry.json \
  --out examples/paper-project/literature_agent_output/outline_v1.json
```

The figures are reproducible with:

```bash
python -m venv /tmp/paper-venv
/tmp/paper-venv/bin/pip install matplotlib
/tmp/paper-venv/bin/python examples/paper-project/scripts/make_demo_figures.py
```

Recompile the paper with:

```bash
python skills/paper-content-refinement/scripts/compile_latex.py \
  examples/paper-project/content_refinement_workdir --name final_paper
```
