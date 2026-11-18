# Upstream notes

This repository ports [Google Research's PaperOrchestra](https://github.com/google-research/paper-orchestra) from a Python/Gemini application into a collection of Agent Skills.

## Mapping

| Upstream component | Here |
|---|---|
| `methods/paper_writer.py` orchestration | `paper-orchestra` skill |
| `methods/paper_writer_with_plotting.py` | `paper-orchestra` + parallel stage instructions |
| `methods/agents/outline_agent.py` + prompt | `paper-outline` skill |
| `methods/agents/literature_review_agent.py` + prompt | `paper-literature-review` skill + scripts |
| `methods/agents/section_writing_agent.py` + prompt | `paper-section-writing` skill |
| `methods/agents/content_refinement_agent.py` + prompt | `paper-content-refinement` skill + scripts |
| `methods/agents/plotting_agent.py` + PaperBanana prompts | `paper-plotting` skill + prompts |
| `autoraters/agent_review.py` | `paper-content-refinement/references/reviewer-rubric.md`, `paper-evaluation/references/agentreview.md` |
| `autoraters/lit_review_quality.py` | `paper-evaluation/references/lit-review-rubric.md` |
| `autoraters/citation_f1.py` | `paper-evaluation/scripts/citation_f1.py` |
| `autoraters/sxs_*.py` | `paper-evaluation/references/sxs-prompts.md` + `aggregate_sxs.py` |
| `templates/cvpr2025`, `templates/iclr2025` | `paper-template/assets/templates/` |
| `utils/pdf_utils.py` compile/render | `paper-content-refinement/scripts/compile_latex.py`, `render_pages.py` |
| `utils/scholar_utils.py` | `paper-literature-review/scripts/semantic_scholar.py` |
| `utils/gemini_utils.py`, `openai_utils.py`, `llm_backend_utils.py` | removed; the host agent supplies the model |
| `frontend/` Streamlit app | removed |
| batch dataset pipeline | removed |
| `paper_writing_cli.py` | replaced by skill invocation |

## What changed

**Provider neutrality.** Upstream calls Gemini and OpenAI through provider-specific clients. The skills use the host agent's model and tools. The deterministic scripts use only the standard library unless a PDF dependency is explicitly required.

**Prompts as references.** Prompts are preserved in `references/` but rewritten to remove Python format placeholders and provider-specific instructions. The substantive directives remain: exhaustive citation hints, macro/micro separation, exact-number tables, figure fidelity, and score-driven revision.

**Verification thresholds.** The Semantic Scholar logic is reimplemented in the standard library: fuzzy title matching above 70, exact-year bonus, abstract requirement, cutoff filtering, deduplication. The 1-query-per-second default is preserved.

**Reviewer loop.** The accept/reject logic is extracted into `decide_revision.py`: accept on overall increase, reject on decrease, and on a tie accept only when sub-axis gains are at least as large as drops.

**Formatting pass.** The VLM review is expressed as a prompt over rendered page images. `render_pages.py` produces individual pages and optional 2×2 grids with PyMuPDF and Pillow.

**Figure generation.** Upstream uses PaperBanana and a Gemini image model. The skill prefers code-generated plots and vector diagrams, and treats image generation as an optional tool when the host provides one. This removes a hard provider dependency and makes data figures reproducible.

## What was removed

- Streamlit frontend, process cleanup, and email delivery.
- Batch processing, process pools, resume logs, and dataset layout.
- Gemini/OpenAI client wrappers and retry/backoff plumbing.
- PaperBanana few-shot retrieval over a private reference pool.
- The PaperWritingBench dataset, which upstream says is not included in the code repository.
- Full autorater batch orchestration over folders of PDFs.

These removals do not affect the paper-writing method. They remove application scaffolding that the host agent already provides.

## Fidelity

Preserved from upstream:

- five-stage pipeline and the parallel literature/plotting step;
- outline directives, including exhaustive citation hints and the macro/micro split;
- literature discovery then sequential verification;
- 90% citation utilization target;
- Introduction and Related Work filled before the remaining sections;
- exact-value tables and figure fidelity rules;
- iterative review with monotonic acceptance;
- separate content and formatting loops;
- citation F1, literature-quality, overall-quality, and SxS evaluation concepts;
- CVPR 2025 and ICLR 2025 templates.

Changed deliberately:

- file-based artifacts instead of Python objects;
- host-provided models and tools instead of provider clients;
- deterministic scripts for verification, bibliography, compiling, rendering, and metric computation;
- explicit gates and a resume script.

## License

Upstream is Apache-2.0. The prompts and templates adapted here retain that license. See `NOTICE` and `LICENSE`.
