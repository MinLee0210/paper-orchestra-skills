# IEEE conference template

This is a generic IEEE conference scaffold built on the standard `IEEEtran` class
(`\documentclass[conference]{IEEEtran}`). It is not tied to a specific IEEE
conference; always replace the limits below with the target CFP.

- **Layout:** two columns, `IEEEtran` conference mode.
- **Page limit:** commonly 6 pages for the main text, references excluded. Check the CFP.
- **Review:** many IEEE conferences are double-blind; keep the anonymous author block unless the CFP says otherwise.
- **Sections:** Abstract, keywords, Introduction, Related Work, Method, Experiments, Conclusion.
- **Tables:** `booktabs`.
- **Citations:** numeric `\cite{key}` with `IEEEtran` bibliography style.
- **Appendix:** after references, new page, if allowed.
- **Engine:** `pdflatex` + `bibtex`.

The `IEEEtran.cls` file is provided by the TeX distribution (`texlive-publishers`
on Debian/Ubuntu). It is not bundled here.
