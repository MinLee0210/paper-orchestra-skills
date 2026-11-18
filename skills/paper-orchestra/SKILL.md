---
name: paper-orchestra
description: End-to-end orchestration for writing a submission-ready AI research paper from raw materials. Use when the user wants to generate, draft, write, or assemble a full research paper, LaTeX manuscript, or conference submission from an idea file plus experimental logs, or wants the complete PaperOrchestra multi-agent workflow run or resumed. Coordinates outline generation, figure generation, verified literature review, section writing, content refinement, and optional evaluation. Do not use for editing a single paragraph or for a literature-only request; use the narrower paper-* skill instead.
license: Apache-2.0
---

# PaperOrchestra Orchestrator

Turn unstructured pre-writing materials into a submission-ready LaTeX manuscript and PDF by running five specialist stages with explicit quality gates.

The design comes from **PaperOrchestra** (Song et al., 2026), a multi-agent framework for automated AI research paper writing. This skill is the entry point: it decides what to run, in what order, and whether the result is good enough to advance.

## Why this is split into stages

A single monolithic prompt produces fluent but shallow papers: missing citations, invented numbers, and figures that do not match the data. PaperOrchestra avoids that by giving each stage a narrow job, a machine-readable artifact, and a gate. The gaps between stages are where an agent can inspect, retry, or ask the user instead of silently degrading the paper.

## Inputs

Required:

- `raw_materials/idea.md` — methodology, contributions, and theoretical framing. No results.
- `raw_materials/experimental_log.md` — setup, numbers, tables, ablations, qualitative observations.
- `latex_template/` — a directory containing `template.tex` and `guidelines.md`, plus the venue's `.sty`/`.bst` files. Use the `paper-template` skill to select or scaffold one.

Optional:

- `raw_materials/figures/` — existing figures. Add `info.json` with `[{"name": "...", "caption": "..."}]` when available.
- `raw_materials/references.bib` — a starting bibliography, if the user already has one.

If the inputs are missing, incomplete, or contaminated with citations or author identities, run the `paper-inputs` skill first.

## Output layout

Create this structure in the working directory (or the path the user names):

```text
paper_project/
├── raw_materials/                 # inputs, copied unchanged
├── latex_template/                # inputs, copied unchanged
├── outline.json                   # stage 1, updated by stage 2
├── plotting_results.json          # stage 2
├── figures/                       # generated or supplied figures
│   └── info.json                  # name + caption pairs
├── literature_agent_output/       # stage 2
│   ├── registry.json
│   ├── citation_map.json
│   ├── references.bib
│   ├── updated_template.tex
│   └── outline_v1.json
├── latex_writeup/
│   ├── template.tex               # updated template with Intro/Related Work
│   ├── raw_draft_paper.tex        # stage 3
│   └── figures/
├── content_refinement_workdir/    # stage 4
├── final_paper.tex
├── final_paper.pdf
├── metrics/                       # optional stage 5
└── run_report.json
```

Never edit `raw_materials/` or `latex_template/`. Copy them into the project first so a retry can restart from a clean input.

## Workflow

### 0. Validate and scaffold

1. Confirm the project directory and copy inputs into the layout above.
2. Run the `paper-inputs` skill's validator if available:

   ```bash
   python <paper-inputs>/scripts/validate_inputs.py paper_project
   ```

3. Choose a venue template with the `paper-template` skill. Record the research cutoff date (the venue submission deadline, `YYYY-MM`). Default to the user's stated cutoff; never invent one.
4. Copy `assets/run_report_template.json` to `run_report.json` and fill in the project path, cutoff, and template. Update it as stages complete.

### 1. Outline

Load the `paper-outline` skill and produce `outline.json`.

Gate: the file must parse as JSON and contain `plotting_plan`, `intro_related_work_plan`, and `section_plan`. Every dataset, metric, optimizer, baseline, and foundation model mentioned in the inputs should have a `citation_hints` entry.

### 2. Literature review and figures, in parallel

These two stages are independent after the outline exists. Run them concurrently when the environment supports subagents or parallel tool calls; otherwise run literature first, then plotting.

