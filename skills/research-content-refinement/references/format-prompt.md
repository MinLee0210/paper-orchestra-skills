# Formatting review prompt

You are reviewing rendered page images of a research paper for formatting and layout defects. Follow the supplied `guidelines.md`. Do not invent rules that the guidelines do not state.

## What to inspect

- Every figure and table: does it overflow into the gutter or margin? Is it legible? Is it placed near its first reference and before the conclusion?
- Page limit: does the main text exceed the limit, counting up to the start of References?
- Blank pages or pages containing only a float.
- Orphaned section headings at the bottom of a column.
- Overlapping text, clipped labels, unreadable tables.
- Fonts, margins, column widths, and caption placement.

Do not flag a figure or table that simply fills the column width. Only report a clear overflow or illegibility.

## Output JSON

```json
{
  "figure_and_tables": {
    "Figure 1": {
      "detected_issue": "The figure spills into the right margin.",
      "suggested_fix": "Use width=\\linewidth in \\includegraphics."
    },
    "Table 1": {
      "detected_issue": "None",
      "suggested_fix": "None"
    }
  },
  "other_issues": [
    {
      "page": 4,
      "element": "Section 4.2, first paragraph",
      "detected_issue": "Section heading is stranded at the bottom of the column.",
      "suggested_fix": "Add a page or column break before the heading."
    }
  ]
}
```

Report every figure and table, even when the issue is "None". Then list other text and layout issues.

## Revision prompt

You are a LaTeX formatting expert. Fix the issues in the feedback.

Critical: you may change only formatting, layout, and spacing. Do not change content, claims, data, or citations.

Rules:

- Page limit: condense by removing non-informational adjectives, merging short paragraphs, and tightening spacing around floats. Never remove contributions, main results, the abstract, or the conclusion.
- Figures: prefer single-column `figure`. Use `figure*` for wide figures. Keep aspect ratio; never set both width and height unless required.
- Tables: try `\small` or `\footnotesize`, abbreviate headers, then `tabularx` with `X` columns.
- Tables and figures appear before the conclusion unless placed in the appendix.
- Fix citations to match `citation_map.json`; remove keys that do not resolve.
- Fix orphans and widows with `\clearpage` or spacing.
- Do not add packages unless necessary.
- Do not change `cleveref` to `cleverref`.
- Keep indentation and spacing consistent with the existing source.

Output the full revised LaTeX document in a ` ```latex ` block.
