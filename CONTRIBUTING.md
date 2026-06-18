# Contributing

Thanks for wanting to develop film in the wrong chemicals.

## Setup

```bash
pip install -r requirements.txt
pytest -q
```

## Adding a new cross-process look

A look lives in three places that must stay in sync:

1. **A preset** — add an `XproProfile` to `PRESETS` in
   [`tools/xpro_core.py`](tools/xpro_core.py), then dump it:
   ```bash
   python - <<'PY'
   import json; from dataclasses import asdict
   import sys; sys.path.insert(0, "tools"); import xpro_core as xc
   name = "my_look"
   json.dump(asdict(xc.PRESETS[name]), open(f"presets/{name}.json","w"), indent=2)
   PY
   ```
2. **A shader** (optional but encouraged) — add `shaders/my_look.frag`. Declare
   only your own uniforms and `main()`; the viewer prepends the standard header
   and `lib/common.glsl`. Register it in the `SHADERS` map in
   [`web/viewer.js`](web/viewer.js) so it shows up in the viewer.
3. **A gallery render** — `python tools/make_gallery.py` regenerates the
   contact sheet and per-preset renders.

## Style

- **Shaders**: GLSL ES 1.00 (WebGL1). Keep helpers in `lib/common.glsl` when
  they're reusable. No 3D textures (use the tiled-LUT approach).
- **Python**: standard library + numpy + Pillow. Keep the maths in
  `xpro_core.py` so tools, tests, and notebooks share one implementation.
- **Tests**: add a case to `tests/` for new core functionality. Run `pytest -q`.

## Pull requests

- Keep changes focused and described.
- Make sure `pytest -q` passes and the viewer still loads every shader.
- If you change the look model, regenerate the gallery so the README image
  reflects reality.
