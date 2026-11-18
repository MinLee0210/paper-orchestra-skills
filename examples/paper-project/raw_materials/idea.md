# Idea: Confidence-Aware Token Routing

> Synthetic example. Not a real research contribution.

## Problem

Dense attention scales quadratically with sequence length. Fixed sparse patterns reduce cost but apply the same connectivity to every input, so they waste computation on easy tokens and miss long-range dependencies on hard ones. The gap is a routing mechanism that chooses sparsity per input without collapsing to a single static pattern.

## Method

Each token produces a routing score from a small gating network. Tokens are partitioned into a local set, which attends densely within a window, and a global set, which attends to a compressed summary of the sequence. The gate is trained jointly with the language-modeling objective.

Let $h_i$ be the hidden state of token $i$ and $g_i \in [0,1]$ its gate:

$$
g_i = \sigma(W_g h_i + b_g), \qquad
\mathcal{L} = \mathcal{L}_{\text{lm}} + \lambda \sum_i g_i
$$

The sparsity penalty $\lambda$ controls the fraction of global tokens. A straight-through estimator passes gradients through the discrete top-$k$ selection.

## Contributions

- A per-input routing gate that mixes local and global attention.
- A sparsity penalty that makes the compute budget explicit and tunable.
- An evaluation on two synthetic sequence tasks showing that the gate concentrates on positions with long-range dependencies.

## Assumptions and scope

The method assumes a causal decoder-only model. It does not claim gains on retrieval or vision tasks. The experiments use short sequences and a single model size; the results should not be generalized to larger models without further evidence.

## Alternative approaches

Fixed window attention, learned static patterns, and low-rank attention all reduce cost. The distinction here is that the pattern is selected per input rather than per layer or per model.
