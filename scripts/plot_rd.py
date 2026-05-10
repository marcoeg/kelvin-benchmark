"""Plot rate-distortion curves from this repository's per-clip CSVs.

Reads results/<dataset>_rd_per_qp_<metric>.csv and writes a per-clip
grid plus a combined overlay PNG into plots/.

Usage:
    python scripts/plot_rd.py --dataset uvg --metric vmaf
    python scripts/plot_rd.py --dataset uvg --metric psnr
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt

QP_VALUES = (22, 27, 32, 37)
ROOT = Path(__file__).resolve().parent.parent

METRICS = {
    "vmaf": {"label": "VMAF", "ylim": (50, 100)},
    "vmaf_neg": {"label": "VMAF-NEG", "ylim": (50, 100)},
    "psnr": {"label": "PSNR-Y (dB)", "ylim": None},
    "ms_ssim": {"label": "MS-SSIM", "ylim": None},
}


def load_rows(csv_path: Path, metric: str) -> list[dict]:
    rows = []
    with open(csv_path) as f:
        for row in csv.DictReader(f):
            rate_b = [float(row[f"qp{q}_baseline_kbps"]) for q in QP_VALUES]
            rate_e = [float(row[f"qp{q}_enhanced_kbps"]) for q in QP_VALUES]
            qual_b = [float(row[f"qp{q}_baseline_{metric}"]) for q in QP_VALUES]
            qual_e = [float(row[f"qp{q}_enhanced_{metric}"]) for q in QP_VALUES]
            rows.append({
                "name": row["sequence"],
                "rate_b": rate_b, "rate_e": rate_e,
                "qual_b": qual_b, "qual_e": qual_e,
            })
    return rows


def plot_grid(rows: list[dict], metric: str, out_path: Path) -> None:
    n = len(rows)
    cols = 4
    rows_n = math.ceil(n / cols)
    fig, axes = plt.subplots(rows_n, cols, figsize=(4.2 * cols, 3.2 * rows_n))
    axes = axes.flatten() if hasattr(axes, "flatten") else [axes]

    for i, r in enumerate(rows):
        ax = axes[i]
        ax.plot(r["rate_b"], r["qual_b"], "o-", label="x264 baseline", color="#A84B2F")
        ax.plot(r["rate_e"], r["qual_e"], "s-", label="Kelvin + x264", color="#20808D")
        ax.set_xlabel("Bitrate (kbps)")
        ax.set_ylabel(METRICS[metric]["label"])
        ax.set_xscale("log")
        ax.set_title(r["name"][:40], fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=7, loc="lower right")

    for j in range(n, len(axes)):
        axes[j].axis("off")

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_combined(rows: list[dict], metric: str, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    for r in rows:
        ax.plot(r["rate_b"], r["qual_b"], "o-", color="#A84B2F", alpha=0.5)
        ax.plot(r["rate_e"], r["qual_e"], "s-", color="#20808D", alpha=0.5)
    ax.plot([], [], "o-", color="#A84B2F", label="x264 baseline")
    ax.plot([], [], "s-", color="#20808D", label="Kelvin + x264")
    ax.set_xscale("log")
    ax.set_xlabel("Bitrate (kbps)")
    ax.set_ylabel(METRICS[metric]["label"])
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", choices=["uvg"], default="uvg")
    ap.add_argument("--metric", choices=["vmaf", "psnr", "ms_ssim"], default="vmaf")
    args = ap.parse_args()

    csv_path = ROOT / "results" / f"{args.dataset}_rd_per_qp_{args.metric}.csv"
    rows = load_rows(csv_path, args.metric)

    plots_dir = ROOT / "plots"
    plots_dir.mkdir(exist_ok=True)
    plot_grid(rows, args.metric,
              plots_dir / f"{args.dataset}_rd_per_sequence_{args.metric}.png")
    plot_combined(rows, args.metric,
                  plots_dir / f"{args.dataset}_rd_combined_{args.metric}.png")
    print(f"Wrote plots/{args.dataset}_rd_per_sequence_{args.metric}.png and "
          f"plots/{args.dataset}_rd_combined_{args.metric}.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