- `paper-literature-review` consumes `outline.json`, `idea.md`, `experimental_log.md`, `template.tex`, `guidelines.md`, and the cutoff. It writes `registry.json`, `citation_map.json`, `references.bib`, `updated_template.tex`, and `outline_v1.json`.
- `paper-plotting` consumes `outline.json` and the raw materials. It writes figures plus `plotting_results.json` and `figures/info.json`.

Merge after both finish:

1. Replace `outline.json` with `outline_v1.json`.
2. Copy the full `latex_template/` directory into `latex_writeup/` (style files, `guidelines.md`, `references.bib`).
3. Overwrite `latex_writeup/template.tex` with `updated_template.tex`.
4. Overwrite `latex_writeup/references.bib` with the verified bibliography.
5. Copy `figures/` (including `info.json`) into `latex_writeup/figures/`.

Gate: every citation key in `citation_map.json` must resolve in `references.bib`; every `citation_candidates` key in the outline must exist in the citation map; every figure named in `info.json` must exist. If the literature stage found fewer than 20 unique papers for a research paper, re-run the missing search tasks or tell the user the coverage is thin.

### 3. Section writing

Load `paper-section-writing`. It fills every empty section of `latex_writeup/template.tex` and writes `latex_writeup/raw_draft_paper.tex`.

Gate: the draft compiles. Run the compile script from `paper-content-refinement`:

```bash
python <paper-content-refinement>/scripts/compile_latex.py latex_writeup --name raw_draft_paper
```

A missing PDF is a hard stop. Fix the LaTeX or retry the section-writing step; do not pass a broken draft into refinement.

### 4. Content refinement

Load `paper-content-refinement`. It reviews the compiled PDF, revises, recompiles, and keeps a revision only when the reviewer score improves (or ties with non-negative sub-axis gains). It then runs a visual formatting pass.

Outputs: `final_paper.tex` and `final_paper.pdf`.

Gate: the PDF exists, compiles from the final `.tex`, respects the page limit in `guidelines.md`, and contains no unresolved `??` references or undefined citation warnings.

### 5. Optional evaluation

Load `paper-evaluation` when a ground-truth paper, baseline, or benchmark is available. It computes citation precision/recall/F1, literature-review quality, and side-by-side wins. Store results under `metrics/`.

## Invocation pattern

When you have a subagent tool, hand each stage a self-contained brief:

```text
Use the paper-outline skill.
Project: /abs/path/paper_project
Inputs: raw_materials/idea.md, raw_materials/experimental_log.md,
        latex_template/template.tex, latex_template/guidelines.md
Cutoff: 2024-11
Write: /abs/path/paper_project/outline.json
Constraints: treat only the provided materials as ground truth; do not invent
results; produce the JSON schema in the skill's references/outline-schema.md.
```

Do not paste the entire skill into the subagent prompt. Point at the skill and at the files. Pass forward only the artifact paths and the gate result.

## Resume rules

Before running a stage, check whether its artifact already exists and passes its gate. If it does, skip the stage and report that it was reused. If an artifact is stale (an input changed after it was written), delete it and rerun. Record every skip and retry in `run_report.json` so the user can see what actually happened.

## Non-negotiable rules

- **Ground truth is the experimental log.** No number, table cell, or claim about results may appear that is not traceable to it.
- **No invented citations.** Every reference must be verified against a real bibliographic source before it enters `references.bib`. The literature skill enforces this; the orchestrator enforces that the gate is run.
- **No leakage.** Write as if the model has no prior knowledge of the paper. Do not reconstruct a known publication, author list, or venue from memory.
- **No silent failure.** If a stage cannot meet its gate after two retries, stop and report the exact failing artifact and error. Do not hand the user a plausible-looking but unverified PDF.

## References

- `references/pipeline.md` — stage contracts, artifact schemas, and failure handling.
- `scripts/pipeline_status.py` — inspect a project and report the next runnable stage.

## Attribution

Ported from Google Research's PaperOrchestra (Apache-2.0). The original implementation is a Python/Gemini application; this repository keeps the method and prompts but expresses them as agent skills and provider-neutral scripts. See the repository `NOTICE`.
