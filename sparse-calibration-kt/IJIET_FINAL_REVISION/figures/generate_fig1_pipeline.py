#!/usr/bin/env python3
"""Compact 1-column Fig. 1: diagnostic pipeline with Table 3 L1–L7 tags."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

HERE = Path(__file__).resolve().parent
OUT = HERE / "fig1_pipeline.png"

ROW1 = [
    "Raw logs",
    "Preprocess\n[L2]",
    "Split\n[L1]",
    "KC map\n[L3]",
    "Train-only\nfrequency",
]
ROW2 = [
    "KC strata\n[L4]",
    "Cold-start\n[L7]",
    "Predict\n[L6]",
    "ECE / Brier\n[L5]",
    "Reliability\n+ report",
]


def box(ax, x, y, w, h, text: str) -> None:
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.012,rounding_size=0.02",
            linewidth=0.7,
            edgecolor="#222222",
            facecolor="#F4F4F4",
        )
    )
    ax.text(
        x + w / 2,
        y + h / 2,
        text,
        ha="center",
        va="center",
        fontsize=6.4,
        fontname="Times New Roman",
        color="#111111",
        linespacing=1.15,
    )


def arrow(ax, x1, y1, x2, y2) -> None:
    ax.add_patch(
        FancyArrowPatch(
            (x1, y1),
            (x2, y2),
            arrowstyle="-|>",
            mutation_scale=7,
            linewidth=0.7,
            color="#333333",
            shrinkA=0,
            shrinkB=0,
        )
    )


def main() -> None:
    fig, ax = plt.subplots(figsize=(3.38, 2.05), dpi=300)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    n = 5
    w, h = 0.168, 0.28
    gap = (1 - n * w) / (n + 1)
    y1, y2 = 0.62, 0.10
    xs = [gap + i * (w + gap) for i in range(n)]
    for i, (lab, x) in enumerate(zip(ROW1, xs)):
        box(ax, x, y1, w, h, lab)
        if i < n - 1:
            arrow(ax, x + w, y1 + h / 2, xs[i + 1], y1 + h / 2)
    mid_y = (y1 + y2 + h) / 2
    x_r = xs[-1] + w / 2
    x_l = xs[0] + w / 2
    ax.plot([x_r, x_r], [y1, mid_y], color="#333333", linewidth=0.7)
    ax.plot([x_r, x_l], [mid_y, mid_y], color="#333333", linewidth=0.7)
    arrow(ax, x_l, mid_y, x_l, y2 + h)
    for i, (lab, x) in enumerate(zip(ROW2, xs)):
        box(ax, x, y2, w, h, lab)
        if i < n - 1:
            arrow(ax, x + w, y2 + h / 2, xs[i + 1], y2 + h / 2)
    fig.savefig(OUT, bbox_inches="tight", pad_inches=0.04, facecolor="white")
    plt.close(fig)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
