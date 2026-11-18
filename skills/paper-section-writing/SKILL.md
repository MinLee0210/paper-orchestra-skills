---
name: paper-section-writing
description: Write the remaining sections of a LaTeX research paper from a structured outline, verified citation map, figures, and experimental log, producing a complete compilable manuscript. Use after the Introduction and Related Work are filled, or whenever the user needs the abstract, method, experiments, results, discussion, conclusion, tables, or appendix drafted into an existing template. Do not use to invent results or to fill in missing data.
license: Apache-2.0
---

# Section writing agent

The outline is the plan; the experimental log is the truth; the citation map is the allowed bibliography; the figures are the available evidence. This stage merges them into a complete LaTeX draft.

## Inputs

- `latex_writeup/template.tex` — Introduction and Related Work already written, other sections empty.
- `outline.json` (the `outline_v1.json` produced by the literature stage) — section plan with `citation_candidates`.
- `idea.md` — method details and equations.
- `experimental_log.md` — every number and table.
- `citation_map.json` — keys, titles, authors, and abstracts.
- `figures/info.json` and the figure files — after the merge these live in `latex_writeup/figures/`.
- `guidelines.md` — page limit, formatting, mandatory sections.

Read `references/prompt.md` for the full writing directive and `references/latex-conventions.md` before editing.

## Process

1. **Read the whole template first.** Identify which sections are filled and which are placeholders. Never rewrite a filled section except for consistency.
2. **Map outline sections to LaTeX sections.** The outline uses titles like `3. Methodology`; match them to `\section{...}` and subsections.
3. **Draft in order:** Abstract, Method, Experiments, Results/Discussion, Conclusion, then Appendix. The abstract is easier to write after the results are placed.
4. **Build tables from the log.** Use `booktabs` (`\toprule`, `\midrule`, `\bottomrule`). Copy exact values. If the log has no value for a cell, leave it empty or remove the row; do not estimate.
5. **Place every figure.** Use the exact filename and extension from `info.json`. One `\includegraphics` per figure; do not combine figures. Reference each figure in the text before or near its placement.
6. **Cite from the map.** Use only `citation_candidates` for that subsection. When describing a cited paper, use its abstract from the map.
7. **Keep the math grounded.** Formalize definitions, losses, and algorithms that appear in `idea.md`. Do not introduce variables or theorems the inputs do not support.
8. **Compile.** Run the compile script from `paper-content-refinement`. Fix errors before returning.
9. **Lint.** Run `python scripts/lint_latex.py` to catch unresolved citations, missing figures, and unbalanced environments.

## Content rules

- **No invented numbers.** Every quantitative claim traces to `experimental_log.md`.
- **No invented citations.** Every key exists in `citation_map.json`.
- **No orphan figures or tables.** Each one is referenced in the text.
- **No missing figures.** Use all figures in `info.json`; if one cannot be used, say why in the handoff.
- **Tables and figures before the Conclusion**, unless deliberately placed in the Appendix.
- **Appendix after References**, on a fresh page if the venue requires it.
- **Limitations and future work** at the end of the main text when the venue expects them. Do not turn a limitation into a hidden claim.
- **Dense academic tone.** No marketing adjectives, no "revolutionary", no "groundbreaking".

## LaTeX rules

- Preserve the preamble, document class, and package list.
- In a two-column venue, prefer single-column `figure` unless the figure is explicitly wide; then use `figure*` and close it with `\end{figure*}`.
- Use `width=\linewidth` or `width=\columnwidth`; never set both width and height, which distorts the aspect ratio.
- Do not change `cleveref` to `cleverref`.
- Do not add packages unless the template already loads them.
- Keep indentation and spacing consistent with the template.

## Output

Write `latex_writeup/raw_draft_paper.tex` containing the full document, not a diff.

Handoff message:

- sections written
- tables created and their source rows
- figures included
- citation keys used
- anything skipped and why
- compile status

## Files

- `references/prompt.md` — complete section-writing directive.
- `references/latex-conventions.md` — table, figure, citation, and appendix patterns.
- `scripts/lint_latex.py` — structural and reference checks.
