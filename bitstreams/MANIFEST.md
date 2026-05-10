# Bitstreams

The encoded `.mp4` bitstreams used to produce the numbers in `results/` will
be uploaded as **GitHub Release attachments** on this repository (they are too
large to track in git). This file is the placeholder manifest.

## Naming convention

```
<dataset>__<sequence>__<leg>__qp<Q>.mp4
```

- `dataset` ∈ {`uvg`, `mcljcv`}
- `sequence` — sequence name, e.g. `Beauty`, `videoSRC09`
- `leg` ∈ {`baseline`, `kelvin`}
- `Q` ∈ {22, 27, 32, 37}

So `uvg__HoneyBee__kelvin__qp27.mp4` is the Kelvin-preprocessed HoneyBee
sequence encoded at QP 27 with the canonical libx264 invocation in
`configs/x264_qp22.json`.

## Expected counts

- UVG: 7 sequences × 2 legs × 4 QPs = **56 bitstreams**
- MCL-JCV: 30 sequences × 2 legs × 4 QPs = **240 bitstreams**

## Verifying

Once published, every bitstream should be reproducible bit-exactly from the
corresponding original YUV (UVG / MCL-JCV) plus, for the Kelvin leg, the
EncodeIQ Mode-C output. Tier-1 reproduction does not require re-running
Kelvin: anyone can take the published bitstreams, decode them, run libvmaf
against the original YUV, and reproduce the published BD-rate numbers
exactly via `scripts/bjontegaard.py`.

## Status

⏳ Pending upload as a GitHub Release.
