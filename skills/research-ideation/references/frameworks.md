# The thirteen lenses

Full treatments for the lenses summarised in `SKILL.md`. Work through one lens at a time; the depth is here, not in the main file.

---

## L1 — Problem-first vs solution-first

Research ideas originate in two modes. Knowing which you are in prevents the two classic failures: building a solution nobody needs, and chasing a problem you cannot approach.

**Problem-first** (pain point → method): starts from a concrete failure or bottleneck. Impactful by construction, because the motivation is intrinsic. Risk: converges on incremental fixes.

**Solution-first** (new capability → application): starts from a tool, result, or insight looking for a use. Often drives breakthroughs by unlocking the previously impossible. Risk: a hammer looking for a nail.

**Workflow**

1. Write the idea in one sentence.
2. Classify it.
3. Problem-first → name who suffers, and what it costs them today.
4. Solution-first → name at least two genuine problems the capability addresses.
5. Either way, state the gap: what cannot be done today that this enables?

**Self-check**

- [ ] Can I name a specific person or community who needs this?
- [ ] Is the problem actually unsolved, or only under-marketed?
- [ ] If solution-first, does the solution create capability or replicate it?

---

## L2 — Reformulate the problem

Gestalt psychology and Kaplan & Simon's insight research: breakthroughs often come from re-representing the problem, not from solving the stated one.

The shift is from *"How do I solve this?"* to *"Am I thinking about this correctly?"*

| Strategy | Example |
|---|---|
| Change the objective | "Make the algorithm faster" → "Eliminate the need for this computation" |
| Change the formalism | Graph problem → spectral linear algebra |
| Change the granularity | Per-token prediction → per-span prediction |
| Change the agent | "How should the model learn?" → "How should the data teach?" |
| Change the timescale | Real-time optimization → amortized inference |
| Invert the direction | Forward simulation → inverse problem |

**Workflow**

1. State the problem in one sentence.
2. Surface the hidden assumptions: formalism, objective, granularity, agent, timescale.
3. For each, generate the alternative: "what if the opposite were true?"
4. Ask whether the reformulation makes the problem easier, harder, or different in a useful way.

A reformulation that makes a hard problem easy is often publishable on its own.

**Examples:** PageRank (importance → graph eigenvector), Dropout (regularizer → approximate ensemble), attention (remember everything → query selectively).

---

## L3 — Constraint analysis (Boden)

Boden distinguishes three kinds of creativity: **exploratory** (search inside the space), **combinational** (combine spaces), **transformational** (change the rules of the space). Transformational creativity is rarest and highest-impact: it changes what counts as a valid solution.

**Workflow**

1. List 5–10 constraints on the current approach: computational, methodological, architectural, evaluative, social.
2. Classify each as **hard** (physically necessary), **soft** (convention), or **hidden** (implicitly assumed and never stated).
3. For each soft or hidden constraint, ask: relax it, tighten it, or replace it with a different one.
4. Hidden constraints are the most fertile. The productive move is usually to expose one and drop it.

**Hall of fame**

| Constraint dropped | Result |
|---|---|
| "Data must fit in memory" | Streaming and external-memory algorithms |
| "Training needs human labels" | Self-supervised learning |
| "Models must be deterministic" | Variational methods, diffusion |
| "Inference is one forward pass" | Iterative refinement, chain-of-thought |

**Self-check:** which constraint in my list have I never seen anyone question?

---

## L4 — Structural analogy and bisociation

Koestler's **bisociation** connects two unrelated frames; Gentner's **structure-mapping** explains why only relational analogies work. Dunbar's lab studies found that distant analogies generated discoveries while nearby ones refined them.

| Depth | Value | Example |
|---|---|---|
| Surface | Low | "A neural network is like a brain" |
| Relational | Medium | "Attention allocation mirrors resource allocation in economics" |
| Structural | High | "Diffusion reverses a thermodynamic process, so non-equilibrium stat-mech applies" |

**Bisociation workflow (volume)**

1. Pick two domains you know at least a little.
2. List 5–10 primitives in each.
3. Build the cross-product matrix.
4. For each cell: "what would it mean to apply A's primitive to B's problem?"
5. Filter for testable, non-trivial combinations; check the mapping is mechanistic.

