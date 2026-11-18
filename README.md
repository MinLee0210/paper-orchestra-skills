# PaperOrchestra Skills

**Agent Skills for automated AI research paper writing — from raw idea and experiment logs to a submission-ready LaTeX manuscript.**

PaperOrchestra Skills is an open-source collection of portable [Agent Skills](https://docs.claude.com/en/docs/claude-code/skills) that turns unstructured pre-writing materials into a complete research paper: outline, figures, verified literature review, LaTeX sections, iterative peer-review refinement, and a final PDF. It is a skill-native port of [Google Research's PaperOrchestra](https://github.com/google-research/paper-orchestra) (Song et al., 2026), redesigned for Claude Code, opencode, Codex, and any agent that reads a `SKILL.md`.

> **What it is:** a multi-agent paper-writing workflow packaged as reusable skills.
> **What it is not:** a substitute for human scientific judgment. You remain responsible for the correctness, originality, and integrity of every generated manuscript.

## At a glance

| Question | Answer |
|---|---|
| Input | `idea.md`, `experimental_log.md`, a LaTeX template, optional figures, a research cutoff |
| Output | verified bibliography, figures, `final_paper.tex`, `final_paper.pdf`, optional metrics |
| Pipeline | outline → literature + plotting (parallel) → section writing → refinement → evaluation |
| Skills | 9 portable `SKILL.md` packages with references and deterministic scripts |
| Templates | CVPR 2025, ICLR 2025, generic IEEE conference, arXiv preprint, or any custom venue |
| Citation safety | Semantic Scholar + arXiv/Crossref/DBLP verification, strict cutoff, targeted matches at >= 90 |
| Works with | Claude Code, opencode, Codex-style agents, custom `SKILL.md` runtimes |
| License | Apache-2.0 |

## Quick start

```bash
git clone https://github.com/MinLee0210/paper-orchestra-skills.git
cd paper-orchestra-skills
./install.sh                      # symlink skills into ~/.claude/skills and ~/.config/opencode/skills
```

Then ask your agent:

```text
Use the paper-orchestra skill to write a paper from ./my-project.
Inputs: raw_materials/idea.md, raw_materials/experimental_log.md.
Template: CVPR 2025. Research cutoff: 2024-11.
```

The orchestrator validates the inputs, runs the five stages, and stops at any quality gate that fails. You can also run stages individually:

```text
Use the paper-outline skill on ./my-project.
Use the paper-literature-review skill with cutoff 2024-11.
Use the paper-content-refinement skill to improve the draft and produce the final PDF.
```

### Requirements

- Python 3.9+ for the bundled scripts (standard library only, except where noted).
- `pdflatex` and `bibtex` for compiling papers. `xelatex`/`biber` are supported by the compile script.
- `SEMANTIC_SCHOLAR_API_KEY` (optional) to raise literature-verification rate limits.
- `PyMuPDF` and `Pillow` (optional) for rendering PDF pages during review.
- `pytest` (optional) to run the offline test suite.

No model API key is required by the skills. They use the model and tools provided by the host agent.

## Proof it runs

The repo ships a complete synthetic run: [`examples/paper-project/final_paper.pdf`](examples/paper-project/final_paper.pdf) (5 pages), its figures, a cached 12-paper bibliography, three-review refinement rounds, and [`run_report.json`](examples/paper-project/run_report.json). The demo is deliberately labeled as synthetic; it proves the pipeline and its artifacts, not a research result.

## Why this exists

Writing a paper from raw materials is not one task. It is five tasks with different failure modes:

- an outline that invents claims the experiments do not support;
- figures that are decorative instead of evidential;
- literature reviews that hallucinate citations or cite only the obvious papers;
- sections that contradict the experimental log;
- drafts that never improve because revision has no stopping rule.

PaperOrchestra addresses this with specialized agents, machine-readable artifacts, and explicit gates. This repository keeps that architecture and removes the parts that only made sense inside Google's Python application: the Streamlit demo, the Gemini/OpenAI client wrappers, batch dataset processing, email delivery, and provider-specific image generation. What remains is the method, expressed as skills any agent can follow.

## The five-stage pipeline

| Stage | Skill | Input | Output | Gate |
|---|---|---|---|---|
| 1 | `paper-outline` | idea, log, template, guidelines | `outline.json` | valid plan with figure, search, and citation plans |
| 2a | `paper-literature-review` | outline + materials | verified registry, `references.bib`, citation map, cited Intro/Related Work | every citation verified; targeted matches >= 90 with year/author; cutoff respected |
| 2b | `paper-plotting` | outline + materials | figures, captions, manifests | every planned figure produced or explicitly skipped |
| 3 | `paper-section-writing` | merged template + plan | complete LaTeX draft | compiles to PDF |
| 4 | `paper-content-refinement` | draft + log + guidelines | final `.tex` and `.pdf` | score improves; page limit met; no undefined refs |
| 5 | `paper-evaluation` | final paper + optional ground truth | citation F1, lit-review score, SxS wins | metrics computed from real files |

Stages 2a and 2b are independent and can run in parallel. The orchestrator merges their outputs before stage 3.

## Skills catalog

| Skill | Use it when you need to… |
|---|---|
| [`paper-orchestra`](skills/paper-orchestra/SKILL.md) | run or resume the full pipeline |
| [`paper-inputs`](skills/paper-inputs/SKILL.md) | prepare `idea.md`, `experimental_log.md`, figures, and remove leakage |
| [`paper-outline`](skills/paper-outline/SKILL.md) | plan the paper: sections, figures, search strategy, citation hints |
| [`paper-template`](skills/paper-template/SKILL.md) | scaffold CVPR 2025, ICLR 2025, IEEE conference, arXiv preprint, or a custom venue template |
| [`paper-plotting`](skills/paper-plotting/SKILL.md) | make data plots and conceptual diagrams with a critic loop |
| [`paper-literature-review`](skills/paper-literature-review/SKILL.md) | find, verify, deduplicate, and cite real papers; write Intro/Related Work |
| [`paper-section-writing`](skills/paper-section-writing/SKILL.md) | draft the remaining sections, tables, figures, and appendix |
| [`paper-content-refinement`](skills/paper-content-refinement/SKILL.md) | review, revise, fix formatting, and compile the final PDF |
| [`paper-evaluation`](skills/paper-evaluation/SKILL.md) | measure citation F1, literature quality, and side-by-side wins |

Each skill contains a `SKILL.md` with the workflow, plus `references/` for prompts and schemas and `scripts/` for deterministic operations. Read only what the task needs; the main file is deliberately short.

## What goes in

```text
my-project/
├── raw_materials/
│   ├── idea.md                 # method, contributions, scope
│   ├── experimental_log.md     # setup, numbers, ablations, observations
│   └── figures/                # optional existing figures + info.json
└── latex_template/             # template.tex, guidelines.md, style files
```

The experimental log is the only source of numbers. The idea file must not contain the source paper's citations, author names, or final results. The `paper-inputs` skill audits both before any expensive stage runs.

## What comes out

```text
paper_project/
├── outline.json
├── figures/ + plotting_results.json
├── literature_agent_output/
│   ├── registry.json
│   ├── citation_map.json
│   ├── references.bib
│   └── updated_template.tex
├── latex_writeup/raw_draft_paper.tex
├── final_paper.tex
├── final_paper.pdf
└── metrics/
```

## Citation verification, not citation generation

The literature stage is deliberately split:

1. **Discovery** uses broad, parallel web search to find candidate papers.
2. **Verification** tries Semantic Scholar, then arXiv, Crossref, and DBLP. Exploration matches require a title ratio above 70. Targeted matches, such as the canonical paper for a dataset or optimizer, require **>= 90 plus a year or author check**. The paper must have an abstract and predate the cutoff.
3. **Writing** uses only the verified registry. Every `\cite{}` key must exist in `citation_map.json`.

The fallback chain matters in restricted environments: Semantic Scholar rate-limits aggressively, and a proxy can block it entirely. Falling back to another bibliographic source is acceptable; falling back to model memory is not.

This design targets the dominant failure mode of autonomous writers: a short, plausible reference list that is partly fabricated and misses most of the field. The bundled scripts make the verification step repeatable:

```bash
python skills/paper-literature-review/scripts/semantic_scholar.py \
  search --title "Attention Is All You Need" --year 2017 --cutoff 2024-11
python skills/paper-literature-review/scripts/semantic_scholar.py \
  search --title "AdamW" --author "Loshchilov" --year 2019 --targeted --cutoff 2024-11
```

## Evaluation

`paper-evaluation` implements four measurements from the PaperOrchestra paper:

- **Citation F1** against a ground-truth reference list, reported overall and separately for must-cite (P0) and good-to-cite (P1) papers.
- **Literature review quality** on six 0–100 axes with anti-inflation caps.
- **Overall quality** via an AgentReview-style reviewer with an accept/reject decision.
- **Side-by-side win rate** against a baseline, evaluated in both orderings.

Overall scores use three independent reviewer samples aggregated by mean (or median), not a single self-review. Per-axis variance is recorded so an unstable score is visible.

Metrics are useful for detecting regressions. They are not a substitute for human review.

## Frequently asked questions

### What is PaperOrchestra Skills?

It is a set of reusable agent skills that implement the PaperOrchestra multi-agent paper-writing method. Each stage is a separate skill with its own inputs, outputs, quality gate, and supporting scripts.

### How is it different from a single “write my paper” prompt?

A single prompt produces fluent text with no verification. This pipeline separates planning, literature discovery, citation verification, figure generation, section writing, and revision. Each stage has an artifact you can inspect and a gate that can fail, so errors surface before they reach the final PDF.

### Can it write a paper from scratch?

It can draft a paper from an idea and an experimental log. It cannot perform the research, invent valid experiments, or certify claims. If the log lacks a result, the pipeline is designed to leave it out rather than fabricate it.

### Does it fabricate citations?

The workflow is built to prevent that. Discovery may guess; verification may not. A paper enters the bibliography only after Semantic Scholar, arXiv, Crossref, or DBLP returns matching metadata and an abstract. The validator rejects citation keys that are not in the verified map.

### Which conferences are supported?

Bundled templates: CVPR 2025 (two-column, 8 pages), ICLR 2025 (single-column, 10 pages), a generic IEEE conference scaffold, and a neutral arXiv preprint. Any venue works if you provide a `template.tex`, `guidelines.md`, and the venue's style files. See the `paper-template` skill for the contract.

### Which agents does it work with?

Any agent that supports the `SKILL.md` format: Claude Code, opencode, Codex-style agents, and custom agent runtimes. `./install.sh` links the skills into the common Claude and opencode directories.

### Does it need an API key?

Only for literature verification. Set `SEMANTIC_SCHOLAR_API_KEY` to raise rate limits. The scripts work without a key at lower throughput. No model API key is required by the skills themselves; they use whatever model and tools the host agent provides.

### Can I use it without internet access?

You can write and refine a paper if you already have a BIB file and figures. The literature discovery and verification stages require network access. Offline mode is not a supported path for citation generation.

### Is there a test suite and CI?

Yes. `tests/` runs offline with pytest; it covers leakage blocking, outline validation, matching thresholds and provider fallbacks, bibliography construction, reviewer aggregation, LaTeX linting, template scaffolding, and the demo output. `.github/workflows/ci.yml` runs the tests and compiles all bundled templates.

### Is there a sample output?

Yes. `examples/paper-project/final_paper.pdf` is a complete synthetic run with a 5-page paper, figures, a 12-paper cached bibliography, three-review refinement rounds, and `run_report.json`. It is deliberately marked as a demo; the citations are cached fixtures, not live verification.

### Is the generated paper ready to submit?

Treat it as a strong draft. Verify every number, every citation, every figure, and every claim. Check the venue's anonymity and page-limit rules. The pipeline reduces mechanical errors; it does not assume academic responsibility.

## Install

The skills are plain directories. You can copy or symlink them.

```bash
./install.sh                          # Claude + opencode
./install.sh --target ~/.claude/skills
./install.sh --target ~/.config/opencode/skills
./install.sh --uninstall
```

Manual install:

```bash
ln -s "$PWD/skills/paper-orchestra" ~/.claude/skills/paper-orchestra
```

## Tests and CI

Run the offline suite:

```bash
python -m pytest -q
```

The tests cover the blocking leakage gate, outline validation, targeted matching, provider fallbacks, bibliography construction, reviewer aggregation, LaTeX linting, template scaffolding, compilation, and the committed demo output. CI compiles all four bundled templates and runs the deterministic pipeline stages.

## Repository structure

```text
skills/                     # one directory per Agent Skill
├── paper-orchestra/        # orchestrator + pipeline status script
├── paper-inputs/           # raw-material templates and validator
├── paper-outline/          # outline prompt, schema, validator
├── paper-template/         # CVPR/ICLR/IEEE/arXiv templates, scaffold script
├── paper-plotting/         # figure prompts, style guide, validator
├── paper-literature-review/# S2 verification, BibTeX, citation map, validators
├── paper-section-writing/  # section prompt, LaTeX conventions, linter
├── paper-content-refinement/# compile, render, review decision, prompts
└── paper-evaluation/       # citation F1, SxS aggregation, rubrics
tests/                      # offline pytest suite and fixtures
.github/workflows/ci.yml    # tests + template compilation
examples/paper-project/     # complete synthetic run with final PDF and run_report.json
docs/                       # architecture, input format, evaluation, FAQ, upstream notes
examples/paper-project/     # synthetic input files for a first run
```

## Documentation

- [Architecture](docs/architecture.md) — stage contracts, artifacts, and data flow.
- [Input format](docs/input-format.md) — exact `idea.md`, log, figure, and template specs.
- [Citation policy](docs/citation-policy.md) — verification thresholds and cutoff rules.
- [Evaluation](docs/evaluation.md) — metrics, rubrics, and reporting.
- [Upstream notes](docs/upstream.md) — what was ported, changed, and removed.
- [FAQ](docs/faq.md) — longer answers for humans and answer engines.

## Keywords

automated research paper writing · AI paper writer · LaTeX manuscript generation · multi-agent paper writing · literature review agent · citation verification · Agent Skills · Claude Code skills · opencode skills · PaperWritingBench · PaperOrchestra · CVPR 2025 template · ICLR 2025 template · IEEE conference template · arXiv preprint template · citation F1 · LLM peer review

## Attribution and license

The method, prompts, and conference templates derive from [Google Research's PaperOrchestra](https://github.com/google-research/paper-orchestra), licensed under Apache-2.0. This repository's skill packaging and scripts are released under Apache-2.0 as well. See [NOTICE](NOTICE) and [LICENSE](LICENSE).

PaperOrchestra citation:

```bibtex
@article{song2026paperorchestra,
  title={PaperOrchestra: A Multi-Agent Framework for Automated AI Research Paper Writing},
  author={Song, Yiwen and Song, Yale and Pfister, Tomas and Yoon, Jinsung},
  journal={arXiv preprint arXiv:2604.05018},
  year={2026}
}
```
