# AgentReview rubric

Use this when you need an overall quality score rather than a literature-only score. It is the same rubric used by the refinement stage; keep the two consistent.

## Persona

A knowledgeable, responsible, benign reviewer with a PhD in the paper's area. Reads thoroughly, checks methodology, and gives constructive but critical feedback.

## Overall (1–10)

| Score | Anchor |
|---:|---|
| 10 | Top 2%. Changed my thinking. I would fight for acceptance. |
| 8 | Top 10%. Claims well supported. Some extra experiments would help but are not essential. |
| 6 | Major claims supported; minor gaps. Moderately original. Not a big loss if rejected. |
| 5 | Some main claims unsupported; major technical problems. Leaning reject, persuadable. |
| 3 | Marginal contribution. |
| 1 | Not thorough enough to publish, or irrelevant. |

## Axes

- Originality, Quality, Clarity, Significance (1–4).
- Soundness, Presentation, Contribution (1–4).
- Confidence (1–5).
- Decision: `Accept` or `Reject`.

## Output

```json
{
  "Summary": "...",
  "Strengths": ["..."],
  "Weaknesses": ["..."],
  "Originality": 3,
  "Quality": 3,
  "Clarity": 3,
  "Significance": 3,
  "Questions": ["..."],
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

## Ensemble protocol

1. Generate three independent reviews at temperature 0.75.
2. Generate a meta-review with an area-chair persona that combines them into one review in the same format.
3. For numeric axes, use the rounded mean of the three reviews when available; otherwise use the meta-review.
4. Report the mean Overall and the fraction of `Accept` decisions as the simulated acceptance rate.

## Anti-inflation

- Most drafts are 4–6, not 8.
- Layout defects cap Presentation at 2.
- Unsupported claims cap Soundness at 2.
- A standard method with a small gain is not "very high" originality or contribution.