**Structure-mapping workflow (depth)**

1. Restate the problem in causal, domain-neutral language.
2. Find other systems that perform the same relational operation.
3. Prefer the most distant match with genuine structural fidelity.
4. Map the mechanism and adapt it.
5. Derive at least one prediction you did not already have.

**Validation**

- [ ] Mechanisms map, not just labels
- [ ] The analogy yields a testable prediction
- [ ] A source-domain expert would accept the mechanism as correctly understood
- [ ] It is non-obvious to the target audience

---

## L5 — Negation and inversion

From De Bono's lateral thinking and TRIZ: take an assumption everyone holds and invert it.

**Workflow**

1. List 5–10 things "everyone knows" in the subfield.
2. Negate each; ask what system you would build.
3. Discard incoherent negations. For ones already tried, check whether conditions changed (L8).
4. Unexplored and coherent → candidate.

| Assumption | Negation | Result |
|---|---|---|
| Strong consistency required | Eventual is fine | CRDTs, eventual consistency |
| Exact answers required | Approximate is fine | Sketches, LSH, ANN |
| Labels required | Learn without them | Self-supervised learning |
| All parameters used per token | Sparse activation | Mixture of experts |
| Training and inference are separate | Keep learning | Test-time training |
| Errors must be prevented | Embrace and correct | Speculative decoding |

**TRIZ moves for CS:** inversion (generative vs discriminative), segmentation (microservices, MoE), merging (end-to-end), universality (multi-task), nesting (meta-learning), dynamization (adaptive computation).

---

## L6 — Abstraction ladder

Polya's heuristic: can you solve a more general problem? A more specific one? An analogous one?

| Move | Question | Outcome |
|---|---|---|
| Generalize | Is my solution a special case of something broader? | Framework or theory paper |
| Specialize | What happens under an extreme constraint? | Niche application, surprising failure |
| Analogize | Where else does this pattern appear? | Cross-domain transfer (L4) |

**Generalize:** replace each specific element with a variable ("ResNet on ImageNet" → "architecture X on distribution Y"), then ask under what conditions the claim holds. If the general principle is new, that is the contribution.

**Specialize:** add extreme constraints — tiny data, huge dimensionality, adversarial inputs, real-time budgets. Failure reveals the method's true assumptions.

**When:** generalize if you have results but no explanation; specialize if you have theory but no grounding; analogize if stuck in either direction.

---

## L7 — Tension synthesis (Janusian)

Rothenberg found that eminent creators hold two contradictory ideas at once instead of choosing. In CS, the influential results usually come from tensions the field thought were irreconcilable.

| Contradiction | Resolution |
|---|---|
| Consistency vs availability | CAP formalized it; Raft and CRDTs found practical middles |
| Security vs usability | Zero-knowledge proofs |
| Expressiveness vs tractability | Probabilistic programming |
| Memorization vs generalization | Grokking |
| Compression vs quality | Learned neural codecs |

**Workflow**

1. Name a binary the field treats as a trade-off.
2. Do not choose. Ask: what system achieves both? Under what conditions is the trade-off not fundamental? Is the opposition an artifact of how the problem was formalized?
3. Seek a synthesis that requires a new abstraction, not a compromise.
4. Test it empirically.

**Common tensions worth mining:** performance vs efficiency, privacy vs utility, generality vs specialization, safety vs capability, interpretability vs performance, scale vs accessibility.

**Self-check:** am I holding the contradiction, or resolving it early? Is my synthesis a new idea or a split-the-difference?

---

## L8 — What changed / adjacent possible

Kauffman's **adjacent possible**: ideas become thinkable when their prerequisites exist. This is why independent simultaneous discovery is common.

**Workflow**

1. List enablers from the last 1–3 years: hardware, context length, inference cost, datasets, open weights, tooling, theory, regulation, public failures.
2. For each: what was previously impractical that is now possible?
3. Combine enablers — the strongest adjacent possibles sit at intersections.
4. Check who else can see it. If everyone can, speed or a unique angle is the differentiator.

**Timing signal:** needs technology that does not exist → too early, park it. Could have been done five years ago → too late, check the literature. The sweet spot is feasible in the last 6–18 months.

