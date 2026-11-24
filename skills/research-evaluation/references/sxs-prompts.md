# Side-by-side prompts

Evaluate each paper independently before comparing. Do not infer quality from length or verbosity. Randomize or swap ordering to cancel positional bias.

## Literature review quality

You are an expert AI researcher and reviewer for CVPR, NeurIPS, or ICLR.

Compare the Introduction and Related Work of two papers.

Criteria:

1. **Problem framing and motivation:** Which introduces the problem more clearly and explains why the gap matters?
2. **Coverage of prior work:** Which gives a more complete and relevant overview?
3. **Organization and synthesis:** Which groups and synthesizes prior work rather than listing papers?
4. **Positioning:** Which explains more clearly how its approach differs from existing methods?
5. **Writing quality:** Which is clearer, more concise, and easier to follow?

Return JSON:

```json
{
  "paper_1_analysis": "...",
  "paper_2_analysis": "...",
  "comparison_justification": "...",
  "winner": "paper_1"
}
```

`winner` is exactly `paper_1`, `paper_2`, or `tie`.

## Full paper quality

Compare two manuscripts that describe the same or highly similar research.

Criteria:

1. **Scientific depth and soundness:** rigor of justification, theory, and experimental setup.
2. **Technical execution:** how effectively the idea is implemented and evaluated.
3. **Organization and flow:** clear, coherent order from Abstract to Conclusion.
4. **Clarity and precision:** concise explanation without ambiguity or repetition.
5. **Evidence and presentation:** effective integration of figures, tables, and results; fewer layout defects.
6. **Academic style:** polished, precise, consistent terminology.

Return JSON:

```json
{
  "paper_1_holistic_analysis": "...",
  "paper_2_holistic_analysis": "...",
  "comparison_justification": "...",
  "winner": "tie"
}
```

## Aggregation

Run each pair in both orderings:

- Two candidate wins, or one win and one tie → candidate win.
- Two baseline wins, or one loss and one tie → baseline win.
- One win and one loss, or two ties → tie.

Then aggregate with `scripts/aggregate_sxs.py`.
