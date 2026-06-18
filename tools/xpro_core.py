"""xpro_core — shared utilities for the cross_processing tools.

Pure-Python + numpy implementation of the cross-processing maths so the CLI
tools, the notebooks, and tests all share one source of truth. Pillow is used
only for image I/O.

The goal is not physical accuracy but a controllable, organic approximation of
what wrong chemistry does to color: tone-dependent channel shifts, distorted
contrast curves, split-toning, and grain.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
import json
from pathlib import Path
from typing import Dict, Tuple

import numpy as np

try:  # Pillow is only needed for image I/O, not for the maths.
    from PIL import Image, ImageOps
except ImportError:  # pragma: no cover
    Image = None
    ImageOps = None


REC709 = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)


# ---------------------------------------------------------------------------
# Image I/O (float RGB in [0, 1], shape HxWx3)
# ---------------------------------------------------------------------------
def load_image(path: str | Path) -> np.ndarray:
    if Image is None:
        raise RuntimeError("Pillow is required for image I/O. pip install Pillow")
    img = Image.open(path)
    img = ImageOps.exif_transpose(img).convert("RGB")  # respect EXIF orientation
    return np.asarray(img, dtype=np.float32) / 255.0


def save_image(path: str | Path, arr: np.ndarray) -> None:
    if Image is None:
        raise RuntimeError("Pillow is required for image I/O. pip install Pillow")
    arr = np.clip(arr, 0.0, 1.0)
    Image.fromarray((arr * 255.0 + 0.5).astype(np.uint8)).save(path)


def luminance(rgb: np.ndarray) -> np.ndarray:
    return rgb @ REC709


# ---------------------------------------------------------------------------
# Tone-dependent transforms
# ---------------------------------------------------------------------------
def smoothstep(edge0: float, edge1: float, x: np.ndarray) -> np.ndarray:
    t = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def s_curve(x: np.ndarray, contrast: float, pivot: float = 0.5) -> np.ndarray:
    """Logistic S-curve normalized to pass through (0,0) and (1,1)."""
    k = max(0.01, contrast)  # avoid div-by-zero (hi-lo -> 0) producing NaNs
    a = 1.0 / (1.0 + np.exp(-k * (x - pivot)))
    lo = 1.0 / (1.0 + np.exp(-k * (0.0 - pivot)))
    hi = 1.0 / (1.0 + np.exp(-k * (1.0 - pivot)))
    return (a - lo) / (hi - lo)


def adjust_saturation(rgb: np.ndarray, sat: float) -> np.ndarray:
    l = luminance(rgb)[..., None]
    return l + (rgb - l) * sat


def add_grain(rgb: np.ndarray, amount: float, size: float = 1.0,
              seed: int = 0, shadow_bias: float = 0.0) -> np.ndarray:
    """Add zero-mean grain. shadow_bias>0 concentrates grain in shadows."""
    if amount <= 0:
        return rgb
    rng = np.random.default_rng(seed)
    h, w = rgb.shape[:2]
    size = max(size, 0.5)  # clamp to avoid div-by-zero / OOM on huge arrays
    size = max(size, 0.5)
    gh, gw = max(1, int(h / size)), max(1, int(w / size))
    noise = rng.standard_normal((gh, gw, 1)).astype(np.float32)
    if (gh, gw) != (h, w):  # nearest-neighbour upscale -> chunky grain
        ys = (np.arange(h) * gh / h).astype(int)
        xs = (np.arange(w) * gw / w).astype(int)
        noise = noise[np.ix_(ys, xs)]
    weight = 1.0
    if shadow_bias:
        weight = 1.0 + shadow_bias * (1.0 - luminance(rgb)[..., None])
    return rgb + noise * amount * weight


# ---------------------------------------------------------------------------
# Cross-processing presets / profiles
# ---------------------------------------------------------------------------
@dataclass
class XproProfile:
    """A parametric description of a cross-processing look.

    shifts are additive RGB offsets applied per tone region; contrast is the
    S-curve steepness; pivot moves the curve's gray point; saturation scales
    chroma; grain_* control the noise.
    """
    name: str = "custom"
    shadow_shift: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    midtone_shift: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    highlight_shift: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    contrast: float = 4.0
    pivot: float = 0.5
    saturation: float = 1.2
    grain_amount: float = 0.04
    grain_size: float = 1.5
    grain_shadow_bias: float = 0.6
    fade: float = 0.0  # 0 = none, lifts blacks toward a faded look

    def to_json(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")

    @classmethod
    def from_json(cls, path: str | Path) -> "XproProfile":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(**data)


def apply_profile(rgb: np.ndarray, p: XproProfile, seed: int = 0) -> np.ndarray:
    out = rgb.astype(np.float32).copy()
    l = luminance(out)

    sh = (1.0 - smoothstep(0.0, 0.5, l))[..., None]
    hi = smoothstep(0.5, 1.0, l)[..., None]
    mid = np.clip(1.0 - sh - hi, 0.0, 1.0)

    shift = (np.array(p.shadow_shift) * sh
             + np.array(p.midtone_shift) * mid
             + np.array(p.highlight_shift) * hi)
    out = out + shift.astype(np.float32)

    out = s_curve(np.clip(out, 0.0, 1.0), p.contrast, p.pivot)
    out = adjust_saturation(out, p.saturation)

    if p.fade > 0:
        out = out * (1.0 - 0.15 * p.fade) + 0.12 * p.fade

    out = add_grain(out, p.grain_amount, p.grain_size, seed, p.grain_shadow_bias)
    return np.clip(out, 0.0, 1.0)


# Built-in presets matching the shader collection.
PRESETS: Dict[str, XproProfile] = {
    "c41_in_e6": XproProfile(
        name="c41_in_e6",
        shadow_shift=(-0.02, 0.10, -0.06),
        midtone_shift=(0.12, -0.04, 0.10),
        highlight_shift=(0.14, 0.10, -0.12),
        contrast=6.0, pivot=0.45, saturation=1.35,
        grain_amount=0.05, grain_size=1.5, grain_shadow_bias=0.8,
    ),
    "e6_in_c41": XproProfile(
        name="e6_in_c41",
        shadow_shift=(-0.06, 0.0, 0.08),
        midtone_shift=(0.10, 0.02, -0.05),
        highlight_shift=(0.08, 0.04, -0.06),
        contrast=2.2, pivot=0.5, saturation=0.78,
        grain_amount=0.02, grain_size=1.2, grain_shadow_bias=0.2, fade=0.7,
    ),
    "push_xpro": XproProfile(
        name="push_xpro",
        shadow_shift=(-0.05, 0.16, -0.04),
        midtone_shift=(0.18, -0.08, 0.16),
        highlight_shift=(0.22, 0.12, -0.16),
        contrast=11.0, pivot=0.42, saturation=1.5,
        grain_amount=0.10, grain_size=2.5, grain_shadow_bias=1.0,
    ),
    "expired_xpro": XproProfile(
        name="expired_xpro",
        shadow_shift=(0.08, -0.06, 0.10),
        midtone_shift=(-0.05, 0.10, -0.08),
        highlight_shift=(0.12, 0.06, 0.04),
        contrast=5.0, pivot=0.5, saturation=1.1,
        grain_amount=0.12, grain_size=3.0, grain_shadow_bias=0.5, fade=0.4,
    ),
    "bw_in_c41": XproProfile(
        name="bw_in_c41",
        shadow_shift=(0.0, 0.0, 0.0),
        midtone_shift=(0.04, 0.0, -0.04),
        highlight_shift=(0.06, 0.02, -0.05),
        contrast=4.0, pivot=0.5, saturation=0.0,  # mono, then tinted
        grain_amount=0.04, grain_size=1.5, grain_shadow_bias=0.4,
    ),
}


def list_presets() -> list[str]:
    return sorted(PRESETS)


# ---------------------------------------------------------------------------
# 3D LUT (.cube) read / write / apply
# ---------------------------------------------------------------------------
def read_cube(path: str | Path) -> Tuple[np.ndarray, np.ndarray]:
    """Read an Adobe .cube 3D LUT. Returns (table NxNxNx3, domain (min,max))."""
    size = None
    dmin = np.zeros(3, np.float32)
    dmax = np.ones(3, np.float32)
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key = line.split()[0].upper()
        if key == "LUT_3D_SIZE":
            size = int(line.split()[1])
        elif key == "DOMAIN_MIN":
            dmin = np.array(line.split()[1:4], np.float32)
        elif key == "DOMAIN_MAX":
            dmax = np.array(line.split()[1:4], np.float32)
        elif key in ("TITLE", "LUT_1D_SIZE"):
            continue
        else:
            parts = line.split()
            if len(parts) == 3:
                rows.append([float(x) for x in parts])
    if size is None:
        raise ValueError("Not a valid 3D .cube file (missing LUT_3D_SIZE)")
    table = np.array(rows, np.float32).reshape(size, size, size, 3)
    # .cube ordering: red fastest. Reshape gives [b, g, r]; transpose to [r,g,b].
    table = table.transpose(2, 1, 0, 3)
    return table, np.stack([dmin, dmax])


def write_cube(path: str | Path, table: np.ndarray, title: str = "cross_processing") -> None:
    n = table.shape[0]
    lines = [f"TITLE \"{title}\"", f"LUT_3D_SIZE {n}", "DOMAIN_MIN 0 0 0", "DOMAIN_MAX 1 1 1"]
    # write with red fastest -> iterate b, g, r
    t = table.transpose(2, 1, 0, 3)  # back to [b,g,r]
    flat = t.reshape(-1, 3)
    for r, g, b in flat:
        lines.append(f"{r:.6f} {g:.6f} {b:.6f}")
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def apply_cube(rgb: np.ndarray, table: np.ndarray) -> np.ndarray:
    """Apply a 3D LUT to an image with trilinear interpolation."""
    n = table.shape[0]
    c = np.clip(rgb, 0.0, 1.0) * (n - 1)
    i0 = np.floor(c).astype(int)
    i1 = np.minimum(i0 + 1, n - 1)
    f = c - i0

    r0, g0, b0 = i0[..., 0], i0[..., 1], i0[..., 2]
    r1, g1, b1 = i1[..., 0], i1[..., 1], i1[..., 2]
    fr, fg, fb = f[..., 0:1], f[..., 1:2], f[..., 2:3]

    def t(ri, gi, bi):
        return table[ri, gi, bi]

    c00 = t(r0, g0, b0) * (1 - fr) + t(r1, g0, b0) * fr
    c01 = t(r0, g0, b1) * (1 - fr) + t(r1, g0, b1) * fr
    c10 = t(r0, g1, b0) * (1 - fr) + t(r1, g1, b0) * fr
    c11 = t(r0, g1, b1) * (1 - fr) + t(r1, g1, b1) * fr
    c0 = c00 * (1 - fg) + c10 * fg
    c1 = c01 * (1 - fg) + c11 * fg
    return c0 * (1 - fb) + c1 * fb


def profile_to_cube(p: XproProfile, size: int = 33) -> np.ndarray:
    """Bake an XproProfile into a 3D LUT table (no grain — LUTs can't carry it)."""
    n = size
    grid = np.linspace(0.0, 1.0, n, dtype=np.float32)
    r, g, b = np.meshgrid(grid, grid, grid, indexing="ij")
    rgb = np.stack([r, g, b], axis=-1).reshape(-1, 1, 3)
    no_grain = XproProfile(**{**asdict(p), "grain_amount": 0.0})
    out = apply_profile(rgb, no_grain).reshape(n, n, n, 3)
    return out


# ---------------------------------------------------------------------------
# Tiled-grid (Hald) LUT PNG <-> 3D table, for the WebGL viewer
# ---------------------------------------------------------------------------
def table_to_tiled(table: np.ndarray) -> np.ndarray:
    """Pack an NxNxNx3 table into a tiled 2D image for digital_xpro_lut.frag.

    Layout: tilesPerRow = round(sqrt(N)); each blue slice is an NxN tile of
    (red across x, green down y); tiles fill left-to-right, top-to-bottom.
    """
    n = table.shape[0]
    tpr = int(round(np.sqrt(n)))
    if tpr * tpr != n:
        raise ValueError(f"N={n} must be a perfect square for tiled packing (e.g. 64)")
    size = n * tpr
    out = np.zeros((size, size, 3), np.float32)
    for sl in range(n):  # blue slice
        ty, tx = divmod(sl, tpr)
        # within tile: x=red, y=green
        tile = table[:, :, sl, :].transpose(1, 0, 2)  # [green, red, 3]
        out[ty * n:(ty + 1) * n, tx * n:(tx + 1) * n] = tile
    return out
