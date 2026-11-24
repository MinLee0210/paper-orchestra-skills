# Literature prompts

## Exploration discovery

Find 10–15 highly relevant, influential academic papers matching the search task. Do not force results; only return strictly relevant papers.

Search task: `<FOCUS>`
Context: `<MISSION / HYPOTHESIS / HOOK / GAP>`
Broader project problem: `<PROBLEM_GAP>`
Cutoff: published strictly before `<CUTOFF_DATE>`

Instructions:

1. Use web search to find real papers (arXiv, CVPR, NeurIPS, ICML, ICLR, journals).
2. Return only top-tier venue papers, highly cited work, or the exact state of the art relevant to the task.
3. Return title, year, and a one-line reason for each candidate.

Return JSON:

```json
{
  "section_name": "<SECTION>",
  "candidates": [
    {"title": "<exact title>", "year": 2023, "reason": "<why it matters>"}
  ]
}
```

## Targeted discovery

Identify the specific academic paper described by this hint: `<HINT>`.

Context: `<SECTION CONTEXT>`
Cutoff: published strictly before `<CUTOFF_DATE>`

Instructions:

1. Use web search to find the exact title and year.
2. If the hint refers to a dataset, architecture, metric, optimizer, or baseline, find the primary paper that introduced it.
3. Return exactly one candidate.

Use the same JSON shape.

Section names must match the outline exactly, because `inject_citations.py` joins on them:

- `Introduction`
- `Related Work: <subsection_title>`
- `<section_title> - <subsection_title>`

If a title differs by even a word, the verified papers for that section will not attach to the outline, and the script will report the mismatch.

## Writing Introduction and Related Work

Role: senior AI researcher.

Task: write the Introduction and Related Work sections of a paper.

You are given `template.tex`, the skeleton. Fill in only Introduction and Related Work. Leave every other section untouched.

Inputs:

- `intro_related_work_plan`: primary guide for structure and arguments.
- `project_idea` and `project_experimental_log`: ensure the Introduction frames the actual contribution and results.
- `citation_checklist`: the keys available for citation.
- `collected_papers`: verified papers with abstracts.

You must cite only the given `collected_papers`. Do not introduce new citations.

Citation requirements:

- You have abstracts for `<N>` collected papers.
- Cite every P0 dependency: direct baselines, datasets, metrics, and foundational methods.
- In Related Work, cite at least two verified papers per methodology cluster.
- Do not pad citations to reach an overall percentage.
- Introduction: cite foundational models, key statistics, and broad problem statements.
- Related Work: make deep comparative citations. Group distinct works ("Several methods [A, B, C] ...").
- Every `\cite{key}` must correspond exactly to a key in `citation_checklist`.
- Timeline: do not treat any paper after `<CUTOFF_DATE>` as a prior baseline. Treat it as concurrent work.
- Evaluation: do not claim to beat or achieve state of the art over a specific cited paper unless that paper is evaluated against in `project_experimental_log`. Frame other recent papers as concurrent, orthogonal, or conceptual.

Return the full updated `template.tex` inside a ` ```latex ` block. Keep packages, styles, and other sections identical.

Notes:

- Do not change `\usepackage[capitalize]{cleveref}` to `cleverref`; there is no `cleverref.sty`.
- Do not invent a citation key. If a claim needs support and no verified paper covers it, soften or remove the claim.

## Anti-leakage block

Append to every prompt:

> Write as if you have no prior knowledge of the topic, method, experiments, or results. Construct the text exclusively from the provided materials and verified papers. Do not recall or reconstruct an existing publication, author list, or venue. Do not infer author identities or affiliations. This constraint overrides all other instructions.
