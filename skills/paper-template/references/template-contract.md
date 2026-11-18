# Template contract

## Required files

| File | Purpose | Required |
|---|---|---|
| `template.tex` | compilable skeleton | yes |
| `guidelines.md` | venue rules in plain language | yes |
| `references.bib` | starter bibliography | yes (may be empty) |
| `*.sty` | venue style | if referenced by the template |
| `*.bst` | bibliography style | if using BibTeX |
| `preamble.tex` | shared macros | optional |

## Section placeholders

The literature stage needs to find Introduction and Related Work. The section-writing stage needs to find the remaining sections. Use one of these forms consistently:

```latex
\section{Introduction}
% TODO: introduction

\section{Related Work}
% TODO: related work

\section{Method}
% TODO: method

\section{Experiments}
% TODO: experiments

\section{Conclusion}
% TODO: conclusion
```

Or the empty-environment form:

```latex
\section{Introduction}
\label{sec:intro}

\section{Related Work}
\label{sec:related}
```

Empty is fine. The agents preserve whatever text is already present and fill what is missing. They are instructed not to rewrite filled sections during section writing.

## Guidelines checklist

`guidelines.md` should answer:

- What is the page limit for the main text, and does it exclude references?
- Is the review double-blind? What must be removed or replaced?
- Which sections are mandatory (for example, Limitations, Ethics, Reproducibility)?
- Which citation commands are expected (`\cite`, `\citep`, `\citet`)?
- Are appendices allowed after references, and do they count toward the limit?
- Are there font, margin, column, or figure requirements that generated LaTeX commonly violates?
- Which engine and bibliography tool should be used (`pdflatex` + `bibtex`, `latexmk`, `xelatex` + `biber`)?

## Pipeline checks

1. `template.tex` contains `\documentclass`, `\begin{document}`, and `\end{document}`.
2. The template compiles before any generated content is added.
3. Every `\usepackage{...}` resolves locally or in the TeX distribution.
4. `references.bib` exists so the literature stage can replace it.
5. Section names match the outline, so the section writer can map outline nodes to LaTeX sections.

## Custom venues

To add a venue:

1. Create `assets/templates/<key>/`.
2. Copy the official style files and the official example `.tex`.
3. Reduce the example to a skeleton with empty section placeholders.
4. Write `guidelines.md` from the official author kit. Quote limits and anonymity rules exactly; do not paraphrase numbers.
5. Add the venue to the table in `SKILL.md` and to the `--venue` choices in `scripts/init_template.py`.

Do not strip the venue's copyright or license headers from style files.
