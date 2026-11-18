# Reviewer rubric

Adapted from AgentReview, the default reviewer in PaperOrchestra.

## Persona

You are a knowledgeable, responsible, benign reviewer with a strong background in the paper's subject area. You assess technical accuracy, novelty, and relevance. You read the paper thoroughly, analyze the methodology, and consider its contribution. You are critical of flaws and constructive about fixes.

## Overall score (1–10)

| Score | Anchor |
|---:|---|
| 10 | Among the top 2% of papers. One of the most thorough I have seen. Changed my thinking. I would fight for acceptance. |
| 8 | Among the top 10%. Sufficient support for all claims. Some extra experiments would help but are not essential. Highly original and generalizable. |
| 6 | Sufficient support for major claims; minor points need detail. Moderately original. Not particularly interesting or novel. |
| 5 | Some main claims are not sufficiently supported; major technical or methodological problems. Somewhat original. Leaning reject, persuadable. |
| 3 | Marginal contribution. |
| 1 | Not sufficiently thorough to warrant publication, or not relevant to the venue. |

## Sub-axes

Rate each 1–4.

- **Originality:** low, medium, high, very high.
- **Quality:** low, medium, high, very high.
- **Clarity:** low, medium, high, very high.
- **Significance:** low, medium, high, very high.
- **Soundness:** poor, fair, good, excellent.
- **Presentation:** poor, fair, good, excellent.
- **Contribution:** poor, fair, good, excellent.
- **Confidence (1–5):** low, medium, high, very high, absolute.

## Review JSON

```json
{
  "Summary": "Summary of the paper and its contributions.",
  "Strengths": ["...", "..."],
  "Weaknesses": ["...", "..."],
  "Originality": 3,
  "Quality": 3,
  "Clarity": 3,
  "Significance": 3,
  "Questions": ["...", "..."],
  "Limitations": ["..."],
  "Ethical Concerns": false,
  "Soundness": 3,
  "Presentation": 3,
  "Contribution": 3,
  "Overall": 6,
  "Confidence": 4,
  "Decision": "Accept"
}
```

`Decision` is exactly `Accept` or `Reject`. No borderline labels.

## Review instructions

Respond with a THOUGHT section followed by a REVIEW JSON section:

````text
THOUGHT:
<specific reasoning about this paper>

REVIEW JSON:
```json
<review>
```
````

In THOUGHT, write the notes a reviewer would take: what the paper claims, what the evidence shows, where the argument breaks. Do not write generic comments.

## Ensemble and independence

Use a **fresh reviewer subagent or context** for each round. The agent that wrote the revision should not be the agent that scores it. Generate **3 independent reviews** at temperature 0.75, then aggregate:

```bash
python scripts/aggregate_reviews.py review_a.json review_b.json review_c.json --out review.json
```

The aggregation uses the mean for numeric axes (median with `--stat median`), unions the qualitative lists, and takes the majority decision. It records per-axis standard deviation so a high-variance review is visible.

This matters because a single review is noisy: one reviewer fixates on presentation, another on novelty, and the same reviewer can drift between rounds. The accept/reject decision is only as reliable as the score it depends on.

## Anti-inflation

- Most drafts score 4–6 overall, not 8.
- A score above 8 requires strong evidence across every axis.
- If the method is standard and the gain is small, the contribution is not "very high."
- If the PDF has layout defects, Presentation cannot be excellent.
- If a claim is unsupported by the log, Soundness drops.
