#!/usr/bin/env python3
"""xpro_profile_extractor — estimate a cross-processing profile from a scan.

Two modes:

1. Paired (best): give a "normal" reference and the cross-processed version of
   the same frame. The tool measures the per-tone color shift, contrast change,
   and saturation change directly.

2. Single (heuristic): give only a cross-processed scan. The tool estimates the
   color cast in shadows / midtones / highlights relative to neutral gray and a
   global contrast/saturation guess.

Output is an XproProfile .json usable by the other tools and notebooks.

Examples
--------
    python tools/xpro_profile_extractor.py scan_xpro.jpg profile.json
    python tools/xpro_profile_extractor.py scan_xpro.jpg profile.json --reference normal.jpg
"""
from __future__ import annotations

import argparse

import numpy as np

import xpro_core as xc


def _region_means(rgb: np.ndarray):
    l = xc.luminance(rgb)
    sh = l < 0.33
    hi = l > 0.66
    mid = ~sh & ~hi
    def mean(mask):
        return rgb[mask].mean(axis=0) if mask.any() else np.zeros(3, np.float32)
    return mean(sh), mean(mid), mean(hi), (sh, mid, hi)


def extract_single(xpro: np.ndarray, name: str) -> xc.XproProfile:
    flat = xpro.reshape(-1, 3)
    sh, mid, hi, _ = _region_means(flat)
    # Shift = color minus its own luminance (deviation from neutral gray).
    def cast(m):
        return tuple(float(x) for x in (m - m.mean()))
    sat = float((flat.std(axis=0).mean()) /
                (xc.luminance(flat).std() + 1e-5))
    contrast = float(np.clip(4.0 + 8.0 * (xc.luminance(flat).std() - 0.2), 1.5, 12.0))
    return xc.XproProfile(
        name=name,
        shadow_shift=cast(sh), midtone_shift=cast(mid), highlight_shift=cast(hi),
        contrast=contrast, pivot=0.5, saturation=float(np.clip(sat, 0.3, 1.8)),
        grain_amount=0.04,
    )


def extract_paired(normal: np.ndarray, xpro: np.ndarray, name: str) -> xc.XproProfile:
    if normal.shape != xpro.shape:
        # resize xpro to normal via simple nearest sampling
        h, w = normal.shape[:2]
        ys = (np.arange(h) * xpro.shape[0] / h).astype(int)
        xs = (np.arange(w) * xpro.shape[1] / w).astype(int)
        xpro = xpro[np.ix_(ys, xs)]
    nf, xf = normal.reshape(-1, 3), xpro.reshape(-1, 3)
    ln = xc.luminance(nf)
    sh, mid, hi = ln < 0.33, (ln >= 0.33) & (ln <= 0.66), ln > 0.66

    def diff(mask):
        if not mask.any():
            return (0.0, 0.0, 0.0)
        d = (xf[mask] - nf[mask]).mean(axis=0)
        return tuple(float(x) for x in d)

    # Contrast change estimated from std ratio of luminance.
    lx = xc.luminance(xf)
    contrast = float(np.clip(4.0 * (lx.std() / (ln.std() + 1e-5)), 1.5, 14.0))
    sat = float(np.clip(
        (xf.std(axis=0).mean() / (lx.std() + 1e-5)) /
        (nf.std(axis=0).mean() / (ln.std() + 1e-5) + 1e-5), 0.3, 2.0))

    return xc.XproProfile(
        name=name,
        shadow_shift=diff(sh), midtone_shift=diff(mid), highlight_shift=diff(hi),
        contrast=contrast, pivot=0.5, saturation=sat, grain_amount=0.04,
    )


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scan", help="cross-processed scan")
    ap.add_argument("output", help="output profile .json")
    ap.add_argument("--reference", help="normal version of the same frame (paired mode)")
    ap.add_argument("--name", default="extracted")
    args = ap.parse_args(argv)

    xpro = xc.load_image(args.scan)
    if args.reference:
        normal = xc.load_image(args.reference)
        profile = extract_paired(normal, xpro, args.name)
        mode = "paired"
    else:
        profile = extract_single(xpro, args.name)
        mode = "single/heuristic"

    profile.to_json(args.output)
    print(f"[{mode}] wrote {args.output}")
    print(f"  contrast={profile.contrast:.2f} saturation={profile.saturation:.2f}")
    print(f"  shadow_shift={tuple(round(x, 3) for x in profile.shadow_shift)}")
    print(f"  midtone_shift={tuple(round(x, 3) for x in profile.midtone_shift)}")
    print(f"  highlight_shift={tuple(round(x, 3) for x in profile.highlight_shift)}")


if __name__ == "__main__":
    main()
