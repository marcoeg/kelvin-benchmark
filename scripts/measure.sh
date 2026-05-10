#!/usr/bin/env bash
# measure.sh -- Run libvmaf on (reference YUV, distorted MP4) pairs.
#
# Anyone can use this script to verify that the published Kelvin
# bitstreams hit the published quality numbers, by running libvmaf
# against the original UVG / MCL-JCV reference YUVs.
#
# Usage:
#   ./scripts/measure.sh <reference.yuv> <distorted.mp4> <width> <height> <fps> <out.json>
#
# Example:
#   ./scripts/measure.sh \
#       /data/uvg/Beauty_1920x1080_120fps_420_8bit_YUV.yuv \
#       /data/kelvin-bitstreams/kelvin/Beauty_qp22.mp4 \
#       1920 1080 120 \
#       /tmp/Beauty_qp22.json
#
# Output:
#   A libvmaf JSON log with VMAF (vmaf_v0.6.1), VMAF-NEG, PSNR-Y, and
#   MS-SSIM per frame plus aggregates. Cross-check the aggregates
#   against results/uvg_rd_per_qp_vmaf.csv.
#
# Requirements:
#   - ffmpeg built with --enable-libvmaf (libvmaf >= v3)
#   - vmaf_v0.6.1 + vmaf_v0.6.1neg model files installed via libvmaf
#
set -euo pipefail

if [[ $# -ne 6 ]]; then
    sed -n '2,21p' "$0"
    exit 1
fi

REFERENCE="$1"
DISTORTED="$2"
WIDTH="$3"
HEIGHT="$4"
FPS="$5"
OUTPUT_JSON="$6"

# Escape colons in libvmaf filter argument list; this matches the exact
# invocation used by the private Kelvin evaluator.
LIBVMAF_FILTER="libvmaf=model='version=vmaf_v0.6.1\\:name=vmaf|version=vmaf_v0.6.1neg\\:name=vmaf_neg':feature='name=psnr|name=float_ms_ssim':log_path=${OUTPUT_JSON}:log_fmt=json"

ffmpeg -y \
    -f rawvideo -pix_fmt yuv420p -s "${WIDTH}x${HEIGHT}" -r "${FPS}" -i "${REFERENCE}" \
    -i "${DISTORTED}" \
    -lavfi "[0:v][1:v]${LIBVMAF_FILTER}" \
    -f null - \
    -v error

echo "Wrote ${OUTPUT_JSON}"
