# E-6 Chemistry

E-6 is the standard process for **color reversal (slide / transparency)** film.
Unlike C-41, it produces a **positive** image on the film itself. It is a longer,
more temperature-sensitive process with **two** development stages.

## Process steps

| Step | Chemistry | Purpose |
|------|-----------|---------|
| 1. First developer | B&W developer (hydroquinone / phenidone) | Develops the *exposed* silver halide to a negative silver image. **No dye is formed here.** |
| 2. Wash / stop | Water | Halts first development |
| 3. Reversal bath | Stannous chloride (or chemical fogging) | Fogs the *remaining* unexposed silver halide so it can be developed in step 4 |
| 4. Color developer | CD-3 developing agent | Develops the fogged silver and forms cyan/magenta/yellow dyes — this is the positive dye image |
| 5. Pre-bleach / conditioner | — | Prepares silver for bleaching |
| 6. Bleach | Ferric EDTA | Converts all metallic silver back to halide |
| 7. Fix | Ammonium thiosulfate | Removes all silver halide |
| 8. Final rinse | Surfactant | Even drying |

Temperature control of the **first developer (38 °C, ±0.3 °C)** is critical:
it sets the overall density and contrast of the final slide. E-6 is far less
forgiving than C-41.

## The reversal logic

The trick of reversal processing is the two-stage development:

1. **First developer** makes a *negative* silver image from the exposed grains.
2. **Reversal bath** fogs everything that's left (the unexposed grains).
3. **Color developer** then develops *those* fogged grains — which are the
   inverse of the original exposure — producing a *positive* dye image.

So a bright part of the scene exposes a lot of silver, which the first developer
consumes; little is left to fog and dye, so it stays light. A dark part exposes
little, leaving lots to fog and dye dark. The image is positive.

## Why it matters for cross-processing

This two-stage structure is the heart of the most famous cross-process:

- **C-41 film in E-6**: The E-6 *first developer* (a B&W developer) makes a
  silver negative from the C-41 stock. But C-41 film's dye couplers and layer
  sensitivities are tuned for a single CD-4 color development. When E-6's
  CD-3 color developer hits it, the dyes form in the **wrong amounts and wrong
  balance**, and the reversal step interacts unexpectedly with the orange mask
  baked into C-41 film. Result: the iconic **high contrast, magenta/green/
  yellow shifted, heavy-grain** cross-process look.
- The strong, separate **first developer** also explains the extreme contrast:
  its B&W contrast curve is imposed on top of the color film's already-steep
  reversal-oriented emulsion.

## Practical notes

- E-6's tight temperature tolerance means cross-processing E-6 chemistry yields
  more *repeatable* extreme results than the looser C-41-host direction.
- Push/pull in E-6 is done by extending/shortening the **first developer** time,
  which is why pushing cross-processed C-41 film so dramatically amplifies
  contrast and grain.
- Older 3-bath hobby kits combine steps; pro 6-bath kits keep them separate.

See also: [`c41_chemistry.md`](c41_chemistry.md),
[`color_film_layers.md`](color_film_layers.md),
[`cross_process_history.md`](cross_process_history.md).
