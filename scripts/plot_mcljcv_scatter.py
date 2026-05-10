"""Scatter BD-VMAF vs BD-VMAF-NEG per clip on MCL-JCV.

Reads results/mcljcv_summary.csv. Plots one point per clip; named
outliers are coloured and labelled.
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent

OUTLIER_COLORS = {
    "rate_floor_violation": "#A12C7B",
    "distribution_shift": "#964219",
    "metric_saturation": "#7A39BB",
}


def main() -> int:
    rows = []
    with open(ROOT / "results" / "mcljcv_summary.csv") as f:
        for r in csv.DictReader(f):
            if not r["sequence"].startswith("videoSRC"):
                continue
            rows.append(r)

    fig, ax = plt.subplots(figsize=(8, 6))
    xs, ys, labels = [], [], []
    for r in rows:
        try:
            x = float(r["bd_vmaf_pct"])
            y = float(r["bd_vmaf_neg_pct"])
        except ValueError:
            continue
        xs.append(x)
        ys.append(y)
        labels.append(r["sequence"])
        outlier = r["outlier_class"]
        color = OUTLIER_COLORS.get(outlier, "#20808D")
        ax.scatter([x], [y], color=color, s=70 if outlier else 35,
                   edgecolor="black" if outlier else "none", linewidth=0.6)
        if outlier:
            ax.annotate(r["sequence"], (x, y), xytext=(8, -4),
                        textcoords="offset points", fontsize=9)

    ax.axhline(0, color="black", lw=0.5)
    ax.axvline(0, color="black", lw=0.5)
    ax.set_xlabel("BD-VMAF (%)  - lower is better")
    ax.set_ylabel("BD-VMAF-NEG (%)  - lower is better")
    ax.set_title("Kelvin v1.0 on MCL-JCV  -  per-clip BD-rate")
    ax.grid(True, alpha=0.3)

    handles = [plt.scatter([], [], color=c, edgecolor="black", linewidth=0.6,
                           s=70, label=lbl.replace("_", " "))
               for lbl, c in OUTLIER_COLORS.items()]
    handles.append(plt.scatter([], [], color="#20808D", s=35, label="other clips (n=27)"))
    ax.legend(handles=handles, loc="lower right", fontsize=9)

    fig.tight_layout()
    out = ROOT / "plots" / "mcljcv_scatter_bdvmaf_vs_bdvmafneg.png"
    fig.savefig(out, dpi=150)
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
