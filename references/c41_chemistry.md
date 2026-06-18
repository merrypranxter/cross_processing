# C-41 Chemistry

C-41 is the standard process for developing **color negative** film. It is a
chromogenic process: the dyes are *formed during development* rather than being
present in the emulsion beforehand.

## Process steps

| Step | Chemistry | Temp | Purpose |
|------|-----------|------|---------|
| 1. Color developer | CD-4 developing agent | 37.8 °C (100 °F) | Reduces exposed silver halide to metallic silver; the oxidized developer reacts with dye couplers to form cyan/magenta/yellow dye clouds |
| 2. Bleach | Ferric EDTA (or ferricyanide) | ~38 °C | Re-oxidizes the metallic silver back to silver halide |
| 3. Fix | Ammonium thiosulfate | ~38 °C | Dissolves the silver halide, leaving only the dye image |
| 4. Wash | Water | — | Removes residual chemistry |
| 5. Stabilizer | Surfactant + (formerly) formaldehyde | — | Hardens/stabilizes dyes, wetting agent for even drying |

The defining feature of C-41 is the **single color developer (CD-4)** working at
a tightly controlled high temperature. The process is short (the developer step
is ~3:15) and standardized worldwide, which is exactly why it's a magnet for
deliberate misuse.

## The chromogenic reaction

1. Light exposes silver halide crystals, creating a latent image.
2. CD-4 reduces the exposed crystals to metallic silver. In doing so the
   developer molecule is oxidized.
3. The oxidized developer couples with **dye couplers** embedded in each
   emulsion layer:
   - red-sensitive layer → **cyan** dye
   - green-sensitive layer → **magenta** dye
   - blue-sensitive layer → **yellow** dye
4. Bleach + fix remove all the silver, leaving only the subtractive CMY dyes.

Because it is a *negative* process, the dye amounts are inversely proportional to
exposure, and the orange **mask** (an integral colored coupler layer) corrects
for unwanted dye absorptions during printing.

## Why it matters for cross-processing

- C-41's developer is a **color** developer. When you put **E-6 (slide) film**
  into C-41, the C-41 developer forms negative-style dye clouds in a film that
  was engineered for reversal — the result is muted, low-contrast, pastel, and
  shifted, because the dye couplers and layer balance are wrong for this path.
- When you develop **C-41 film correctly** but later cross-process *another*
  stock through C-41, the orange mask and coupler chemistry of the host film
  drive much of the color character.
- C-41's high, fixed temperature and short times make push/pull behaviour
  predictable enough to be repeatable as an *aesthetic*.

## Practical notes

- C-41 is more temperature-forgiving than E-6 in practice, but color accuracy
  still depends on the 37.8 °C developer.
- "Blix" (combined bleach + fix) is common in consumer kits; pro labs keep them
  separate for archival stability.
- Exhausted C-41 developer shifts everything warm/green — a known source of the
  "lab look" some photographers chase deliberately.

See also: [`e6_chemistry.md`](e6_chemistry.md),
[`color_film_layers.md`](color_film_layers.md).
