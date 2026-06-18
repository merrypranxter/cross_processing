// shaders/split_tone_xpro.frag
// Split-tone derived from cross-process behaviour: shadows and highlights
// tinted with different colors, joined by a smooth tone-dependent transition.
// Default: cyan shadows (blue layer overdeveloping), orange highlights
// (red layer underdeveloping). Grain differs between shadows and highlights.
//
// Header + lib/common.glsl are prepended by web/viewer.js.

uniform vec3  u_shadow_color;     // e.g. (0.0, 0.55, 0.65) cyan
uniform vec3  u_highlight_color;  // e.g. (1.0, 0.55, 0.15) orange
uniform float u_split_smoothness; // 0.05..0.5 width of the crossover
uniform float u_balance;          // -0.5..0.5 move the crossover up/down

void main() {
    vec3 c = texture2D(u_image, v_uv).rgb;
    float l = luma(c);

    float split = clamp(0.5 + u_balance, 0.05, 0.95);
    vec2 w = toneWeights(l, split, u_split_smoothness); // (shadowW, hiW)

    // Soft-light style tint so the toning colors interact with luminance
    // rather than flatly overlaying.
    vec3 shadowTone    = mix(c, c * u_shadow_color * 2.0, 0.5);
    vec3 highlightTone = mix(c, 1.0 - (1.0 - c) * (1.0 - u_highlight_color), 0.5);

    vec3 outc = c;
    outc = mix(outc, shadowTone, w.x * 0.7);
    outc = mix(outc, highlightTone, w.y * 0.7);

    // Grain: chunkier in shadows, finer in highlights.
    float gSh = grain(v_uv, u_resolution, 2.5, 1.0) * w.x * 0.06;
    float gHi = grain(v_uv, u_resolution, 1.2, 2.0) * w.y * 0.03;
    outc += gSh + gHi;

    gl_FragColor = vec4(clamp(outc, 0.0, 1.0), 1.0);
}
