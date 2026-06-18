#!/usr/bin/env python3
"""xpro_lut_applier — apply a cross-processing 3D LUT to an image.

Supports Adobe .cube LUTs and the built-in parametric presets (baked to a LUT
on the fly). Can also export the LUT as a tiled PNG for the WebGL viewer.

Examples
--------
    # Apply a preset at 80% strength
    python tools/xpro_lut_applier.py in.jpg out.jpg --preset c41_in_e6 --amount 0.8

    # Apply an external .cube LUT
    python tools/xpro_lut_applier.py in.jpg out.jpg --cube looks/myxpro.cube

    # Bake a preset to a .cube and a tiled PNG (no input image needed)
    python tools/xpro_lut_applier.py --preset push_xpro --export-cube push.cube \
        --export-tiled push_lut.png
"""
from __future__ import annotations

import argparse
import sys

import numpy as np

import xpro_core as xc


def build_table(args) -> np.ndarray:
    if args.cube:
        table, _ = xc.read_cube(args.cube)
        return table
    if args.preset:
        if args.preset not in xc.PRESETS:
            sys.exit(f"Unknown preset '{args.preset}'. Choose from: {xc.list_presets()}")
        return xc.profile_to_cube(xc.PRESETS[args.preset], size=args.size)
    sys.exit("Provide either --cube or --preset.")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", nargs="?", help="input image")
    ap.add_argument("output", nargs="?", help="output image")
    ap.add_argument("--cube", help="path to an Adobe .cube 3D LUT")
    ap.add_argument("--preset", help=f"built-in preset {xc.list_presets()}")
    ap.add_argument("--amount", type=float, default=1.0, help="blend 0..1 (default 1)")
    ap.add_argument("--size", type=int, default=33, help="LUT size when baking a preset")
    ap.add_argument("--export-cube", help="also write the LUT to this .cube path")
    ap.add_argument("--export-tiled", help="also write a tiled PNG LUT for the viewer")
    args = ap.parse_args(argv)

    table = build_table(args)

    if args.export_cube:
        xc.write_cube(args.export_cube, table, title=args.preset or "cross_processing")
        print(f"wrote {args.export_cube}")
    if args.export_tiled:
        # Tiled packing needs a perfect-square size; resample to 64 if needed.
        n = table.shape[0]
        if int(round(n ** 0.5)) ** 2 != n:
            grid = np.linspace(0, 1, 64, dtype=np.float32)
            r, g, b = np.meshgrid(grid, grid, grid, indexing="ij")
            rgb = np.stack([r, g, b], -1)
            table = xc.apply_cube(rgb, table)
        xc.save_image(args.export_tiled, xc.table_to_tiled(table))
        print(f"wrote {args.export_tiled}")

    if args.input:
        if not args.output:
            sys.exit("Provide an output path when an input image is given.")
        img = xc.load_image(args.input)
        graded = xc.apply_cube(img, table)
        out = img * (1.0 - args.amount) + graded * args.amount
        xc.save_image(args.output, out)
        print(f"wrote {args.output} (amount={args.amount})")
    elif not (args.export_cube or args.export_tiled):
        ap.error("Nothing to do: give an input/output image or an --export-* option.")


if __name__ == "__main__":
    main()
