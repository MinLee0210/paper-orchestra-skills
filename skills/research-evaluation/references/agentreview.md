# AgentReview rubric

This skill scores overall paper quality with the **same rubric as the refinement stage**. The persona, the 1–10 anchors, the sub-axes, the JSON schema, and the anti-inflation caps are defined once:

- [`research-content-refinement/references/reviewer-rubric.md`](../../research-content-refinement/references/reviewer-rubric.md) — the rubric. Do not restate or re-derive it here; score with those anchors.

What this file adds is only what differs in evaluation: how to turn several reviews into a reported number.

## Ensemble protocol

1. Generate three independent reviews at temperature 0.75, preferably with independent reviewer contexts.
2. Aggregate them:

   ```bash
   python <research-content-refinement>/scripts/aggregate_reviews.py review_a.json review_b.json review_c.json --out review.json
   ```

3. Use the aggregated numeric axes (`--stat mean` by default) and the majority decision.
4. Report the mean Overall and the fraction of `Accept` decisions as the simulated acceptance rate. Inspect per-axis standard deviation; high variance means the score is unstable.

## Reporting

- Always report the judge model, the rubric version, and the temperature next to the score.
- Report the citation count next to any citation metric; precision is trivially high on a short bibliography.
- A simulated acceptance rate is a ranking device, not peer review. Its calibration against real decisions is unknown unless you have measured it on your own accepted and rejected papers.

## Anti-inflation

- Most drafts are 4–6, not 8.
- Apply the Presentation and Soundness caps from the refinement rubric.
- A standard method with a small gain is not "very high" originality or contribution.

## Known failure mode of this gate

The refinement loop decides on the *delta* in Overall, not on the Decision. A paper that three reviewers mark `Reject` can still pass if the revision nudges the mean up. When you use this rubric as a submit/don't-submit gate, require an absolute threshold as well: mean Overall at or above 7 **and** a majority of `Accept` decisions.
