# Literature review rubric (0–100)

Adapted from PaperOrchestra's literature-review autorater. Score conservatively.

## Baseline

The prompt includes the average citation count for accepted papers in the venue. Use it as the reference for "typical" coverage. A review with half the reference count is narrow unless the field is genuinely small.

## Scope

Evaluate only the Introduction and Related Work (or equivalents). Ignore method and results except to check whether the review sets up the paper's claims correctly.

## Process

1. Identify the paper title.
2. Locate Introduction and Related Work.
3. Identify the stated problem, claimed contributions, and relevant subfields.
4. Estimate unique citations, citation density, breadth, and volume relative to the reference average.
5. Score each axis from explicit text only. Do not reward expected but missing knowledge.
6. Apply caps and penalties.
7. Output JSON only.

## Axes

### 1. Coverage and completeness

- Breadth across major threads.
- Foundational and recent work.
- Obvious omissions.
- Volume relative to the reference average.

Count anchors:

- `< 50%` of reference: cap 55 unless the field is very small.
- `50–80%`: minimal acceptable coverage.
- `80–120%`: solid breadth if integrated well.
- `> 120%`: strong coverage if relevance holds.

### 2. Relevance and focus

- Alignment with the problem.
- Few tangents, no padding.
- Clear scoping and prioritization.

### 3. Critical analysis and synthesis

- Thematic grouping and comparison.
- Tradeoffs, limitations, open gaps.
- Synthesis rather than sequential summaries.

Cap: 60 if the review is mostly descriptive.

### 4. Positioning and novelty

- Literature-grounded gap.
- Explicit differentiation from the closest work.
- Why the gap matters.

Cap: 60 if novelty is asserted without explicit comparison.

### 5. Organization and writing

- Logical structure and signposting.
- Precise academic language.
- Appropriate subsectioning and definitions.

### 6. Citation practices and rigor

- Claims are supported by citations.
- Credible and consistent sources.
- Density relative to length.
- Balance of foundational and recent work.

Caps: 55 if citation count is far below the reference; 65 if count is high but integration is weak.

## Anti-inflation

- Default overall: 45–70.
- `> 85` requires strong evidence on every axis.
- `> 90` is rare and requires survey-level mastery.
- If any axis is `< 50`, overall rarely exceeds 75.
- High citation count does not imply high quality; relevance and synthesis must justify it.

## Penalties

- Overclaiming novelty: −5 to −15.
- Missing key recent work: −5 to −15.
- Mostly descriptive: −5 to −10.
- Generic gap statement: −5 to −10.
- Citation dumping or inconsistency: −5 to −10.

## Weighting

Coverage 20%, relevance 15%, critical analysis 25%, positioning 25%, organization 10%, citation rigor 5%. Apply penalties after weighting.

## Output JSON

```json
{
  "paper_title": "...",
  "citation_statistics": {
    "estimated_unique_citations": 42,
    "citation_density_assessment": "appropriate",
    "breadth_across_subareas": "broad",
    "comparison_to_baseline": "72% of venue average",
    "notes": "..."
  },
  "axis_scores": {
    "coverage_and_completeness": {"score": 70, "justification": "..."},
    "relevance_and_focus": {"score": 74, "justification": "..."},
    "critical_analysis_and_synthesis": {"score": 68, "justification": "..."},
    "positioning_and_novelty": {"score": 72, "justification": "..."},
    "organization_and_writing": {"score": 80, "justification": "..."},
    "citation_practices_and_rigor": {"score": 69, "justification": "..."}
  },
  "penalties": [{"reason": "...", "points_deducted": 5}],
  "summary": {
    "strengths": ["..."],
    "weaknesses": ["..."],
    "top_improvements": ["..."]
  },
  "overall_score": 69
}
```

Each justification is 2–5 sentences, evidence-based. Quote at most 25 words from the paper. If evidence is missing, write "Not evidenced in the text."
