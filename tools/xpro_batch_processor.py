#!/usr/bin/env python3
"""xpro_batch_processor — apply a cross-processing look to a folder of images.

Each image can optionally get slightly jittered parameters so a batch looks like
a stack of individually-developed rolls rather than a uniform filter.

Examples
--------
    python tools/xpro_batch_processor.py ./in ./out --preset c41_in_e6
    python tools/xpro_batch_processor.py ./in ./out --preset push_xpro --jitter 0.15
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np

import xpro_core as xc

EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".webp"}


def jittered(profile: xc.XproProfile, amount: float, rng) -> xc.XproProfile:
    """Return a copy of `profile` with small random perturbations."""
    if amount <= 0:
        return profile
    d = asdict(profile)
    for key in ("contrast", "saturation", "grain_amount", "pivot"):
        scale = 1.0 + rng.uniform(-amount, amount)
        d[key] = float(d[key] * scale)
    # nudge each shift triple
    for key in ("shadow_shift", "midtone_shift", "highlight_shift"):
        v = np.array(d[key]) + rng.uniform(-amount * 0.05, amount * 0.05, 3)
        d[key] = tuple(float(x) for x in v)
    return xc.XproProfile(**d)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("indir", help="input folder")
    ap.add_argument("outdir", help="output folder")
    grp = ap.add_mutually_exclusive_group(required=True)
    grp.add_argument("--preset", help=f"built-in preset {xc.list_presets()}")
    grp.add_argument("--profile", help="path to an XproProfile .json")
    grp.add_argument("--cube", help="path to a .cube LUT")
    ap.add_argument("--jitter", type=float, default=0.0,
                    help="per-image parameter jitter 0..1 (ignored for --cube)")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args(argv)

    indir, outdir = Path(args.indir), Path(args.outdir)
    if not indir.is_dir():
        sys.exit(f"Not a directory: {indir}")
    outdir.mkdir(parents=True, exist_ok=True)

    files = sorted(p for p in indir.iterdir() if p.suffix.lower() in EXTS)
    if not files:
        sys.exit(f"No images found in {indir}")

    cube_table = None
    base_profile = None
    if args.cube:
        cube_table, _ = xc.read_cube(args.cube)
    elif args.profile:
        base_profile = xc.XproProfile.from_json(args.profile)
    else:
        if args.preset not in xc.PRESETS:
            sys.exit(f"Unknown preset. Choose from: {xc.list_presets()}")
        base_profile = xc.PRESETS[args.preset]

    rng = np.random.default_rng(args.seed)
    for i, f in enumerate(files):
        img = xc.load_image(f)
        if cube_table is not None:
            out = xc.apply_cube(img, cube_table)
        else:
            prof = jittered(base_profile, args.jitter, rng)
            out = xc.apply_profile(img, prof, seed=args.seed + i)
        dst = outdir / f.name
        xc.save_image(dst, out)
        print(f"[{i + 1}/{len(files)}] {f.name} -> {dst}")

    print(f"done: {len(files)} images -> {outdir}")


if __name__ == "__main__":
    main()
