---
name: research-ideation
description: "Structured ideation for research: a diverge-converge-refine workflow plus 13 cognitive-science lenses (problem reframing, hard/soft/hidden constraints, structural analogy and bisociation, negation, abstraction laddering, tension synthesis, adjacent possible, composition, stakeholder rotation, boundary probing, simplicity). Use when exploring a problem space, choosing or pivoting a research direction, judging whether an idea is worth pursuing, preparing a brainstorming session, or when candidate directions feel too conventional - including fixation, tunnel vision, incrementalism, and analysis paralysis. Not for literature surveys (use research-literature-review), experiment design (research-experimental-design), sample sizing (research-statistical-power), or running experiments (research-autoresearch)."
version: 2.0.0
author: Orchestra Research
license: MIT
tags: [Research Ideation, Brainstorming, Creative Thinking, Problem Discovery, Analogical Reasoning, Research Strategy]
dependencies: []
---

# Research ideation

Two jobs, one skill:

- **A workflow** to take a blank page to 3–5 ranked, defensible research directions: diverge → converge → refine.
- **Thirteen lenses** from creativity research to generate candidates the workflow alone will not reach.

This skill merges the earlier `research-brainstorming` and `research-creative-thinking` skills. Four lenses they both described — the abstraction ladder, analogy transfer, tension hunting, and constraint manipulation — now appear once here. Full treatments live in [references/frameworks.md](references/frameworks.md).

## When to use

- Starting a new direction and you need structured exploration, not inspiration
- Stuck on a project: fixation, tunnel vision, or every idea is "+2% on a benchmark"
- Deciding whether a half-formed idea is worth two weeks of compute
- Preparing a session with collaborators
- Moving fields and looking for a high-leverage entry point

**Not for:** surveying a field's literature (use `research-literature-review`), designing or sizing an experiment once you have a question (use `research-experimental-design`, `research-statistical-power`), or executing an experiment loop (use `research-autoresearch`).

## Workflow

### Phase 1 — Diverge

Produce 10–20 candidates with no filtering. Filters this early kill the strange ideas, which are the ones that recombine later.

1. **Tensions** (L7): list 5 trade-offs the field treats as unavoidable.
2. **What changed** (L8): list 3 shifts in the last 18 months — compute, data, tooling, regulation, a public failure.
3. **Boundary probing** (L11): pick 2 popular methods; find where they break.
4. **Analogy** (L4): import 1 mechanism from an adjacent field.
5. **Compose / decompose** (L9): combine 2 techniques, or split 1 monolithic method apart.
6. **Ladder** (L6): for each candidate, write the more general, more specific, and adjacent-domain version.

Write every candidate down, including the ones you dislike. The discard pile is where phase 3 finds its best material.

### Phase 2 — Converge

Narrow to 3–5. Apply the filters in order; the first two kill most candidates.

| Filter | Question | Kill criterion |
|---|---|---|
| Two-sentence test (L13) | Can I state problem and insight in two sentences? | No → not yet an idea |
| Problem-first check (L1) | Who suffers from this today, and how much? | No one → drop |
| Simplicity (L12) | Would a well-tuned simple baseline match it? | Yes → the idea is the baseline |
| Stakeholder (L10) | Who benefits, who objects? | No beneficiary → drop |
| Feasibility | Can I run the decisive experiment with what I have? | No → park with a written reason |

### Phase 3 — Refine the winner

1. Two-sentence pitch (L13).
2. Name the tension it resolves, or the constraint it drops (L3, L7).
3. Fix the abstraction level: general principle, or specific instantiation (L6).
4. Three concrete experiments that could falsify it.
5. The strongest objection, and the answer.
6. A two-week pilot that would give signal on feasibility.

Done when a reader who knows nothing about your project can restate the idea and its falsification test.

## The thirteen lenses

Each is one move. Full workflows, examples, and validation checklists are in [references/frameworks.md](references/frameworks.md).

### Frame

**L1 — Problem-first vs solution-first.** Classify the idea. Problem-first needs a named beneficiary and a cost of not solving it; solution-first needs at least two problems the new capability unlocks. *Self-check: can I name the person who needs this?*

**L2 — Reformulate the problem.** Change the objective, the formalism, the granularity, the agent, or the timescale. "Make the algorithm faster" → "eliminate the computation". *Self-check: is the difficulty in the problem, or in how I stated it?*

**L3 — Constraint analysis (Boden).** List 5–10 constraints; mark each hard (physics), soft (convention), or hidden (never stated). Relax, tighten, or replace the soft and hidden ones. *Self-check: which constraint have I never seen questioned?*

### Generate

**L4 — Structural analogy and bisociation.** Describe the problem in domain-neutral, causal language; find a distant field with the same relational structure; map the mechanism, not the vocabulary. Build a cross-product matrix when you want volume. *Self-check: does the mapping predict something I did not already know?*

