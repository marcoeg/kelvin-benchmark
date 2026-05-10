# kelvin-benchmark

Public, reproducible H.264 R-D benchmark for **Kelvin v1.0** — a neural pre-encoder that runs once before `libx264` and reduces bitrate at matched perceptual quality.

> **What this repo is:** the measurement harness, configs, raw CSV outputs, plots, and (later) the encoded `.mp4` bitstreams that produced them. Anyone can re-run libvmaf against the published bitstreams and reproduce every number to within rounding.
>
> **What this repo is *not*:** the Kelvin encoder itself. Kelvin is closed source. It runs inside the [EncodeIQ](https://www.encodeiq.ai) cloud service (Graziano Labs Corp.). The artifacts here are the *outputs* of running EncodeIQ in **Mode C** (preprocessing-only) on UVG and MCL-JCV, then encoding the preprocessed sequences with stock `libx264`.

---

## Headline numbers

| Dataset                          | n  | BD-VMAF (mean) | BD-VMAF-NEG (mean) | BD-PSNR-Y (mean) |
| -------------------------------- | :- | -------------: | -----------------: | ---------------: |
| UVG (1080p)                      | 7  | **−20.23%**    | —                  | **+27.38%**      |
| MCL-JCV (full)                   | 30 | **−12.80%**    | +5.21%             | +39.50%          |
| MCL-JCV (excl. 3 named outliers) | 27 | **−20.50%**    | **−2.01%**         | +35.75%          |

Negative BD-rate = bitrate saved at matched quality. Positive BD-quality = quality gained at matched bitrate. Both are conventional Bjøntegaard-delta values.

The MCL-JCV n=30 row is honest but misleading: three clips dominate the mean (one is a +153% rate-floor pathology). After excluding those three with documented failure modes (see below), the n=27 mean is consistent with UVG and the gain holds under the gaming-resistant `vmaf_v0.6.1neg` model.

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

| Sequence       | BD-VMAF | BD-PSNR-Y | BD-MS-SSIM |
| -------------- | ------: | --------: | ---------: |
| Beauty         |  −26.13% |   +28.87% |     −6.94% |
| Bosphorus      |  −24.50% |   +22.17% |     +2.83% |
| HoneyBee       |  −35.83% |   +36.20% |    +11.92% |
| Jockey         |  −12.26% |   +28.67% |     +3.20% |
| ReadySteadyGo  |   −8.54% |   +21.25% |     +3.49% |
| ShakeNDry      |  −20.80% |   +29.28% |     +5.26% |
| YachtRide      |  −13.58% |   +25.21% |     +3.18% |
| **mean (n=7)** | **−20.23%** | **+27.38%** | **+3.28%** |

7/7 wins on BD-VMAF; 7/7 wins on BD-PSNR-Y. The gain ranges from ~−9% on the highest-motion clip (ReadySteadyGo) to ~−36% on a smooth high-detail clip (HoneyBee).

R-D plots: [`plots/uvg_rd_combined_vmaf.png`](plots/uvg_rd_combined_vmaf.png), per-sequence [`plots/uvg_rd_per_sequence_vmaf.png`](plots/uvg_rd_per_sequence_vmaf.png). PSNR and MS-SSIM variants alongside in `plots/`.

---

## MCL-JCV — 30 short clips, harder coverage

USC MCL-JCV, 30 sequences, mixed resolutions and frame rates. This is the dataset that exposes failure modes.

**n=30:** mean BD-VMAF −12.80%, median −17.75%, **28/30 wins**.

Two clips are outliers in opposite directions (huge regression on `videoSRC13`, huge gain on `videoSRC29`). A third (`videoSRC09`) is a smaller but real regression. With those three removed the dataset behaves like UVG:

| MCL-JCV slice                         | n  | BD-VMAF | BD-VMAF-NEG | BD-PSNR-Y |
| ------------------------------------- | :- | ------: | ----------: | --------: |
| All clips                             | 30 | −12.80% |      +5.21% |   +39.50% |
| Excl. videoSRC09, videoSRC13, videoSRC29 | 27 | **−20.50%** | **−2.01%** | +35.75% |
| Median (all)                          | 30 | −17.75% |      −3.63% |   +25.75% |

The n=27 BD-VMAF-NEG row is the load-bearing number: VMAF-NEG is the gaming-resistant model, designed to penalize preprocessing tricks. A negative value here means the saving is not a perceptual artifact of standard VMAF.

Scatter: [`plots/mcljcv_scatter_bdvmaf_vs_bdvmafneg.png`](plots/mcljcv_scatter_bdvmaf_vs_bdvmafneg.png).

### The 3 named failures (do not skip this section)

1. **`videoSRC13` — rate-floor violation.** Smooth sky-and-clouds. The clip is so flat that `libx264` baseline is already at the codec's rate floor. Kelvin spends bits to add detail the encoder then has to encode. BD-VMAF +152.83%. This is a known v1 limitation: Kelvin lacks an explicit floor-detection branch.
2. **`videoSRC09` — distribution shift.** Saturated red tulips, near-monochrome chroma planes outside the training distribution. BD-VMAF +68.63%. Diagnosed but not yet fixed in v1.
3. **`videoSRC29` — metric saturation.** Low-light cinematic, baseline VMAF already near 100. BD-VMAF reads −52.14% but the integration window is squeezed against the 100-cap; the underlying pixel-level gain is real but the magnitude is over-stated. This is a measurement artefact, not a model failure — included here for transparency, not as a brag.

Per-clip table with `outlier_class` column: [`results/mcljcv_summary.csv`](results/mcljcv_summary.csv).

---

## What's reproducible and what isn't

**Tier 1 — full Bjøntegaard reproduction (anyone, ~30 min):**
Take the published encoded `.mp4` bitstreams (forthcoming as a GitHub Release on this repo), the original UVG / MCL-JCV YUVs (you supply), the libvmaf invocation in [`configs/libvmaf.json`](configs/libvmaf.json), and [`scripts/bjontegaard.py`](scripts/bjontegaard.py). You get bit-exact the same VMAF / PSNR / MS-SSIM scores and BD-rate values to within rounding. The four CSVs in `results/` are pre-computed for convenience.

To verify the BD-rate computation reproduces the published mean:

```
python scripts/bjontegaard.py results/uvg_rd_per_qp_vmaf.csv
# prints per-sequence BD-VMAF and mean = -20.23%
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
│   └── mcljcv_summary.csv       # 30 clips + outlier_class column + n=30/n=27/median rows
├── plots/                       # PNGs regenerated from results/ via scripts/
├── docs/
└── bitstreams/                  # MANIFEST + (eventually) GitHub Release attachments
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
