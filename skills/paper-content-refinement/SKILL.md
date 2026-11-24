---
name: paper-content-refinement
description: Iteratively review, revise, and compile a LaTeX research paper using simulated peer review and a visual formatting pass, keeping only revisions that do not lower the score. Use when a draft already exists and the user wants to improve it, address reviewer feedback, fix page-limit or layout problems, resolve LaTeX compile errors, or produce the final PDF. Also use after section writing as the final stage of the paper pipeline.
license: Apache-2.0
---

# Content refinement agent

A draft that compiles is not a paper that reads well. This stage runs a score-driven revision loop: review the compiled PDF, revise the source, recompile, re-review, and keep the revision only when the score does not drop (a tie needs non-negative sub-axis progress). It then runs a separate visual pass for layout defects.

The accept/reject rule is deliberate. Without it, a revision loop drifts: each round fixes one complaint and introduces another, and the final draft is worse than the first. The rule makes progress monotonic.

## Inputs

- `latex_writeup/raw_draft_paper.tex` and the surrounding directory (template, style files, bibliography, figures).
- `experimental_log.md` — ground truth for every number.
- `citation_map.json` — allowed bibliography.
- `guidelines.md` — page limit, anonymity, formatting.
- Optional: a human reviewer's comments, or previous review JSON.

## Loop

1. **Copy the draft tree** into `content_refinement_workdir/` and work there. Keep `latex_writeup/` untouched so a failed loop can restart from the original draft.
2. **Compile the baseline.** If it does not compile, stop and fix LaTeX first. A review of a broken PDF is noise.
3. **Render pages** to PNGs (or 2×2 grids) for visual review.
4. **Review with an independent reviewer.** Use a fresh reviewer subagent or a separate context; the writer must not grade its own revision. Generate **3 independent reviews** at temperature 0.75 with `references/reviewer-rubric.md`, then aggregate them. This reduces the variance that otherwise flips the keep/revert decision.
5. **Revise.** Address weaknesses and questions in the manuscript itself, not in a response letter. Answer questions by adding the information to the paper where it naturally belongs. Ignore requests for new experiments that are not in the log. Output a JSON worklog plus the full revised LaTeX.
6. **Compile the revision.** If compilation fails, revert and try again; do not keep a broken revision.
7. **Re-review.** Score the new PDF with the same rubric, temperature, and a fresh reviewer; again use 3 samples and aggregate.
8. **Decide.** Use:

   ```bash
   python scripts/aggregate_reviews.py review_v0_a.json review_v0_b.json review_v0_c.json --out review_v0.json
   python scripts/aggregate_reviews.py review_v1_a.json review_v1_b.json review_v1_c.json --out review_v1.json
   python scripts/decide_revision.py --before review_v0.json --after review_v1.json
   ```

   - Overall increased → accept and continue.
   - Overall decreased → reject and stop.
   - Overall tied and sub-axis gains >= drops → accept the revision, then stop: the score has stalled.
   - Overall tied and drops > gains → reject and stop.

9. **Stop** when the score decreases, the sub-axes degrade on a tie, the score ties (the tied revision is kept, but a stalled score earns no further round), the revision limit is reached (default 3), or two consecutive revisions produce no change.
10. **Formatting pass.** Review the page images against `guidelines.md`, fix overflow, spacing, page limit, and typography, and compile again. Formatting changes must not alter claims, numbers, or citations.

## Output

Copy the accepted result to the project root:

- `final_paper.tex`
- `final_paper.pdf`
- `content_refinement_workdir/content_refinement_worklog.json` — decisions and scores per round
- `content_refinement_workdir/format_refinement_worklog.json` — formatting issues and fixes
- `content_refinement_workdir/peer_reviews/review_v*.json` — aggregated reviews
- `content_refinement_workdir/peer_reviews/raw/review_v*_*.json` — individual reviewer samples
- `content_refinement_workdir/pdf_screenshots/` — rendered pages used for review

## Score discipline

- Use integers on the rubric scale.
- Do not inflate scores to justify a revision. A tie is a valid outcome.
- Score the paper you have, not the paper you intended.
- If the reviewer cannot see a claimed contribution in the PDF, it does not exist for scoring purposes.

## Formatting rules

- **Page limit:** count pages up to and including the start of References. Condense by removing non-informational adjectives, merging short paragraphs, and tightening spacing around floats. Never remove core contributions, main results, the abstract, or the conclusion.
- **Figures:** place near the first reference, before the conclusion, at column width. Use `figure*` only for wide figures.
- **Tables:** use `\small` or `\footnotesize` before switching to `tabularx`; abbreviate headers; never let a table spill into the gutter. Adding `\usepackage{tabularx}` is the one preamble change the formatting pass may make, because no bundled template loads it; do not add other packages.
- **References:** every `\cite` resolves; every `\ref` resolves; no `??`.
- **Typography:** fix orphans and widows; no blank pages containing only a float.

Read `references/format-prompt.md` for the visual review prompt.

## Practical commands

```bash
python scripts/compile_latex.py content_refinement_workdir --name raw_draft_paper
python scripts/render_pages.py content_refinement_workdir/raw_draft_paper.pdf content_refinement_workdir/pdf_screenshots/v0
```

`compile_latex.py` runs the full pdflatex/bibtex/pdflatex/pdflatex sequence, writes a compile log, and reports undefined references. `render_pages.py` requires PyMuPDF and optionally Pillow for grids.

## Failure handling

- **Compile fails:** inspect the log tail, fix the first error only, recompile. Do not shotgun-edit.
- **Score stalls:** stop (a tie counts as a stall). More rounds at the same score waste budget and risk drift.
- **Reviewer asks for missing experiments:** ignore the request and note it in the worklog. This stage refines presentation, not science.
- **Page limit cannot be met without removing content:** tell the user which section is over and by how much. Do not silently delete results.

## Files

- `references/reviewer-rubric.md` — AgentReview-style rubric and JSON schema.
- `references/refinement-prompt.md` — revision prompt and worklog format.
- `references/format-prompt.md` — visual formatting review prompt.
- `scripts/compile_latex.py` — deterministic LaTeX build.
- `scripts/render_pages.py` — PDF to PNG pages/grids.
- `scripts/aggregate_reviews.py` — mean/median aggregation of independent reviews.
- `scripts/decide_revision.py` — accept/reject decision from two aggregated review JSONs.
