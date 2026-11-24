# Examples

`paper-project/` is a complete, synthetic end-to-end run. It includes raw
materials, an outline, a cached citation registry, figures, a draft, a
three-review refinement round, the final PDF, and `run_report.json`.

The method is invented, the numbers are illustrative, and the template is a
neutral `article` scaffold rather than a real venue. See
[`paper-project/README.md`](paper-project/README.md) for the artifact map and
the honest caveats.

## Try the input audit

```bash
python skills/research-inputs/scripts/validate_inputs.py examples/paper-project
```

## Try a full run with an agent

```text
Use the research-orchestra skill.
Project: examples/paper-project
Research cutoff: 2024-11
Template: the provided neutral template.
```

For a real submission, scaffold a venue template first:

```bash
python skills/research-template/scripts/init_template.py \
  --venue cvpr2025 --out examples/paper-project/latex_template --force
```

## What is intentionally absent

- No verified citation registry. The literature stage must discover real papers; a bundled fake registry would defeat the point.
- No generated figures. The plotting stage creates them from the log.
- No final PDF. That is the output of a run, not an input.

The example is here to show the shape of the inputs and to make the first command succeed. Do not submit anything derived from it.
