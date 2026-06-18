#!/usr/bin/env python3
"""split_tone_generator — generate split-tone looks from cross-process data.

Tints shadows and highlights with different colors and a smooth crossover,
mirroring the natural split-tone of cross-processing (cyan shadows, orange
highlights by default). Can apply to an image and/or export the look as a
.cube LUT for use elsewhere.

Examples
--------
    python tools/split_tone_generator.py in.jpg out.jpg
    python tools/split_tone_generator.py in.jpg out.jpg \
        --shadow 0.0,0.55,0.65 --highlight 1.0,0.55,0.15 --balance -0.05
    python tools/split_tone_generator.py --export-cube splittone.cube
"""
from __future__ import annotations

import argparse
import sys

import numpy as np

import xpro_core as xc


def parse_rgb(s: str) -> np.ndarray:
    parts = [float(x) for x in s.split(",")]
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("expected r,g,b (e.g. 0.0,0.55,0.65)")
    return np.array(parts, np.float32)


def split_tone(rgb: np.ndarray, shadow: np.ndarray, highlight: np.ndarray,
               smoothness: float, balance: float) -> np.ndarray:
    l = xc.luminance(rgb)
    split = float(np.clip(0.5 + balance, 0.05, 0.95))
    hi_w = xc.smoothstep(split - smoothness, split + smoothness, l)[..., None]
    sh_w = 1.0 - hi_w

    # soft-light style interaction with luminance
    shadow_tone = rgb * shadow * 2.0
    highlight_tone = 1.0 - (1.0 - rgb) * (1.0 - highlight)
    shadow_tone = rgb + (shadow_tone - rgb) * 0.5
    highlight_tone = rgb + (highlight_tone - rgb) * 0.5

    out = rgb.copy()
    out = out + (shadow_tone - out) * (sh_w * 0.7)
    out = out + (highlight_tone - out) * (hi_w * 0.7)
    return np.clip(out, 0.0, 1.0)


def build_cube(shadow, highlight, smoothness, balance, size=33) -> np.ndarray:
    grid = np.linspace(0, 1, size, dtype=np.float32)
    r, g, b = np.meshgrid(grid, grid, grid, indexing="ij")
    rgb = np.stack([r, g, b], -1)
    return split_tone(rgb, shadow, highlight, smoothness, balance)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", nargs="?")
    ap.add_argument("output", nargs="?")
    ap.add_argument("--shadow", type=parse_rgb, default=parse_rgb("0.0,0.55,0.65"),
                    help="shadow tint r,g,b (default cyan)")
    ap.add_argument("--highlight", type=parse_rgb, default=parse_rgb("1.0,0.55,0.15"),
                    help="highlight tint r,g,b (default orange)")
    ap.add_argument("--smoothness", type=float, default=0.25)
    ap.add_argument("--balance", type=float, default=0.0,
                    help="-0.5..0.5 shifts the shadow/highlight crossover")
    ap.add_argument("--export-cube", help="write the split-tone as a .cube LUT")
    args = ap.parse_args(argv)

    if args.export_cube:
        table = build_cube(args.shadow, args.highlight, args.smoothness, args.balance)
        xc.write_cube(args.export_cube, table, title="split_tone_xpro")
        print(f"wrote {args.export_cube}")

    if args.input:
        if not args.output:
            sys.exit("Provide an output path with an input image.")
        img = xc.load_image(args.input)
        out = split_tone(img, args.shadow, args.highlight, args.smoothness, args.balance)
        xc.save_image(args.output, out)
        print(f"wrote {args.output}")
    elif not args.export_cube:
        ap.error("Give an input/output image or --export-cube.")


if __name__ == "__main__":
    main()
