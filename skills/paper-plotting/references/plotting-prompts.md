# Plotting prompts

Adapted from PaperOrchestra's PaperBanana module. Use only the parts that fit the available tools.

## Reference retrieval

If a local library of published figures is available, select the 3–5 most relevant examples for the target.

Match on two axes:

1. **Data characteristics** for plots (categorical, time series, multi-series) or **research topic** for diagrams.
2. **Visual intent** (bar chart, line chart, heatmap, framework diagram, module diagram).

Prefer the same visual intent over the same topic: structure transfers better than subject matter. Return only the IDs of the selected examples. Use them as style references, never as content sources.

## Planner (plot)

I am generating a statistical plot for a top-tier AI paper. Given the raw data and the visual intent, produce a detailed description of the plot to generate.

Your description must include all raw data points to be plotted. For content, explain the precise mapping of variables to visual channels (x, y, hue) and enumerate every data point or series. For presentation, specify aesthetics: hex colors, font sizes, line widths, marker sizes, legend placement, and grid style.

Do not invent values. If a value is missing from the raw data, say so explicitly.

## Planner (diagram)

I am generating an illustrative diagram from the method description and the figure caption. Produce a detailed description of the diagram.

Describe every element, its label, and its connections. Specify layout (left-to-right, top-to-bottom, cyclic), background (white or very light pastel), colors, line weights, icon style, and which parts are trainable versus frozen when that distinction matters.

Use only components that appear in the method. Do not add plausible-sounding modules that are not described.

## Stylist

You are a lead visual designer for top-tier AI conferences.

Given a preliminary figure description, refine only the aesthetics. Preserve the semantic content, the data, and the logic exactly. Enrich colors, typography, spacing, and layout. If the description is already clean and readable, leave it alone.

Output only the final polished description.

## Critic (plot)

Review the rendered plot against the raw data and the visual intent.

Check:

1. Data fidelity: every value matches the raw data; no omitted or invented points.
2. Labels: axis labels, units, legend entries, and annotations are correct and readable.
3. Overlap: no text hidden by bars, gridlines, hatching, or other elements.
4. Chart type: the chosen form actually communicates the intended comparison.
5. Caption exclusion: the image does not contain "Figure N" or the caption text.

Return JSON:

```json
{
  "critic_suggestions": "Specific issues, or 'No changes needed.'",
  "revised_description": "A complete revised description, or 'No changes needed.'"
}
```

## Critic (diagram)

Review the rendered diagram against the method description and caption.

Check:

1. Fidelity: every component and connection is described in the method; nothing critical is missing.
2. Text quality: labels are spelled correctly and use the paper's terminology.
3. Flow: the reading order is obvious; arrows and groupings are unambiguous.
4. Hallucination: no invented datasets, modules, losses, or results.
5. Caption exclusion: no "Figure N" and no caption text inside the image.

Return the same JSON shape as the plot critic.

## Caption

Write the final caption from the figure description and the surrounding section.

Requirements:

- One to three sentences, plain text, no markdown.
- No "Figure N:" or "Caption N:" prefix.
- State what is shown and the single takeaway.
- No claim that the figure does not support.
- Mention error bars or shading if present, and say what they represent.

Return the caption only.

## Self-critique checklist when no vision model is available

Open the PNG and answer:

- Can I read every label at 100% zoom?
- Does the visual comparison match the numbers in the log?
- Is the most important result the most visually prominent thing?
- Is there any element that exists only because it looked decorative?
- Would the caption still be true if I removed every adjective?
