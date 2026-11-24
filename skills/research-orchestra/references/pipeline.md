# Pipeline contracts

This file is the detailed companion to `SKILL.md`. Read it when you need exact artifact shapes or failure behavior.

## Stage contracts

| Stage | Skill | Reads | Writes | Hard gate |
|---|---|---|---|---|
| 0 | `research-inputs` | user files | normalized `raw_materials/` | required files exist; no leaked citations or author identities |
| 1 | `research-outline` | idea, log, template, guidelines | `outline.json` | valid JSON; three top-level plans; citation hints cover every named dependency |
| 2a | `research-literature-review` | outline, idea, log, template, guidelines | `literature_agent_output/*` | every paper verified; cutoff respected; >=20 unique papers for a full paper (below that the validator warns and the orchestrator must tell the user coverage is thin) |
| 2b | `research-plotting` | outline, idea, log | `figures/*`, `plotting_results.json`, `figures/info.json` | every planned figure produced or explicitly skipped with a reason |
| 3 | `research-section-writing` | merged template, outline, citation map, figures, inputs | `latex_writeup/raw_draft_paper.tex` | PDF compiles |
| 4 | `research-content-refinement` | draft, log, citation map, guidelines | `final_paper.tex`, `final_paper.pdf` | compile succeeds; page limit respected; no undefined citations/refs |
| 5 | `research-evaluation` | final PDF/TeX, optional ground truth | `metrics/*.json` | metrics are computed from real files, not estimated |

## `outline.json`

Top-level keys, all required:

```json
{
  "plotting_plan": [],
  "intro_related_work_plan": {
    "introduction_strategy": {},
    "related_work_strategy": {}
  },
  "section_plan": []
}
```

After the literature stage, `outline.json` is replaced by `outline_v1.json`, which adds `citation_candidates` to each plan node and removes `citation_hints`.

## `registry.json`

The citation registry is the source of truth for bibliography generation. It is a JSON array of objects:

```json
[
  {
    "citation_key": "Vaswani2017Attention",
    "paper_id": "204e3073870fae3d05bcbc2f6a8e263d9b72e776",
    "title": "Attention Is All You Need",
    "authors": ["Ashish Vaswani", "Noam Shazeer"],
    "venue": "NeurIPS",
    "year": 2017,
    "abstract": "The dominant sequence transduction models ...",
    "citation_count": 100000,
    "found_in_section": "Related Work: Efficient Attention",
    "reason": "Foundational architecture",
    "journal": null,
    "volume": null,
    "pages": null,
    "publication_date": "2017-06-12"
  }
]
```

`citation_map.json` is a dictionary keyed by `citation_key` containing only the fields the writing agent needs: `citation_key`, `title`, `authors`, `venue`, `year`, `abstract`.

## Merge step

After literature and plotting:

```bash
cp literature_agent_output/outline_v1.json outline.json
cp -r latex_template/. latex_writeup/
cp literature_agent_output/updated_template.tex latex_writeup/template.tex
cp literature_agent_output/references.bib latex_writeup/references.bib
cp -r figures/. latex_writeup/figures/
```

The merge is not optional. Writing from the pre-literature template produces uncited Introduction and Related Work sections, and writing without `references.bib` produces undefined citations. Copying the full template directory keeps the venue's `.sty`, `.bst`, and `guidelines.md` beside the draft. A user-supplied `raw_materials/references.bib` is not part of the merge: the literature stage re-verifies its entries, and the merge copies only the verified bibliography.

## Retry policy

- A stage may retry internally (for example, a search task or a figure) as many times as its own skill allows.
- The orchestrator retries a whole stage at most twice.
- On the third failure, stop. Write the failing command, stderr tail, and artifact path into `run_report.json`, then report to the user.
- Never replace a failed artifact with a hand-written approximation. A missing figure is better than a fabricated one.

## Resume

`scripts/pipeline_status.py` inspects the filesystem and prints the next runnable stage. Use it after an interruption or before starting work in an existing project. It does not call an LLM and does not modify files.

## Parallelism

Stages 2a and 2b are safe to run concurrently because they share only the immutable outline and raw materials. They write to separate directories. Do not run two stages that write the same file concurrently.
