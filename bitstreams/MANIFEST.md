# Bitstreams

All 296 encoded `.mp4` bitstreams (56 UVG + 240 MCL-JCV) used to produce the
numbers in `results/` are published as GitHub Release assets:

**[Release v1.0.0 — Tier-1 reproducibility bitstreams](https://github.com/marcoeg/kelvin-benchmark/releases/tag/v1.0.0)**

## Download

Bitstreams are split by dataset × leg × QP across 18 tarballs so each asset
fits comfortably under GitHub's 2 GB per-asset cap.

```bash
REL=https://github.com/marcoeg/kelvin-benchmark/releases/download/v1.0.0
mkdir -p UVG MCLJCV

# UVG: 7 sequences × 2 legs × 4 QPs = 56 mp4
for L in baseline kelvin; do for Q in 22 27 32 37; do
  curl -fLO $REL/uvg-$L-qp$Q.tar
done; done
curl -fLO $REL/summaries-uvg.tar
for f in uvg-*.tar summaries-uvg.tar; do tar -xf "$f" -C UVG/; done

# MCL-JCV: 30 sequences × 2 legs × 4 QPs = 240 mp4
for L in baseline kelvin; do for Q in 22 27 32 37; do
  curl -fLO $REL/mcljcv-$L-qp$Q.tar
done; done
curl -fLO $REL/summaries-mcljcv.tar
for f in mcljcv-*.tar summaries-mcljcv.tar; do tar -xf "$f" -C MCLJCV/; done

# Verify integrity
curl -fLO $REL/MANIFEST.sha256
sha256sum -c MANIFEST.sha256
```

## Asset layout

| Asset | Contents | Size |
|---|---|---:|
| `uvg-baseline-qp{22,27,32,37}.tar`  | 7 baseline mp4 per QP | 21–195 MB |
| `uvg-kelvin-qp{22,27,32,37}.tar`    | 7 Kelvin mp4 per QP   | 22–200 MB |
| `mcljcv-baseline-qp{22,27,32,37}.tar` | 30 baseline mp4 per QP | 34–315 MB |
| `mcljcv-kelvin-qp{22,27,32,37}.tar`   | 30 Kelvin mp4 per QP   | 35–319 MB |
| `summaries-uvg.tar`     | 7 per-clip `*.opt.summary.json`  | 30 KB |
| `summaries-mcljcv.tar`  | 30 per-clip `*.opt.summary.json` | 100 KB |
| `MANIFEST.sha256` | SHA-256 of every extracted artifact | 40 KB |

## File naming (after extraction)

```
<sequence>.opt.<leg>.qp<Q>.mp4
<sequence>.opt.summary.json
```

- `sequence` — e.g. `Beauty_1920x1080_120fps_420_8bit_YUV`, `videoSRC09_1920x1080_25`
- `leg` ∈ {`baseline`, `kelvin`}
- `Q` ∈ {22, 27, 32, 37}

The `*.opt.summary.json` sidecars carry the per-clip RD curves, BD-rate
values, libvmaf log paths, and full provenance (git SHAs, ffmpeg version,
libvmaf model strings, Kelvin checkpoint hash).

## Reproducibility

Tier-1 reproduction does not require re-running Kelvin. Anyone can:

1. Download the Release tarballs.
2. Run libvmaf against the bitstreams using the original UVG / MCL-JCV YUV
   references and the libvmaf config in `configs/libvmaf.json`.
3. Recompute BD-rate via `python scripts/bjontegaard.py results/uvg_rd_per_qp_vmaf.csv` —
   this should print exactly `mean = -27.62%` for UVG.

## Production details

- **Kelvin v1.0 checkpoint v12** (the same model deployed in EncodeIQ today).
- libx264 preset=medium, threads=1, QP ∈ {22, 27, 32, 37}.
- libvmaf v3 single pass: `vmaf_v0.6.1` + `vmaf_v0.6.1neg` + `psnr` + `float_ms_ssim`.
- Parity harness pinned to `scene-enhance @ bdbee02`.
