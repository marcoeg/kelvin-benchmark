# Attributions

This benchmark uses two publicly distributed video datasets. Neither dataset is
redistributed in this repository — users are expected to download the original
YUVs from the dataset authors and run the harness against them locally. The
results published here (CSV tables, plots, and forthcoming bitstreams) are
derivative quality measurements, not redistributions of the source video.

---

## UVG — Ultra Video Group test sequences

- **Authors:** Ultra Video Group, Tampere University, Finland.
- **Source:** <http://ultravideo.fi/>
- **License:** Creative Commons Attribution-NonCommercial 3.0
  (CC BY-NC 3.0). <https://creativecommons.org/licenses/by-nc/3.0/>
- **Sequences used (7):** Beauty, Bosphorus, HoneyBee, Jockey,
  ReadySteadyGo, ShakeNDry, YachtRide. All 1920×1080 @ 120 fps,
  8-bit 4:2:0 YUV.

The published per-sequence and aggregate measurements in
`results/uvg_*.csv` and the rendered plots in `plots/uvg_*.png` are
derivative quality measurements. The original YUV sequences are not
included in this repository. Use of the UVG sequences is subject to
CC BY-NC 3.0; this benchmark is published for research and
non-commercial evaluation purposes.

If you use UVG in your own work, cite the dataset authors as
instructed on the UVG website.

---

## MCL-JCV — University of Southern California, Media Communications Lab

- **Authors:** Haiqiang Wang, Ioannis Katsavounidis, Jiantong Zhou,
  Jeonghoon Park, Shawmin Lei, Xin Zhou, Man-On Pun, Xin Jin,
  Ronggang Wang, Xu Wang, Yun Zhang, Jiwu Huang, Sam Kwong, C.-C. Jay Kuo.
- **Paper:** Wang et al., *"MCL-JCV: a JND-based H.264/AVC video quality
  assessment dataset,"* Proceedings of IEEE International Conference
  on Image Processing (ICIP), 2016.
- **Source:** <https://mcl.usc.edu/mcl-jcv-dataset/> and the
  Hugging Face mirror at
  <https://huggingface.co/datasets/uscmcl/MCL-JCV_Dataset>
- **Terms:** academic / research use, as specified by USC MCL on
  the dataset page. See the original dataset page for current terms.
- **Sequences used:** all 30 sequences (videoSRC01 through videoSRC30).

The per-clip table in `results/mcljcv_summary.csv` and the scatter plot
in `plots/mcljcv_scatter_bdvmaf_vs_bdvmafneg.png` are derivative quality
measurements. The original MP4/YUV sequences are not included in this
repository.

If you use MCL-JCV in your own work, cite Wang et al. 2016 as above.

---

## Tooling

- **FFmpeg / libx264** — <https://ffmpeg.org/>, <https://www.videolan.org/developers/x264.html>
- **libvmaf v3** — Netflix, <https://github.com/Netflix/vmaf>,
  models `vmaf_v0.6.1` and `vmaf_v0.6.1neg`.
- **SciPy** PCHIP and adaptive quadrature for BD-rate.
- **matplotlib** for plot rendering.
