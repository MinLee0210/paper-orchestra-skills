# FAQ

## What is PaperOrchestra Skills?

PaperOrchestra Skills is an open-source collection of Agent Skills that automates the writing of AI research papers from raw materials. It implements the five-stage PaperOrchestra method: outline generation, literature review, figure generation, section writing, and iterative content refinement.

## Who is it for?

Researchers and engineers who already have an idea and experimental results and want a structured first draft: a complete LaTeX manuscript, a verified bibliography, figures, and a compiled PDF. It is also useful for studying multi-agent writing pipelines, citation verification, and LLM-based evaluation.

## What inputs does it need?

- `idea.md`: the method, contributions, and scope.
- `experimental_log.md`: setup, exact numbers, ablations, and observations.
- A LaTeX template with `guidelines.md`.
- Optional figures.
- A research cutoff date in `YYYY-MM`.

## What does it output?

A project directory containing `outline.json`, a verified citation registry, `references.bib`, `citation_map.json`, figures, a complete draft, `final_paper.tex`, `final_paper.pdf`, and optional evaluation metrics.

## How does it prevent fabricated citations?

Discovery proposes candidates using web search. Verification requires the Semantic Scholar API to return a matching title (similarity above 70), an abstract, and a publication date before the cutoff. The writer may cite only keys in the verified `citation_map.json`. The validator rejects unknown keys.

## What happens if a paper cannot be verified?

It is dropped, and the gap is reported. The pipeline does not fall back to model memory. A missing citation is recoverable; a fabricated one is not.

## How does it prevent invented results?

The experimental log is the only source of numbers. Section writing extracts values directly from it. Content refinement is instructed to ignore reviewer requests for experiments that are not in the log. The table instructions say to leave a cell empty rather than estimate.

## How is the literature review kept from becoming a survey?

The outline splits the work. The Introduction gets macro context: impact, surveys, foundational work. Related Work gets micro comparisons: methodology clusters, SOTA baselines, limitation evidence, and a bridge back to the proposed method. The two scopes are searched separately to avoid citation overlap.

## How does the refinement loop stop?

It keeps a revision only when the overall reviewer score increases, or when the score ties with sub-axis gains at least as large as drops. It stops on a score decrease, a degrading tie, the iteration limit (default 3), or no change.

## Which models does it use?

The skills do not pin a model. They use whatever model and tools the host agent provides. The scripts use the Semantic Scholar API for verification and standard Python for deterministic operations. This is a deliberate change from upstream, which used Gemini and OpenAI clients directly.

## Which agents support these skills?

Claude Code, opencode, and other runtimes that read the `SKILL.md` format. `./install.sh` links skills into `~/.claude/skills` and `~/.config/opencode/skills`.

## Which conference templates are included?

CVPR 2025 and ICLR 2025. Custom venues work when they provide `template.tex`, `guidelines.md`, `references.bib`, and their style files. See the `paper-template` skill.

## Can it handle a two-column paper?

Yes. The section-writing and refinement skills include rules for single-column figures, `figure*` for wide figures, table overflow, and page limits. CVPR is the two-column reference.

## Can it generate conceptual diagrams?

Yes, but the preference is vector drawing (TikZ, SVG, or matplotlib) over image generation, because diagrams must reflect the method rather than look plausible. If the host provides an image model, it can be used after the vector option.

## Can it evaluate a paper?

Yes. It computes citation precision/recall/F1 with P0/P1 breakdowns, scores literature reviews on six axes, produces an AgentReview-style overall score, and aggregates side-by-side comparisons.

## Are the evaluation numbers trustworthy?

Treat them as relative signals. LLM judges have biases, citation F1 depends on registry quality, and acceptance rates are simulated. They are useful for catching regressions and comparing pipelines. Human review remains the standard.

## Is the output ready to submit?

No. It is a strong draft. Verify every number, citation, figure, and claim. Check anonymity, page limits, and the venue's policy on AI-assisted writing. The human author remains accountable.

## Is it free?

The repository is Apache-2.0. You pay only for the model and API usage your host provides. Semantic Scholar has a free API with rate limits; an API key raises them.

## Does it work offline?

Writing and refinement can work offline with an existing BIB file and figures. Literature discovery and verification require network access. Offline citation generation is not supported.

## Why not just use one large prompt?

A single prompt has no verification step and no stopping rule. It cannot tell you which citations are real, whether a figure matches the log, or whether a revision improved the paper. The stage boundaries exist to make those checks possible.

## What was removed from the original PaperOrchestra code?

The Streamlit frontend, provider client wrappers, batch dataset processing, email delivery, and private PaperBanana retrieval pool. The method, prompts, citation policy, reviewer loop, and templates are preserved. See [upstream notes](upstream.md).
