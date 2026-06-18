// shaders/push_processed_xpro.frag
// Push-developed cross-processing: longer development in the wrong chemistry.
// Extreme color shifts, blown highlights, crushed shadows, large clumpy grain.
// The "punk rock" cross-process.
//
// Header + lib/common.glsl are prepended by web/viewer.js.

uniform float u_push_stops;    // 0..3   how many stops of push
uniform float u_aggression;    // 0..1   color shift exaggeration
uniform float u_highlight_clip;// 0..1   how hard highlights blow out
uniform float u_shadow_crush;  // 0..1   how hard shadows crush

void main() {
    vec3 c = texture2D(u_image, v_uv).rgb;
    float l = luma(c);

    // Push raises exposure non-linearly.
    c *= 1.0 + 0.35 * u_push_stops;

    // Exaggerated channel-skewed shift (magenta/green push).
    float hi = smoothstep(0.5, 1.0, l);
    float sh = 1.0 - smoothstep(0.0, 0.5, l);
    vec3 shift = vec3(0.20, -0.10, 0.18) * (0.5 + hi)   // magenta-yellow highs
               + vec3(-0.05, 0.16, -0.04) * sh;          // green shadows
    c += shift * u_aggression;

    // Brutal S-curve.
    float contrast = 6.0 + 6.0 * u_push_stops;
    c = sCurve(clamp(c, 0.0, 1.0), contrast, 0.42);

    // Crush shadows and clip highlights explicitly.
    c = mix(c, smoothstep(0.0, 1.0, c), 0.4);
    c -= u_shadow_crush * 0.12 * sh;
    c += u_highlight_clip * 0.18 * hi;

    c = adjustSaturation(c, 1.4);

    // Huge clumpy grain (low-frequency noise modulating fine grain).
    float clump = valueNoise(v_uv * u_resolution / 28.0);
    float g = grain(v_uv, u_resolution, 2.5, 0.0);
    c += g * (0.10 + 0.18 * u_push_stops) * (0.5 + clump);

    gl_FragColor = vec4(clamp(c, 0.0, 1.0), 1.0);
}