**Also useful for revisiting old negative results:** list the assumptions that caused rejection; ask which are still true; re-run with the rest.

---

## L9 — Compose and decompose

Innovation often lies in arrangement, not in new primitives.

**Compose:** find two methods solving complementary subproblems; ask what capability emerges from combining them (retrieval + chain-of-thought → retrieval-augmented reasoning).

**Decompose:** take a monolith apart and ask which component is load-bearing (fine-tuning splits into data selection, optimization, regularization — data selection usually dominates).

**Workflow**

1. List 5–10 components or techniques in the area.
2. Compose pairs; ask about emergent capability.
3. Decompose a complex method; isolate each component's contribution.
4. For compositions: is the gain emergent or additive?
5. For decompositions: is there a dominant or a redundant component?

---

## L10 — Stakeholder rotation

Each perspective exposes a different class of question.

| Stakeholder | Questions |
|---|---|
| End user | Usable? Which errors are unacceptable? What latency is tolerable? |
| Developer | Debuggable? Maintenance burden? Does it compose? |
| Theorist | Why does it work? What guarantees? Where are the gaps? |
| Adversary | How is it exploited? What are the attack surfaces? |
| Ethicist | Who is harmed? What biases are embedded? Who is excluded? |
| Regulator | Auditable? Explainable? Accountable? |
| Operator | Cost? Scaling behaviour? Failure modes? |

**Workflow:** describe the system in one paragraph; spend five minutes in each role; list three concerns per role; the unaddressed concern with the widest impact is the research question.

---

## L11 — Boundary probing

Where a method breaks is often worth more than where it works.

**Boundaries:** distributional (out-of-distribution), scale (10× or 0.1×), adversarial, compositional (combined capabilities), temporal (concept drift).

**Workflow**

1. Pick a widely used method with strong reported results.
2. Identify the implicit assumptions in its evaluation: dataset, scale, domain, metric.
3. Violate them systematically.
4. Document where and how it breaks.
5. Diagnose the cause, not just the symptom.
6. Propose a fix, or argue the failure is fundamental.

**Self-check:** am I probing a genuine boundary or confirming a known limitation? Can I explain why?

---

## L12 — Simplicity test

Fields over-index on elaborate solutions when a tuned baseline is competitive.

**Warning signs:** many hyperparameters with narrow optima; ablations where every component contributes marginally; the simple baseline was never tuned; the improvement over baselines is within noise on most benchmarks.

**Workflow**

1. Identify the current SOTA.
2. Strip it to its one key idea.
3. Build that minimal version with careful engineering.
4. Compare fairly: same compute, same tuning effort.
5. Small gap → the simplicity is the contribution. Large gap → you now know what the complexity buys.

**Framings:** "We show that [simple method] with [one modification] matches [complex SOTA]"; "We identify [component] as the critical driver, not [the others]".

---

## L13 — Two-sentence test

> **Sentence 1 (problem):** "[Domain] struggles with [problem], which matters because [consequence]."
> **Sentence 2 (insight):** "We [approach] by [mechanism], which works because [reason]."

**If you cannot fill it in:** the problem is vague → L1; the insight is unclear → L12; the significance is unestablished → L7.

**Calibration:** would a smart colleague outside the subfield see why it matters? Does it survive without jargon? What is a skeptic's first objection, and is it answerable?

---

## Deep-session protocol

Combining lenses is more productive than running one exhaustively. A 90-minute session:

**Map the space (15 min)**

1. L3: list constraints; mark hard, soft, hidden.
2. L8: list recent enablers that change the feasibility landscape.

**Generate disruptions (30 min)**

3. L5: negate three soft or hidden constraints.
4. L4: pick a distant field; build the cross-product matrix.
5. L2: restate the problem three ways — objective, formalism, agent.

**Deepen the leads (30 min)**

6. L4: for each promising idea, find the structural analogy and extract predictions.
7. L6: move each idea up (generalize) and down (specialize).
8. L7: hold the tension; look for synthesis rather than a side.

**Evaluate (15 min)**

9. L13 on every survivor.
10. L12 on the winner: what is the simplest version that would still be interesting?

An idea that survives all four phases and passes the two-sentence test is worth a pilot, not necessarily a paper.
