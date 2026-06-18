"""Tests for tools/xpro_core.py — run with: pytest -q (from repo root)."""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools")))
import xpro_core as xc  # noqa: E402


@pytest.fixture
def img():
    rng = np.random.default_rng(0)
    return rng.random((32, 32, 3)).astype(np.float32)


def test_luminance_gray():
    gray = np.full((4, 4, 3), 0.5, np.float32)
    assert np.allclose(xc.luminance(gray), 0.5)


def test_s_curve_endpoints():
    x = np.array([0.0, 1.0], np.float32)
    y = xc.s_curve(x, 6.0, 0.5)
    assert np.allclose(y, [0.0, 1.0], atol=1e-5)


def test_apply_profile_in_range(img):
    out = xc.apply_profile(img, xc.PRESETS["c41_in_e6"], seed=1)
    assert out.shape == img.shape
    assert out.min() >= 0.0 and out.max() <= 1.0


def test_presets_loadable():
    assert "c41_in_e6" in xc.list_presets()
    for name in xc.list_presets():
        assert isinstance(xc.PRESETS[name], xc.XproProfile)


def test_profile_json_roundtrip(tmp_path):
    p = xc.PRESETS["push_xpro"]
    path = tmp_path / "p.json"
    p.to_json(path)
    q = xc.XproProfile.from_json(path)
    assert q.name == p.name
    assert q.contrast == p.contrast


def test_cube_roundtrip(tmp_path):
    table = xc.profile_to_cube(xc.PRESETS["e6_in_c41"], size=9)
    path = tmp_path / "look.cube"
    xc.write_cube(path, table)
    back, domain = xc.read_cube(path)
    assert back.shape == table.shape
    assert np.allclose(back, table, atol=1e-4)


def test_apply_cube_identity(img):
    # An identity LUT must leave the image (almost) unchanged.
    n = 17
    grid = np.linspace(0, 1, n, dtype=np.float32)
    r, g, b = np.meshgrid(grid, grid, grid, indexing="ij")
    identity = np.stack([r, g, b], -1)
    out = xc.apply_cube(img, identity)
    assert np.allclose(out, img, atol=1.0 / (n - 1))


def test_tiled_packing_shape():
    table = xc.profile_to_cube(xc.PRESETS["c41_in_e6"], size=64)
    tiled = xc.table_to_tiled(table)
    assert tiled.shape == (512, 512, 3)


def test_tiled_requires_square():
    table = xc.profile_to_cube(xc.PRESETS["c41_in_e6"], size=33)
    with pytest.raises(ValueError):
        xc.table_to_tiled(table)
