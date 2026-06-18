# Color Film Emulsion Layers

Color film is a stack of light-sensitive layers coated on a base. Understanding
the stack explains *why* cross-processing produces non-uniform, non-linear color
shifts rather than a simple tint.

## The layer stack (top to bottom, typical)

```
  ── Protective overcoat
  ── UV filter
  ── Blue-sensitive layer        → forms YELLOW dye
  ── Yellow filter (Carey Lea silver)   blocks blue from lower layers
  ── Green-sensitive layer       → forms MAGENTA dye
  ── Red-sensitive layer         → forms CYAN dye
  ── Antihalation / base
  ── Film base (acetate or PET)
```

Two ideas matter:

1. **Subtractive color.** Each layer records one additive primary (R/G/B) and
   forms its *complementary* subtractive dye (cyan/magenta/yellow). Cyan absorbs
   red, magenta absorbs green, yellow absorbs blue.
2. **The yellow filter layer.** Silver halide is intrinsically blue-sensitive,
   so a yellow filter sits below the blue layer to stop blue light contaminating
   the green and red layers. (It's bleached away during processing.)

## Spectral sensitivity and dye couplers

Each layer contains **dye couplers** — colorless molecules that react with
oxidized developer to form the layer's dye. The couplers are tuned to a specific
developing agent (CD-4 for C-41, CD-3 for E-6) and to a specific development
path (negative vs. reversal). This tuning is the linchpin of cross-processing:

- Run film through the *wrong* developer and the coupling efficiency, dye hue,
  and density-vs-exposure relationship all change — **per layer, by different
  amounts**.
- The three layers therefore drift apart: their characteristic curves
  (toe/shoulder, contrast) no longer line up, which is why shadows, midtones,
  and highlights each shift toward a *different* color.

## The orange mask (C-41 only)

Color negative film carries an integral **orange mask**: colored couplers that
compensate for the unwanted absorptions of the cyan and magenta dyes during
printing. Slide film has no such mask.

- This is why **C-41-in-E-6** has such violent color: the orange mask is being
  developed by a reversal path it was never designed for.
- And why **E-6-in-C-41** looks softer/pastel: no mask + negative development of
  a reversal-tuned emulsion yields low-contrast, desaturated, shifted color.

## Layer behaviour under cross-processing (rules of thumb)

| Layer | Normal dye | Common cross-process drift |
|-------|-----------|----------------------------|
| Blue-sensitive | Yellow | Highlights → yellow/green |
| Green-sensitive | Magenta | Midtones → magenta |
| Red-sensitive | Cyan | Shadows → cyan/green; highlights → warm |

These drifts are *exposure-dependent*: a single color shift can't describe them,
which is why digital simulation needs tone-dependent transforms or multiple
blended LUTs (see [`../shaders/digital_xpro_lut.frag`](../shaders/digital_xpro_lut.frag)).

See also: [`c41_chemistry.md`](c41_chemistry.md), [`e6_chemistry.md`](e6_chemistry.md).
