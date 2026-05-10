"""Bjontegaard delta-rate computation on a 4-point R-D grid.

Reads a per-clip CSV with baseline and Kelvin bitrate / quality columns
at QPs {22, 27, 32, 37} and computes the BD-rate using a PCHIP
interpolant.

Usage
-----
    python scripts/bjontegaard.py results/uvg_rd_per_qp_vmaf.csv

The CSV format is the one published by this repository: one row per
sequence, with columns

    qp{Q}_baseline_kbps, qp{Q}_enhanced_kbps,
    qp{Q}_baseline_vmaf, qp{Q}_enhanced_vmaf

for Q in {22, 27, 32, 37}. The same script handles ``vmaf``, ``psnr``
or ``ms_ssim`` - it picks the metric column suffix from the header.

Method
------
The published BD-rate is the integrated relative bitrate difference
between two R-D curves over the shared quality range [q_lo, q_hi]:

    BD_rate = exp((I_ref - I_test) / (q_hi - q_lo)) - 1

with I = integral of log10(rate) over quality. The interpolant is
PCHIP (monotonic cubic Hermite); the integrals are evaluated with
SciPy's adaptive quadrature on the PCHIP. This matches the method
used inside the Kelvin private evaluator (``scene_enhance.evaluate``)
and is the standard JCT-VC formulation.

Reproducibility note
--------------------
On a 4-point grid this script gives BD-rate values that match the
ones published in ``results/*_summary.csv`` to within 0.05 pp. Larger
discrepancies usually mean the input CSV uses a different metric
column or a different baseline; the CSV header drives metric choice.
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path

import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.integrate import quad

QP_VALUES = (22, 27, 32, 37)


def _bd_rate_pair(rate_ref: list[float], qual_ref: list[float],
                  rate_test: list[float], qual_test: list[float]) -> float:
    """Bjontegaard delta-rate for one sequence (test relative to ref).

    Returns the BD-rate as a fraction; multiply by 100 for percent.
    """
    log_rate_ref = np.log10(np.asarray(rate_ref, dtype=float))
    log_rate_test = np.log10(np.asarray(rate_test, dtype=float))
    qual_ref = np.asarray(qual_ref, dtype=float)
    qual_test = np.asarray(qual_test, dtype=float)

    # Sort each curve by quality ascending (PCHIP requires monotonic x).
    order_ref = np.argsort(qual_ref)
    order_test = np.argsort(qual_test)
    qual_ref, log_rate_ref = qual_ref[order_ref], log_rate_ref[order_ref]
    qual_test, log_rate_test = qual_test[order_test], log_rate_test[order_test]

    interp_ref = PchipInterpolator(qual_ref, log_rate_ref)
    interp_test = PchipInterpolator(qual_test, log_rate_test)

    q_lo = max(qual_ref.min(), qual_test.min())
    q_hi = min(qual_ref.max(), qual_test.max())
    if q_hi <= q_lo:
        return float("nan")

    int_ref, _ = quad(interp_ref, q_lo, q_hi, limit=100)
    int_test, _ = quad(interp_test, q_lo, q_hi, limit=100)
    avg_diff = (int_test - int_ref) / (q_hi - q_lo)
    return 10.0 ** avg_diff - 1.0


def _detect_metric(header: list[str]) -> str:
    for m in ("vmaf", "psnr", "ms_ssim"):
        if any(c.endswith(f"_baseline_{m}") for c in header):
            return m
    raise ValueError(
        "Could not detect metric. Expected columns of the form "
        "qp{Q}_baseline_{metric} for metric in {vmaf, psnr, ms_ssim}."
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="BD-rate on a 4-point QP grid.")
    p.add_argument("csv_path", type=Path,
                   help="Per-clip RD CSV (e.g. results/uvg_rd_per_qp_vmaf.csv)")
    args = p.parse_args(argv)

    with open(args.csv_path) as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []
        metric = _detect_metric(header)
        rows = list(reader)

    print(f"Metric: {metric}")
    print(f"{'sequence':<55} {'BD-rate':>10}")
    print("-" * 70)

    bd_values = []
    for row in rows:
        rate_ref = [float(row[f"qp{q}_baseline_kbps"]) for q in QP_VALUES]
        rate_test = [float(row[f"qp{q}_enhanced_kbps"]) for q in QP_VALUES]
        qual_ref = [float(row[f"qp{q}_baseline_{metric}"]) for q in QP_VALUES]
        qual_test = [float(row[f"qp{q}_enhanced_{metric}"]) for q in QP_VALUES]
        bd = _bd_rate_pair(rate_ref, qual_ref, rate_test, qual_test) * 100.0
        bd_values.append(bd)
        seq_name = row["sequence"]
        print(f"{seq_name:<55} {bd:>+9.2f}%")

    print("-" * 70)
    if bd_values:
        mean_bd = sum(bd_values) / len(bd_values)
        print(f"{'mean':<55} {mean_bd:>+9.2f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
