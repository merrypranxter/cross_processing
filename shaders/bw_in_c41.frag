// shaders/bw_in_c41.frag
// Black-and-white film (e.g. Ilford XP2) developed in C-41 color chemistry.
// Monochrome image carrying a subtle warm tint and C-41 grain structure.
//
// Header + lib/common.glsl are prepended by web/viewer.js.

uniform vec3  u_tint_color;     // tint hue, e.g. (1.0, 0.85, 0.65) warm
uniform float u_tint_intensity; // 0..1  how strongly to tint
uniform float u_grain_size;     // 0.5..4 grain scale in pixels

void main() {
    vec3 c = texture2D(u_image, v_uv).rgb;

    // Monochrome conversion.
    float l = luma(c);

    // C-41 of a B&W stock leaves a tint that is strongest in the midtones
    // and fades toward both ends of the curve.
    float midWeight = 1.0 - abs(l - 0.5) * 2.0; // 1 at mid, 0 at ends
    vec3 tinted = mix(vec3(l), vec3(l) * u_tint_color, u_tint_intensity * (0.4 + 0.6 * midWeight));

    // Subtle highlight warmth shift (the developer biases highlights warm).
    float hi = smoothstep(0.6, 1.0, l);
    tinted += vec3(0.04, 0.02, -0.01) * hi * u_tint_intensity;

    // C-41 grain — finer and more even than push-processed B&W grain.
    float g = grain(v_uv, u_resolution, u_grain_size, 0.0);
    tinted += g * 0.05;

    gl_FragColor = vec4(clamp(tinted, 0.0, 1.0), 1.0);
}
