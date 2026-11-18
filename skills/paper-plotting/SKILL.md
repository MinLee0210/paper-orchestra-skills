---
name: paper-plotting
description: Generate publication-quality figures for a research paper from raw materials: statistical plots, conceptual diagrams, captions, and a critic-driven revision loop. Use when the user asks for paper figures, plots, charts, architecture diagrams, teaser figures, or visual summaries, when plotting_plan exists in outline.json, or when a draft is missing figures. Do not use for general graphic design or slide decks.
license: Apache-2.0
---

# Plotting agent

Figures carry the argument. A paper with generic plots and a hallucinated architecture diagram is worse than a paper with two honest figures. This skill turns the outline's `plotting_plan` into figures whose content is traceable to `idea.md` and `experimental_log.md`.

## Two kinds of figures

| Type | What it is | Preferred implementation |
|---|---|---|
| `plot` | data visualization: bars, lines, scatter, heatmap, radar, Pareto | Python + matplotlib, data copied from the log |
| `diagram` | conceptual illustration: pipeline, architecture, module, data flow | vector drawing (TikZ, SVG, or matplotlib patches); an image model only when no vector route exists |

For a `plot`, code is mandatory. Never draw data by hand and never let an image model invent values.

For a `diagram`, fidelity to the method matters more than polish. Label every block with the terminology from `idea.md`. Do not add components that are not in the method.

## Process per figure

1. **Load the plan entry** from `outline.json` (`figure_id`, `title`, `plot_type`, `data_source`, `objective`, `aspect_ratio`).
2. **Extract only the needed data.** For a plot, copy the exact values from `experimental_log.md` into a small data file or into the plotting script. If a value is missing, stop and report it; do not interpolate.
3. **Plan the visual.** Decide the chart type, the x/y encoding, the grouping, the ordering, and the comparison the reader should see. Read `references/figure-style.md` for the default style.
4. **Render.** Write a script that saves a vector PDF (`figures/<figure_id>.pdf`) and a PNG preview at 300 dpi (`figures/<figure_id>.png`). The PDF is for LaTeX; the PNG is for visual review.
5. **Critique and revise.** Inspect the PNG. Check data fidelity, labels, overlap, legend, and whether the objective is actually visible. Revise up to 3 rounds. When a vision-capable model is available, use it as the critic; otherwise use the checklist in `references/plotting-prompts.md`.
6. **Caption.** Write a plain-text caption with no "Figure N" prefix and no markdown. State what is shown and the one takeaway. Do not claim a trend the figure does not show.
7. **Record.** Append to `plotting_results.json` and `figures/info.json`.

## Output contract

`figures/info.json`:

```json
[
  {"name": "fig_main_results.pdf", "caption": "Comparison on both datasets. The method improves ..."},
  {"name": "fig_architecture.pdf", "caption": "Overview of the proposed pipeline."}
]
```

`plotting_results.json`:

```json
[
  {
    "figure_id": "fig_main_results",
    "title": "Main results",
    "task_name": "plot",
    "aspect_ratio": "16:9",
    "caption": "...",
    "image_path": "figures/fig_main_results.pdf",
    "preview_path": "figures/fig_main_results.png",
    "data_source": "experimental_log.md",
    "critic_rounds": 2,
    "notes": "Two baselines omitted because the log does not report them."
  }
]
```

Validate:

```bash
python scripts/validate_figures.py /path/to/project
```

The script checks that every `info.json` entry resolves, that files are non-empty, and that previews exist for visual review.

## Reference examples

PaperOrchestra retrieves a few similar figures before planning. If the user has a local library of published figures, select the top 3–5 with the same visual intent (bar chart, multi-series line, pipeline diagram) and use them only as style references. Never copy their content, data, or labels. If no library exists, skip retrieval; the style guide is enough.

## Style defaults

- White background, no chartjunk, no 3D effects, no gradients.
- Font sizes: 8–10 pt at final print size. One figure should read at column width.
- Colorblind-safe palette; distinct markers as well as colors.
- Direct labels over legends when there are fewer than five series.
- Error bars when the log reports variance or multiple seeds. State the meaning in the caption.
- Axis labels include units. No title inside the image if the caption already names it.
- For two-column venues, design for a single column unless the figure is explicitly wide.

## Aspect ratios

Use the ratio requested in the plan. Map it to a matplotlib figure size with `figsize=(w, w * h_ratio)`; keep the rendered PDF tight with `bbox_inches="tight"`.

## Failure handling

- **Missing data:** skip the figure, record `"status": "skipped"` with a reason, and tell the user. Never synthesize a value.
- **Plot code fails:** simplify the chart type rather than debugging for many rounds. A clean bar chart beats a broken radar chart.
- **Diagram is too complex:** split it into two figures or move detail into the caption. A diagram with 20 unreadable boxes communicates less than five clear ones.
- **No image generation tool:** produce the diagram as TikZ or SVG. For LaTeX inclusion, export to PDF first.

## Files

- `references/plotting-prompts.md` — planner, stylist, critic, and caption prompts.
- `references/figure-style.md` — concrete style rules and a matplotlib preamble.
- `scripts/validate_figures.py` — verify the figure manifest and files.
