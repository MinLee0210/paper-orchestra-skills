# Experimental log

> Synthetic example. All numbers are illustrative and must not be treated as real results.

## Setup

- **Task:** causal language modeling on two synthetic sequence tasks.
- **Datasets:**
  - CopyLong: sequences of 512 tokens; 20,000 train, 2,000 validation, 2,000 test.
  - Needle: sequences of 1,024 tokens; 10,000 train, 1,000 validation, 1,000 test.
- **Metrics:** validation perplexity (lower is better) and exact-match on the final query (higher is better).
- **Baselines:**
  - Dense: full causal attention.
  - Window: fixed local window of 64 tokens.
  - Static: fixed stride pattern with 25% global tokens.
- **Implementation:** 6 layers, 256 hidden dimensions, 4 heads, AdamW, learning rate 3e-4, batch size 64, 20 epochs, one NVIDIA A100.
- **Evaluation protocol:** three seeds; report mean and standard deviation of the best validation checkpoint.

## Main results

| Method | CopyLong PPL | CopyLong EM | Needle PPL | Needle EM |
|---|---:|---:|---:|---:|
| Dense | 12.4 ± 0.2 | 71.2 ± 0.8 | 9.8 ± 0.3 | 64.1 ± 1.1 |
| Window | 15.1 ± 0.3 | 58.4 ± 1.2 | 11.6 ± 0.4 | 49.7 ± 1.4 |
| Static | 14.6 ± 0.2 | 60.9 ± 0.9 | 11.1 ± 0.3 | 52.3 ± 1.0 |
| Ours | 12.9 ± 0.2 | 69.8 ± 0.7 | 10.1 ± 0.2 | 62.9 ± 0.9 |

## Ablations

| Variant | Change | CopyLong PPL | Needle EM |
|---|---|---:|---:|
| Full model | — | 12.9 | 62.9 |
| No sparsity penalty | lambda = 0 | 12.7 | 61.4 |
| Global fraction 12.5% | k reduced | 13.4 | 58.8 |
| Global fraction 50% | k increased | 12.8 | 63.0 |
| Gate fixed to 0.25 | no routing | 14.2 | 53.1 |

## Qualitative observations

- The gate assigns larger values to positions that must copy a token from 256 steps earlier.
- On sequences with no long-range dependency, the gate collapses to a near-constant low value.
- The sparsity penalty controls the global fraction monotonically between 10% and 45%.
- Removing routing costs 9.8 exact-match points on Needle, which is larger than the gap between routing and dense attention.

## Failed runs and caveats

- A hard top-k gate without a straight-through estimator failed to train; gradients were zero for unselected tokens.
- The gain over Dense on Needle perplexity is within one standard deviation.
- No experiments were run beyond 1,024 tokens or 6 layers.

## Unverified values

None. Every value above is synthetic but internally consistent for this example.
