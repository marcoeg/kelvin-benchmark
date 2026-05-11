# kelvin-benchmark

[![Release](https://img.shields.io/github/v/release/marcoeg/kelvin-benchmark?label=bitstreams&color=blue)](https://github.com/marcoeg/kelvin-benchmark/releases/tag/v1.0.0) [![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Public, reproducible H.264 R-D benchmark for **Kelvin v1.0** — a neural pre-encoder that runs once before `libx264` and reduces bitrate at matched perceptual quality.

> **What this repo is:** the measurement harness, configs, raw CSV outputs, plots, and the [296 encoded `.mp4` bitstreams](https://github.com/marcoeg/kelvin-benchmark/releases/tag/v1.0.0) that produced them. Anyone can re-run libvmaf against the published bitstreams and reproduce every number to within rounding.
>
> **What this repo is *not*:** the Kelvin encoder itself. Kelvin is closed source. It runs inside the [EncodeIQ](https://www.encodeiq.ai) cloud service (Graziano Labs Corp.). The artifacts here are the *outputs* of running EncodeIQ in **Mode C** (preprocessing-only) on UVG and MCL-JCV, then encoding the preprocessed sequences with stock `libx264`.
>
> **Checkpoint:** all numbers below are produced by **Kelvin v1.0 checkpoint v12**, the model currently deployed in production EncodeIQ. Tier-2 customers running the EncodeIQ API today get this same model; the published numbers are what you actually get.

---

## Headline numbers

| Dataset                                  | n  | BD-VMAF (mean) | BD-VMAF-NEG (mean) | BD-PSNR-Y (mean) |
| ---------------------------------------- | :- | -------------: | -----------------: | ---------------: |
| UVG (1080p)                              | 7  | **−27.62%**    | **−5.18%**         | **+21.38%**      |
| MCL-JCV (full)                           | 30 | −16.83%        | +4.42%             | +24.86%          |
| MCL-JCV (excl. 2 named regressions)      | 28 | **−27.70%**    | **−5.37%**         | +20.56%          |
| MCL-JCV (excl. 3 outliers, old set)      | 27 | −26.65%        | −5.08%             | +18.38%          |

All three columns are BD-rate values (rate-axis Bjøntegaard delta) under their respective metric. Negative = bitrate saved at matched quality. The positive BD-PSNR-Y column reflects rate spent on perceptual content that PSNR cannot see, not a quality regression — see the per-sequence section below.

---

## Bitstreams

All 296 encoded `.mp4` bitstreams (56 UVG + 240 MCL-JCV) plus per-clip `*.opt.summary.json` sidecars and a SHA-256 manifest are published as GitHub Release assets:

**[Release v1.0.0 — Tier-1 reproducibility bitstreams](https://github.com/marcoeg/kelvin-benchmark/releases/tag/v1.0.0)**

```bash
REL=https://github.com/marcoeg/kelvin-benchmark/releases/download/v1.0.0
mkdir -p UVG MCLJCV

# UVG — 56 mp4
for L in baseline kelvin; do for Q in 22 27 32 37; do
  curl -fLO $REL/uvg-$L-qp$Q.tar
done; done
curl -fLO $REL/summaries-uvg.tar
for f in uvg-*.tar summaries-uvg.tar; do tar -xf "$f" -C UVG/; done

# MCL-JCV — 240 mp4
for L in baseline kelvin; do for Q in 22 27 32 37; do
  curl -fLO $REL/mcljcv-$L-qp$Q.tar
done; done
curl -fLO $REL/summaries-mcljcv.tar
for f in mcljcv-*.tar summaries-mcljcv.tar; do tar -xf "$f" -C MCLJCV/; done

# Verify integrity
curl -fLO $REL/MANIFEST.sha256
sha256sum -c MANIFEST.sha256
```

Full asset table and naming convention: [`bitstreams/MANIFEST.md`](bitstreams/MANIFEST.md).

UVG cleanly delivers **−27.62% mean BD-VMAF, 7/7 wins**, and **−5.18% under VMAF-NEG (6/7)** — the gain holds under the gaming-resistant model.

MCL-JCV at n=30 looks softer (−16.83%) only because two clips dominate the mean (one is a +212% rate-floor pathology; one is a known distribution-shift failure). With those two true regressions removed, n=28 mean BD-VMAF is **−27.70%** with **−5.37%** under VMAF-NEG — consistent with UVG.

---

## What Kelvin is, in one paragraph

Kelvin v1.0 is a learned preprocessor. Input: a raw or near-raw master (8-bit 4:2:0 YUV, or ProRes 422). Output: a perceptually-equivalent YUV that compresses better with stock `libx264`. It is **not** a new codec. It does not change bitstream syntax, decoders, or players. The downstream encoder is stock `libx264 preset=medium`. **H.264 only at this time** — no x265, no SVT-AV1.

---

## Methodology

**Encoder (identical for both legs of every comparison):**

```
ffmpeg -y \
  -f rawvideo -pix_fmt yuv420p -s WxH -r FPS -i <yuv> \
  -c:v libx264 -qp <Q> -preset medium -pix_fmt yuv420p \
  -an -threads 1 -v error \
  <output>.mp4
```

QP grid: `{22, 27, 32, 37}`. `threads=1` is required for run-to-run bit-exact reproducibility. Constant-QP is used (not CRF) so the 4-point R-D curve is on a fixed quality grid.

**Metrics:** single `libvmaf` v3 pass per (reference, distorted) pair, four metrics extracted simultaneously:

```
[0:v][1:v]libvmaf=
  model='version=vmaf_v0.6.1\:name=vmaf|version=vmaf_v0.6.1neg\:name=vmaf_neg':
  feature='name=psnr|name=float_ms_ssim':
  log_path=<out>.json:log_fmt=json
```

Reference is the original raw YUV; distorted is the decoded MP4.

**BD-rate:** PCHIP fit through 4 RD points + Bjøntegaard delta integrated with `scipy.integrate.quad`. Arithmetic mean across sequences. See [`scripts/bjontegaard.py`](scripts/bjontegaard.py).

**Two legs per sequence:**

1. *Baseline:* `original.yuv → libx264 → mp4`
2. *Kelvin:* `original.yuv → EncodeIQ Mode C → preprocessed.yuv → libx264 → mp4`

Both are decoded back to YUV and scored against the **original** raw YUV. Identical encoder, identical metric pass, identical reference. The only variable is the preprocessor.

---

## UVG — 1080p, the canonical dataset

7 sequences, 1920×1080 @ 120 fps, CC BY-NC 3.0.

| Sequence       | BD-VMAF | BD-VMAF-NEG | BD-PSNR-Y | BD-MS-SSIM |
| -------------- | ------: | ----------: | --------: | ---------: |
| Beauty         | −39.83% |      −9.84% |   +39.20% |    +20.00% |
| Bosphorus      | −27.20% |      −6.52% |   +15.58% |     +5.15% |
| HoneyBee       | −33.67% |      +2.69% |   +35.29% |    +22.59% |
| Jockey         | −20.83% |      −5.69% |   +20.38% |    +10.75% |
| ReadySteadyGo  | −16.40% |      −4.57% |   +10.61% |     +3.65% |
| ShakeNDry      | −28.14% |      −4.62% |   +17.78% |     +6.63% |
| YachtRide      | −27.31% |      −7.69% |   +10.80% |     +2.11% |
| **mean (n=7)** | **−27.62%** | **−5.18%** | **+21.38%** | **+10.13%** |

**7/7 wins on BD-VMAF; 6/7 wins on BD-VMAF-NEG.** The gain ranges from −16.4% on the highest-motion clip (ReadySteadyGo) to −39.8% on Beauty. The single positive BD-VMAF-NEG (HoneyBee +2.69%) is small and surrounded by very large gains on the standard model; it does not look like model gaming. The BD-PSNR-Y column is positive on all 7 clips (mean +21.38%) — that is the expected signature of a perceptual preprocessor, which trades pixel fidelity for VMAF, not a regression.

R-D plots: [`plots/uvg_rd_combined_vmaf.png`](plots/uvg_rd_combined_vmaf.png), per-sequence [`plots/uvg_rd_per_sequence_vmaf.png`](plots/uvg_rd_per_sequence_vmaf.png). PSNR and MS-SSIM variants alongside in `plots/`.

---

## MCL-JCV — 30 short clips, harder coverage

USC MCL-JCV, 30 sequences, mixed resolutions and frame rates. This is the dataset that exposes failure modes.

**n=30:** mean BD-VMAF **−16.83%**, median **−25.39%**, **28/30 wins**.

The mean-vs-median gap is the entire story. Two clips are the only true regressions and they're large. Once you remove them the dataset looks like UVG.

| MCL-JCV slice                            | n  | BD-VMAF | BD-VMAF-NEG | BD-PSNR-Y |
| ---------------------------------------- | :- | ------: | ----------: | --------: |
| All clips                                | 30 | −16.83% |      +4.42% |   +24.86% |
| Excl. videoSRC09, videoSRC13 (regressions) | 28 | **−27.70%** | **−5.37%** | +20.56% |
| Excl. videoSRC09, videoSRC13, videoSRC29 | 27 | −26.65% |      −5.08% |   +18.38% |
| Median (all)                             | 30 | −25.39% |      −5.64% |   +15.60% |

The n=28 BD-VMAF-NEG row is the load-bearing number: VMAF-NEG is the gaming-resistant model, designed to penalize preprocessing tricks. **−5.37% under VMAF-NEG with 24/28 wins** means the saving is not a perceptual artifact of standard VMAF.

Scatter: [`plots/mcljcv_scatter_bdvmaf_vs_bdvmafneg.png`](plots/mcljcv_scatter_bdvmaf_vs_bdvmafneg.png).

### The 2 named failures (do not skip this section)

1. **`videoSRC13` — rate-floor violation.** Smooth sky-and-clouds. The clip is so flat that `libx264` baseline is already at the codec's rate floor. Kelvin spends bits to add detail the encoder then has to encode. **BD-VMAF +212.23%**, BD-VMAF-NEG +211.35%. This is a known v1 limitation: Kelvin lacks an explicit floor-detection branch.
2. **`videoSRC09` — distribution shift.** Saturated red tulips, near-monochrome chroma planes outside the training distribution. **BD-VMAF +58.48%**, BD-VMAF-NEG +71.61%. Diagnosed but not yet fixed in v1.

### Why we kept videoSRC29 in the n=28 cut

`videoSRC29` is a low-light cinematic clip where Kelvin reads BD-VMAF **−56.09%** (best in the dataset). On the older v13b_prime checkpoint we excluded it as "metric saturation" — baseline VMAF was high enough that the integration window squeezed against the 100-cap and the magnitude was overstated. Under the v12 production path it shows BD-VMAF-NEG **−13.33%** and BD-PSNR-Y **+79.40%**, so the underlying gain is real and large. We now report it in the canonical n=28 cut and only exclude the two true regressions. The n=27 cut is retained for compatibility with prior reporting.

Per-clip table with `outlier_class` column: [`results/mcljcv_summary.csv`](results/mcljcv_summary.csv).

---

## What's reproducible and what isn't

**Tier 1 — full Bjøntegaard reproduction (anyone, ~30 min):**
Take the [published encoded `.mp4` bitstreams](https://github.com/marcoeg/kelvin-benchmark/releases/tag/v1.0.0), the original UVG / MCL-JCV YUVs (you supply), the libvmaf invocation in [`configs/libvmaf.json`](configs/libvmaf.json), and [`scripts/bjontegaard.py`](scripts/bjontegaard.py). You get bit-exact the same VMAF / VMAF-NEG / PSNR / MS-SSIM scores and BD-rate values to within rounding. The four CSVs in `results/` are pre-computed for convenience.

To verify the BD-rate computation reproduces the published mean:

```
python scripts/bjontegaard.py results/uvg_rd_per_qp_vmaf.csv
# prints per-sequence BD-VMAF and mean = -27.62%
```

**Tier 2 — running Kelvin on your own clips (paid pilot):**
Kelvin is closed source and runs only inside EncodeIQ. To run Mode C on your own masters and reproduce the *preprocessing* step end-to-end, contact `marco@grazianolabs.com` for a pilot account. EncodeIQ exposes a JSON-over-HTTPS API; pilots return the preprocessed YUV (or, in Modes A/B, an encoded stream + ABR ladder).

**Not in this repo:** the Kelvin model weights, network architecture, training data, or training code. Those remain proprietary to Graziano Labs Corp.

---

## Repository layout

```
kelvin-benchmark/
├── README.md                    # this file
├── LICENSE                      # MIT, covers the harness in this repo only
├── ATTRIBUTIONS.md              # UVG and MCL-JCV dataset terms
├── configs/
│   ├── x264_qp22.json           # canonical libx264 invocation (one per QP, identical otherwise)
│   ├── qp_grid.json             # the 4-point QP grid + Bjøntegaard rationale
│   └── libvmaf.json             # the single-pass libvmaf v3 filter (vmaf + vmaf_neg + psnr + ms_ssim)
├── scripts/
│   ├── bjontegaard.py           # 4-point PCHIP BD-rate (verified against published numbers)
│   ├── measure.sh               # libvmaf invocation wrapper
│   ├── plot_rd.py               # per-sequence + combined RD plots, all three metrics
│   └── plot_mcljcv_scatter.py   # BD-VMAF vs BD-VMAF-NEG scatter, outliers labeled
├── results/
│   ├── uvg_summary.csv          # 7 UVG sequences + mean
│   ├── uvg_rd_per_qp_vmaf.csv   # full RD table for BD-VMAF reproduction
│   ├── uvg_rd_per_qp_psnr.csv
│   ├── uvg_rd_per_qp_ms_ssim.csv
│   └── mcljcv_summary.csv       # 30 clips + outlier_class column + n=30/n=28/n=27/median rows
├── plots/                       # PNGs regenerated from results/ via scripts/
└── bitstreams/
    └── MANIFEST.md              # download instructions; the 296 .mp4 + SHA-256 manifest are GitHub Release v1.0.0 assets
```

---

## Citation

```
@misc{graziano2026kelvin,
  author = {Marco Graziano},
  title  = {Kelvin v1.0: a neural pre-encoder for H.264 — public benchmark},
  year   = {2026},
  url    = {https://github.com/marcoeg/kelvin-benchmark}
}
```

Companion writeup: [Inside Kelvin v1.0](https://medium.com/@marcoeg/inside-kelvin-v1-0-a-neural-pre-encoder-for-h-264-3ce719f3e60b).

---

## Contact

Marco Graziano — `marco@grazianolabs.com` — [Graziano Labs Corp.](https://www.encodeiq.ai)

---

© 2026 Graziano Labs Corp. — harness, configs, scripts, and CSVs released under [MIT](LICENSE). Kelvin model weights and code are proprietary.
