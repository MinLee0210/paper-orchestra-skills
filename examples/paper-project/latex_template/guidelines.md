# Neutral example template

This is not a real venue template. It exists so the example project validates and compiles without bundling a conference style.

- **Layout:** single column, 1 inch margins.
- **Page limit:** 8 pages excluding references.
- **Review:** double-blind. Remove author names and affiliations.
- **Sections:** Abstract, Introduction, Related Work, Method, Experiments, Conclusion.
- **Tables:** `booktabs`.
- **Citations:** `\cite{key}` with `plain` BibTeX.
- **Appendix:** after references, new page.

For a real submission, replace this directory with a venue bundle:

```bash
python skills/paper-template/scripts/init_template.py --venue cvpr2025 --out path/to/latex_template --force
```
