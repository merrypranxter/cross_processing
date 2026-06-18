#!/usr/bin/env python3
"""make_gallery — render every preset on a sample scene into gallery/.

Produces gallery/sample_input.png, one render per preset, and a contact sheet.
Run from the repo root:  python tools/make_gallery.py
"""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np

import xpro_core as xc

ROOT = Path(__file__).resolve().parent.parent
GALLERY = ROOT / "gallery"


def sample_scene(h=360, w=540) -> np.ndarray:
    """A synthetic but photographic-feeling scene: sky gradient, 'ground',
    a sun disc, color patches, and a gray ramp — enough tones to show off the
    tone-dependent cross-process behaviour. No external assets required."""
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    u, v = x / (w - 1), y / (h - 1)

    # Sky: cool top to warm horizon.
    sky = np.stack([0.35 + 0.5 * v, 0.45 + 0.35 * v, 0.75 - 0.2 * v], -1)
    # Ground: warm, darkening downward.
    ground = np.stack([0.45 - 0.2 * (v - 0.6), 0.32 - 0.15 * (v - 0.6),
                       0.18 - 0.1 * (v - 0.6)], -1)
    horizon = 0.6
    img = np.where((v < horizon)[..., None], sky, ground)

    # Sun.
    d = np.sqrt((u - 0.72) ** 2 + ((v - 0.32) * (w / h)) ** 2)
    sun = np.clip(1.0 - d * 6.0, 0.0, 1.0)[..., None]
    img = img + sun * np.array([1.0, 0.95, 0.8]) * 0.9

    # Color patches (skin-ish, foliage, denim, neutral) along the bottom.
    patches = [(0.10, [0.80, 0.55, 0.45]), (0.32, [0.20, 0.45, 0.20]),
               (0.54, [0.20, 0.30, 0.60]), (0.76, [0.85, 0.85, 0.85])]
    for cx, col in patches:
        mask = (np.abs(u - cx) < 0.07) & (np.abs(v - 0.80) < 0.08)
        img[mask] = col

    # Gray ramp strip at the very bottom.
    ramp = (v > 0.92)
    img[ramp] = np.repeat(u[ramp][:, None], 3, axis=1)

    return np.clip(img, 0.0, 1.0)


def contact_sheet(images, labels, cols=3, pad=8):
    rows = (len(images) + cols - 1) // cols
    h, w = images[0].shape[:2]
    sheet = np.ones((rows * h + (rows + 1) * pad,
                     cols * w + (cols + 1) * pad, 3), np.float32)
    for i, im in enumerate(images):
        r, c = divmod(i, cols)
        y0 = pad + r * (h + pad)
        x0 = pad + c * (w + pad)
        sheet[y0:y0 + h, x0:x0 + w] = im
    return sheet


def main():
    GALLERY.mkdir(exist_ok=True)
    scene = sample_scene()
    xc.save_image(GALLERY / "sample_input.png", scene)

    images, labels = [scene], ["input"]
    for name in xc.list_presets():
        out = xc.apply_profile(scene, xc.PRESETS[name], seed=7)
        xc.save_image(GALLERY / f"{name}.png", out)
        images.append(out)
        labels.append(name)
        print(f"rendered {name}")

    sheet = contact_sheet(images, labels, cols=3)
    xc.save_image(GALLERY / "contact_sheet.png", sheet)
    print(f"wrote {GALLERY/'contact_sheet.png'}")


if __name__ == "__main__":
    main()
