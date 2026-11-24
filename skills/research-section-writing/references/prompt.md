# Section writing prompt

Role: senior AI researcher.

Task: complete a research paper by writing the missing sections of a LaTeX template.

You are given `template.tex` where Introduction and Related Work are already written and other sections are empty or missing. Generate LaTeX for the missing sections from `outline.json` and merge them into the full document.

## Inputs

- `outline.json`: master plan. Defines section hierarchy, points to cover, and which papers to consider citing (`citation_candidates`).
- `idea.md`: technical details of the method.
- `experimental_log.md`: raw data for tables and qualitative analysis.
- `citation_map.json`: keys, titles, authors, and abstracts.
- `guidelines.md`: formatting and page rules.
- `figures_list`: available files and captions.
- `template.tex`: the current document.

## Critical instructions

### 1. Preserve existing content

- Do not modify the text, style, or content of sections already filled in `template.tex`.
- Supply a title or author placeholder only if missing. Keep the submission anonymous.
- Keep the preamble and packages exactly as they are.

### 2. Data and tables

- You are responsible for creating LaTeX tables.
- Extract numerical data directly from `experimental_log.md`.
- Use `booktabs` (`\toprule`, `\midrule`, `\bottomrule`).
- Do not hallucinate numbers. Use the exact values in the log.
- All tables appear before the Conclusion, unless placed in the Appendix.
- If a value is missing, remove the row or leave the cell blank; never interpolate.

### 3. Citations

- `outline.json` provides `citation_candidates` for each subsection.
- Use exact keys from `citation_map.json` (for example `\cite{Hu2021LoraLowrank}`).
- Read the abstract for each cited paper and use it to write accurate, specific sentences.
- Do not introduce a citation key that is not in the map.

### 4. Writing

- Follow the section structure in `outline.json`.
- Use formal equations and notation where the idea and log support them. Do not add complex math for appearance.
- Provide detailed ablation and qualitative analysis: what works, what does not, and why.
- Discuss limitations and future work at the end when the venue expects it.
- Put the Appendix after References, on a fresh page if required.

### 5. Figures

- Describe the supplied figures faithfully. Do not contradict the visual evidence.
- Use all figures in `figures_list`.
- Use exact filenames with extensions. Figures live in the `figures/` subdirectory.
- Do not merge multiple figures into one.
- In a two-column format, prefer single-column `figure` unless the figure is very wide.
- Reference every figure in the text.
- All figures appear before the Conclusion, unless placed in the Appendix.
- Do not include "Figure N" in the caption; LaTeX adds it.
- Refine captions only when necessary.

### 6. Style

- Adopt the tone of a top-tier ML conference paper: dense, objective, technical.
- Match the indentation and spacing of `template.tex`.

## Output format

Return the full code for the completed `template.tex`. Previously empty sections are filled; previously filled sections remain mostly untouched. Wrap the code in a ` ```latex ` block.

## Important notes

- Do not change `\usepackage[capitalize]{cleveref}` to `cleverref`.
- Ensure the code compiles: environment names match, `figure*` closes with `\end{figure*}`, no undefined macros.
- If a claim cannot be supported by the log or a verified citation, remove it rather than inventing support.

## Anti-leakage

Write as if you have no prior knowledge of the topic, method, experiments, or results. Use only the provided materials and verified papers. Do not reconstruct an existing publication, author list, or venue.
