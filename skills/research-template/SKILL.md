---
name: research-template
description: Select, scaffold, and adapt a LaTeX template and its writing guidelines for automated paper generation. Use when the user names a venue or format (CVPR, ICLR, IEEE conference, arXiv preprint, OSDI, SOSP, ASPLOS, NSDI, two-column, single-column), needs template.tex plus guidelines.md, wants to add a custom template, or needs to check page limits, fonts, and required packages before drafting.
license: Apache-2.0
---

# Conference templates

The writing agents edit a real LaTeX project. They need three things from a template: a compilable skeleton, the venue's formatting rules in plain language, and a stable contract for where sections go. This skill supplies all three.

## Bundled templates

| Key | Venue | Layout | Main-text limit |
|---|---|---|---|
| `cvpr2025` | CVPR 2025 | two-column | 8 pages excluding references |
| `iclr2025` | ICLR 2025 | single-column | 10 pages excluding references |
| `ieeeconf` | IEEE conference (generic) | two-column | commonly 6 pages; check the CFP |
| `arxiv` | arXiv preprint (neutral) | single-column | no hard limit |
| `osdi2026` | OSDI 2026 | two-column | 12 pages excluding references |
| `sosp2026` | SOSP 2026 | two-column | 12 pages of technical content |
| `asplos2027` | ASPLOS 2027 | two-column | 11 pages excluding references |
| `nsdi2027` | NSDI 2027 | two-column | 12 pages excluding references |

Each bundle contains:

```text
<venue>/
├── template.tex        # skeleton with empty section placeholders
├── guidelines.md       # venue rules, in markdown
├── references.bib      # starter bibliography
├── preamble.tex        # optional shared macros (CVPR)
└── *.sty / *.bst       # venue style files, when bundled
```

The four systems bundles ship as a full sample paper rather than a bare skeleton, because systems authors usually start from the venue's worked example. Their `guidelines.md` is quoted from the template's own header comment, so the page limit is never paraphrased. Section placeholders work the same way once the bodies are cleared; the section writer preserves any text it finds, so clear the sample sections before generation.

List them:

```bash
ls skills/research-template/assets/templates
```

## Scaffold a project template

```bash
python scripts/init_template.py --venue cvpr2025 --out /path/to/project/latex_template
python scripts/init_template.py --venue iclr2025 --out /path/to/project/latex_template
python scripts/init_template.py --venue ieeeconf --out /path/to/project/latex_template
python scripts/init_template.py --venue arxiv --out /path/to/project/latex_template
python scripts/init_template.py --venue osdi2026 --out /path/to/project/latex_template
```

The script copies every file, refuses to overwrite a non-empty directory unless `--force` is given, and prints the required file check.

## Add a custom template

A custom template is valid when it satisfies this contract:

1. `template.tex` compiles on its own with `pdflatex` (or the engine the venue requires).
2. `guidelines.md` states the page limit, anonymity rules, required sections, citation style, and any mandatory statements.
3. Every package the template references is present in the directory or in a standard TeX distribution.
4. The document has clear, empty section placeholders for the sections the writer must fill: Introduction, Related Work, Method, Experiments, Conclusion. The literature stage fills Introduction and Related Work; the section-writing stage fills the rest.
5. `references.bib` exists, even if empty, because the bibliography step rewrites it.

Read `references/template-contract.md` for the section-placeholder format and the checks the pipeline performs.

## What to tell the user before drafting

- **Page limit:** the limit that applies to the main text, excluding references.
- **Anonymity:** whether author names and acknowledgements must be removed.
- **Figures:** two-column templates usually want single-column figures; wide figures use `figure*`.
- **Citations:** `natbib` (`\citep`, `\citet`) versus numeric `\cite`.
- **Appendices:** whether they follow the references and whether they count toward the limit.

## Template pitfalls

- Do not rename style files. `\usepackage{cvpr}` and `\bibliographystyle{ieeenat_fullname}` depend on exact names.
- Do not replace `cleveref` with `cleverref`; there is no `cleverref.sty`. This typo appears repeatedly in generated LaTeX.
- Do not add packages that the venue forbids. When in doubt, use what the skeleton already loads.
- Keep the preamble stable across revisions. Formatting fixes should change layout, not packages; the one allowed addition is `tabularx` (see `research-content-refinement`).
- If the venue requires a specific engine (for example `xelatex` for font reasons), record it in `guidelines.md` so the compile step uses it.

## Validation

```bash
python scripts/init_template.py --venue cvpr2025 --out /tmp/check_template --force
cd /tmp/check_template
pdflatex -interaction=nonstopmode template.tex
```

A template that does not compile before generation will not compile after generation. Fix it first.

## Files

- `assets/templates/cvpr2025/`, `assets/templates/iclr2025/` — bundled venues with style files.
- `assets/templates/ieeeconf/`, `assets/templates/arxiv/` — generic IEEE conference and neutral preprint scaffolds.
- `assets/templates/osdi2026/`, `sosp2026/`, `asplos2027/`, `nsdi2027/` — systems venues. Structure guidance for these lives in `research-systems-paper-writing`.
- `scripts/init_template.py` — the single scaffolder for every bundled venue; always produces the `template.tex` + `guidelines.md` + `references.bib` contract.
- `references/template-contract.md` — exact placeholder and file contract.
