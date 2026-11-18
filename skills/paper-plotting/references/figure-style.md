# Figure style

## Matplotlib preamble

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 9,
    "axes.labelsize": 9,
    "axes.titlesize": 10,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linewidth": 0.5,
    "lines.linewidth": 1.5,
    "lines.markersize": 4,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})
```

`pdf.fonttype = 42` embeds TrueType fonts, which avoids Type-3 font warnings in venue PDF checkers.

## Color

Use a colorblind-safe qualitative palette. Example (Okabe–Ito):

```python
PALETTE = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#000000"]
```

Use color plus marker or hatch, so the figure remains readable in grayscale.

## Sizes

| Target | Figure width |
|---|---|
| single column | 3.3 in |
| 1.5 column | 5.0 in |
| full width | 7.0 in |

Height follows the planned aspect ratio. Keep text at 8–10 pt after scaling.

## Saving

```python
fig.savefig("figures/fig_name.pdf", bbox_inches="tight", pad_inches=0.02)
fig.savefig("figures/fig_name.png", dpi=300, bbox_inches="tight", pad_inches=0.02)
```

Always save both: the PDF for LaTeX, the PNG for review.

## Data honesty

- Plot exactly the values in `experimental_log.md`.
- Do not truncate a y-axis to exaggerate a difference unless the truncation is labeled and necessary.
- Do not sort categories to manufacture a trend; sort by a meaningful axis and say so.
- If error bars come from multiple seeds, say "mean ± std over N seeds" in the caption.
- If a baseline is missing for a dataset, leave a gap or omit the series; do not fill it in.

## Diagrams

- Left-to-right for pipelines, top-to-bottom for hierarchies, cycles only for iterative methods.
- One visual encoding per meaning: color for module type, line style for data flow, not both for the same distinction.
- Label arrows when the operation is not obvious (for example "stop-gradient").
- Keep text horizontal. Rotated labels are a readability tax.
- Use the paper's variable names, not internal code names.
