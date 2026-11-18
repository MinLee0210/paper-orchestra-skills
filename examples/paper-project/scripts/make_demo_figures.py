#!/usr/bin/env python3
"""Generate the illustrative figures for the synthetic demo paper.

The values are copied from raw_materials/experimental_log.md. This script is a
demo artifact; the paper-plotting skill normally asks the agent to write the
plotting code from the log.
"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "figures"
OUT.mkdir(parents=True, exist_ok=True)

PALETTE = ["#0072B2", "#D55E00", "#009E73", "#CC79A7"]
METHODS = ["Dense", "Window", "Static", "Ours"]
COPYLONG_PPL = [12.4, 15.1, 14.6, 12.9]
NEEDLE_PPL = [9.8, 11.6, 11.1, 10.1]
COPYLONG_EM = [71.2, 58.4, 60.9, 69.8]
NEEDLE_EM = [64.1, 49.7, 52.3, 62.9]

ABLATION = ["Full", "No penalty", "12.5% global", "50% global", "Fixed gate"]
ABLATION_PPL = [12.9, 12.7, 13.4, 12.8, 14.2]
ABLATION_EM = [62.9, 61.4, 58.8, 63.0, 53.1]

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 9,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linewidth": 0.5,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})


def grouped_bars(ax, values_a, values_b, ylabel, labels, title):
    x = range(len(labels))
    width = 0.36
    ax.bar([i - width / 2 for i in x], values_a, width, label="CopyLong", color=PALETTE[0])
    ax.bar([i + width / 2 for i in x], values_b, width, label="Needle", color=PALETTE[1])
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=15, ha="right")
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=10, pad=6)
    ax.legend(frameon=False)


def main_results():
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.8))
    grouped_bars(axes[0], COPYLONG_PPL, NEEDLE_PPL, "Validation perplexity", METHODS, "(a) Perplexity (lower is better)")
    grouped_bars(axes[1], COPYLONG_EM, NEEDLE_EM, "Exact match (%)", METHODS, "(b) Exact match (higher is better)")
    fig.tight_layout()
    fig.savefig(OUT / "fig_main_results.pdf", bbox_inches="tight", pad_inches=0.02)
    fig.savefig(OUT / "fig_main_results.png", dpi=300, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def ablation():
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.8))
    axes[0].bar(ABLATION, ABLATION_PPL, color=PALETTE[0])
    axes[0].set_ylabel("CopyLong perplexity")
    axes[0].set_title("(a) Effect of the budget", fontsize=10, pad=6)
    axes[0].tick_params(axis="x", rotation=20)
    axes[1].bar(ABLATION, ABLATION_EM, color=PALETTE[1])
    axes[1].set_ylabel("Needle exact match (%)")
    axes[1].set_title("(b) Long-range accuracy", fontsize=10, pad=6)
    axes[1].tick_params(axis="x", rotation=20)
    fig.tight_layout()
    fig.savefig(OUT / "fig_ablation.pdf", bbox_inches="tight", pad_inches=0.02)
    fig.savefig(OUT / "fig_ablation.png", dpi=300, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def routing_schematic():
    fig, ax = plt.subplots(figsize=(7.0, 3.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")

    def box(x, y, w, h, label, color):
        patch = FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.15",
            linewidth=1.0, edgecolor="#333333", facecolor=color,
        )
        ax.add_patch(patch)
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=8.5)

    def arrow(x1, y1, x2, y2):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=10, linewidth=1.0, color="#333333"))

    box(0.2, 2.0, 1.7, 1.0, "Token states\n$h_i$", "#E8F1FA")
    box(2.5, 2.0, 1.7, 1.0, "Gate\n$g_i=\\sigma(W_g h_i)$", "#FDF0E6")
    box(4.8, 3.0, 2.0, 0.9, "Local window\nattention", "#E9F5EE")
    box(4.8, 1.0, 2.0, 0.9, "Global summary\nattention", "#F5EAF3")
    box(7.5, 2.0, 1.9, 1.0, "Merge and\nproject", "#EEEEEE")
    arrow(1.9, 2.5, 2.5, 2.5)
    arrow(4.2, 2.7, 4.8, 3.4)
    arrow(4.2, 2.3, 4.8, 1.5)
    arrow(6.8, 3.4, 7.5, 2.7)
    arrow(6.8, 1.5, 7.5, 2.3)
    ax.text(4.45, 4.25, "top-$k$ split", fontsize=8, style="italic", ha="center")
    fig.tight_layout()
    fig.savefig(OUT / "fig_routing_schematic.pdf", bbox_inches="tight", pad_inches=0.02)
    fig.savefig(OUT / "fig_routing_schematic.png", dpi=300, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


if __name__ == "__main__":
    main_results()
    ablation()
    routing_schematic()
    print(f"Wrote figures to {OUT}")
