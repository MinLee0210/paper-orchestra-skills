# Examples

The example project is synthetic. It exists to exercise the pipeline: the method is invented, the numbers are illustrative, and the template is a neutral `article` scaffold rather than a real venue.

## Try the input audit

```bash
python skills/paper-inputs/scripts/validate_inputs.py examples/paper-project
```

## Try a full run with an agent

```text
Use the paper-orchestra skill.
Project: examples/paper-project
Research cutoff: 2024-11
Template: the provided neutral template.
```

For a real submission, scaffold a venue template first:

```bash
python skills/paper-template/scripts/init_template.py \
  --venue cvpr2025 --out examples/paper-project/latex_template --force
```

## What is intentionally absent

- No verified citation registry. The literature stage must discover real papers; a bundled fake registry would defeat the point.
- No generated figures. The plotting stage creates them from the log.
- No final PDF. That is the output of a run, not an input.

The example is here to show the shape of the inputs and to make the first command succeed. Do not submit anything derived from it.
