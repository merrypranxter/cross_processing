# A Short History of Cross-Processing

Cross-processing — *développement croisé*, "X-pro" — is the deliberate
development of film in chemistry meant for a different film type. What began as a
darkroom mistake became one of the most recognizable aesthetics in photography.

## Origins: the productive accident

The standardization of C-41 (color negative) and E-6 (color reversal) in the
1970s created two incompatible-but-physically-mixable processes. Inevitably,
rolls ended up in the wrong tank — and some of those "ruined" rolls were more
interesting than the correct ones. Photographers began doing it on purpose.

## The 1980s–1990s: fashion and editorial

Cross-processing became a signature of high-fashion and music photography:

- The look — **punchy contrast, surreal color casts, glowing highlights, gritty
  grain** — read as modern, edgy, and expensive on the printed page.
- Editorial shooters used **slide film in C-41** for pastel, dreamy spreads, and
  **negative film in E-6** for saturated, high-contrast impact.
- It defined the visual language of 1990s magazines, album covers, and early
  music video color grading.

## Lomography and the democratization of the look

The **Lomographic Society** (founded 1992, around the Lomo LC-A camera) turned
cross-processing into a populist movement. Their "Ten Golden Rules"
("don't think," "be fast," "shoot from the hip") embraced unpredictability, and
cross-processing — especially slide film like Agfa Precisa or Kodak Elite Chrome
run through C-41 — became a Lomography staple. The "Lomo look" (vignetting,
saturated shifts, light leaks, cross-process color) entered popular culture.

## The 2000s: chemical look, digital tools

As digital cameras took over, the cross-process *aesthetic* outlived the
*chemistry*:

- Photoshop **curves** adjustments (the classic "cross-process curve": S-curve
  the RGB master, push blue down in shadows, pull it up in highlights) recreated
  the look.
- Apps and presets — VSCO, Instagram's early filters (e.g. "X-Pro II"),
  Lightroom presets — packaged it for everyone.
- These digital versions are usually **uniform color grades**; they miss the
  *exposure-dependent, per-layer* behaviour of real chemistry, which is exactly
  the gap this repository's tone-dependent shaders and multi-LUT approach try to
  close.

## Popular film/process combinations

| Film (designed for) | Processed in | Characteristic result |
|---------------------|--------------|-----------------------|
| Slide / E-6 (Provia, Velvia, Elite Chrome, Precisa) | C-41 | High contrast, vivid/shifted color, strong casts (often green/yellow) |
| Negative / C-41 (Portra, Pro 400H, consumer color) | E-6 | Muted, pastel, low-contrast, "faded" — but with surreal shifts |
| B&W chromogenic (Ilford XP2, Kodak BW400CN) | C-41 | Intended path, but yields neutral/cool-warm mono with C-41 grain |

> Note: the colloquial shorthand can be confusing. "Cross-processed slides" most
> often means **E-6 film developed in C-41** — the classic high-contrast,
> heavily-shifted Lomo look — even though the seed material and shaders here also
> explore the reverse (**C-41 film in E-6**). Both directions are covered; check
> the layer behaviour in [`color_film_layers.md`](color_film_layers.md).

## Why it endures

Cross-processing is a deliberate surrender of control: the photographer chooses
the *conditions* for an accident and accepts the result. In an era of perfect,
correctable digital color, the unpredictability and chemical "honesty" of the
wrong process is precisely the appeal — the mistake is the masterpiece.

See also: [`c41_chemistry.md`](c41_chemistry.md), [`e6_chemistry.md`](e6_chemistry.md).
