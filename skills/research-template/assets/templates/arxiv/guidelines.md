# arXiv preprint template

A neutral one-column preprint scaffold. It is not an official arXiv style; arXiv
accepts the PDF that LaTeX produces, so the layout is a convention rather than a
requirement.

- **Layout:** single column, 1 inch margins, 11 pt.
- **Page limit:** none. Keep the main text readable; move long derivations to the appendix.
- **Review:** not anonymous by requirement, but this scaffold uses Anonymous Authors so generation does not invent identities.
- **Sections:** Abstract, Introduction, Related Work, Method, Experiments, Discussion, Conclusion, Appendix.
- **Tables:** `booktabs`.
- **Citations:** `\cite{key}` with `plain` BibTeX. Use `natbib` if you prefer author-year.
- **Engine:** `pdflatex` + `bibtex`.

Before posting, replace the anonymous block with the real author list and check
the license you want to attach on arXiv.
