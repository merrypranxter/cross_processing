// shaders/lib/common.glsl
// Shared helpers for the cross_processing shader collection.
//
// These shaders are written for GLSL ES 1.00 (WebGL1) so they run in the
// bundled web/ viewer with no transpilation. This file is NOT a #include —
// GLSL ES 1.00 has no preprocessor include. The web viewer concatenates it
// ahead of each .frag file at load time (see web/viewer.js). If you compile a
// shader by hand, paste the contents of this file above the shader body.

// ---------------------------------------------------------------------------
// Perceptual luminance (Rec. 709). Used everywhere to drive tone-dependent
// effects (shadows vs. highlights respond differently to wrong chemistry).
float luma(vec3 c) {
    return dot(c, vec3(0.2126, 0.7152, 0.0722));
}

// Cheap, stable hash -> [0,1). Good enough for film grain.
float hash21(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
}

// Value noise in [0,1].
float valueNoise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f); // smoothstep interpolation
    float a = hash21(i + vec2(0.0, 0.0));
    float b = hash21(i + vec2(1.0, 0.0));
    float c = hash21(i + vec2(0.0, 1.0));
    float d = hash21(i + vec2(1.0, 1.0));
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

// Film grain: zero-mean noise scaled by `amount`. `size` controls grain scale
// in pixels (larger = chunkier). `seed` lets you animate or vary per channel.
float grain(vec2 uv, vec2 resolution, float size, float seed) {
    vec2 p = (uv * resolution) / max(size, 0.5);
    return (hash21(p + seed) - 0.5);
}

// A filmic S-curve. `contrast` > 1 steepens midtones, `pivot` sets the gray
// point the curve rotates around (0.5 = neutral, lower = darker midtones).
float sCurve(float x, float contrast, float pivot) {
    // Logistic-style curve normalized to pass through (pivot, pivot).
    float k = max(0.01, contrast); // avoid div-by-zero (hi-lo -> 0) -> NaN
    float a = 1.0 / (1.0 + exp(-k * (x - pivot)));
    float lo = 1.0 / (1.0 + exp(-k * (0.0 - pivot)));
    float hi = 1.0 / (1.0 + exp(-k * (1.0 - pivot)));
    return (a - lo) / (hi - lo);
}

vec3 sCurve(vec3 c, float contrast, float pivot) {
    return vec3(sCurve(c.r, contrast, pivot),
                sCurve(c.g, contrast, pivot),
                sCurve(c.b, contrast, pivot));
}

// Saturation adjust around luminance. sat=1 is identity, 0 grayscale, >1 boost.
vec3 adjustSaturation(vec3 c, float sat) {
    float l = luma(c);
    return mix(vec3(l), c, sat);
}

// Smooth shadow/highlight weights from luminance. Returns vec2(shadowW, hiW).
// `split` is the tone where the crossover sits, `softness` the transition width.
vec2 toneWeights(float l, float split, float softness) {
    float hi = smoothstep(split - softness, split + softness, l);
    return vec2(1.0 - hi, hi);
}

// Convert a color temperature shift into an RGB multiplier (approximate).
// `amount` in roughly [-1,1]; positive = warmer (more red/less blue).
vec3 warmth(float amount) {
    return vec3(1.0 + 0.25 * amount, 1.0, 1.0 - 0.25 * amount);
}