**L5 — Negation and inversion (TRIZ).** List 5 assumptions "everyone knows"; negate each and ask what system you would build. *Self-check: has this negation been tried, and have the conditions changed since?*

**L6 — Abstraction ladder.** Generalize (what is this a special case of?), specialize (what happens under an extreme constraint?), analogize (where else does this pattern appear?). *Self-check: am I adding a method when the contribution is actually the general principle?*

**L7 — Tension synthesis (Janusian).** Take a pair the field treats as a trade-off and refuse to choose a side. Ask whether the trade-off is fundamental or an artifact of the current formalization. *Self-check: is my resolution a synthesis, or a compromise that splits the difference?*

**L8 — What changed / adjacent possible.** List what became possible in the last 6–18 months and what that unlocks. Too early and the prerequisite is missing; too old and someone did it. *Self-check: could this have been done three years ago? Then check the literature harder.*

**L9 — Compose and decompose.** Combine two methods that solve complementary subproblems, or take a monolith apart to find which component is load-bearing. *Self-check: is the gain emergent, or just the sum of parts?*

**L10 — Stakeholder rotation.** Read the system as end user, developer, theorist, adversary, ethicist, regulator, and operator. The unaddressed concern with the widest impact is a research question. *Self-check: whose problem am I actually solving?*

### Stress-test

**L11 — Boundary probing.** Systematically violate the implicit assumptions of a strong method: distribution, scale, adversary, composition, time. A failure you can explain is a contribution. *Self-check: can I say why it breaks, not just that it does?*

**L12 — Simplicity test.** Strip the SOTA method to its one key idea, build it carefully at the same tuning effort, and compare. A small gap means the simplicity is the contribution; a large gap tells you what the complexity buys. *Self-check: was the simple baseline ever tuned as hard as the complex one?*

### State

**L13 — Two-sentence test.** "[Domain] struggles with [problem], which matters because [consequence]. We [approach] by [mechanism], which works because [reason]." *Self-check: would a skeptic's first objection be answerable from these two sentences?*

## Which lens to reach for

| Situation | Start with |
|---|---|
| No idea what area to work in | L7 tension synthesis → L8 what changed |
| Vague area, no specific question | L6 ladder → L11 boundary probing |
| Idea exists, unsure it is good | L13 two-sentence test → L12 simplicity |
| Good idea, need a fresh angle | L4 analogy → L10 stakeholder rotation |
| Want to combine existing work | L9 compose/decompose |
| New technique looking for an application | L1 problem-first → L10 stakeholder rotation |
| Want to challenge conventional wisdom | L3 constraints → L5 negation |
| Results exist but the story is missing | L7 tension synthesis → L6 ladder |

## Pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| Novelty without impact | "No one has done X" — and no one needs X | L1 |
| Incremental by default | Every idea is +2% on a benchmark | L6, L12 |
| Complexity worship | 8 components, each helping marginally | L12 |
| Echo chamber | All candidates come from the same 10 papers | L4 |
| Stale assumptions | "Tried in 2019, didn't work" | L8 |
| Single perspective | Only the ML engineer's view considered | L10 |
| Premature convergence | Committed to the first idea | Rerun phase 1 with a different lens |
| Fixation | Cannot stop thinking about it one way | L2 |
| Self-censoring | Dismissing ideas as "too weird" before exploring | L5 |
| Analysis paralysis | Too many options, no commitment | L8 feasibility filter |

## Running it with an agent

1. Establish the starting point: new area, stuck project, or idea under evaluation.
2. Pick 2–3 lenses from the table above — not all thirteen.
3. Walk each lens with the researcher supplying domain content. The agent supplies structure, not domain knowledge.
4. Keep a running candidate list, including rejects.
5. Converge with the phase-2 filters; refine the winner into a pitch, falsification tests, and a pilot.
6. Push for specificity: "improve efficiency" is not a candidate. Ask "why?" three times before accepting a motivation.
7. The researcher decides; the agent keeps the process honest.

## Files

- [references/frameworks.md](references/frameworks.md) — full workflows, examples, and validation checklists for all 13 lenses; the deep-session protocol that combines them.

## Attribution

Merges two MIT-licensed skills from [Orchestra-Research/AI-Research-SKILLs](https://github.com/Orchestra-Research/AI-Research-SKILLs) (`21-research-ideation/brainstorming-research-ideas` and `21-research-ideation/creative-thinking-for-research`, commit `773a52944ba4`), Copyright (c) 2025 Claude AI Research Skills Contributors. Changes: consolidated into one skill, four duplicated frameworks merged, numbering unified, cross-references retargeted. See `NOTICE` and `THIRD_PARTY_LICENSES/`.
