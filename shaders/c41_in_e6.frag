// shaders/c41_in_e6.frag
// C-41 color negative film developed in E-6 slide chemistry.
// The classic cross-process: high contrast, magenta skies, green skin,
// yellow shadows, heavy grain. A non-linear, tone-dependent color transform.
//
// Header (precision, u_image, u_resolution, u_time, v_uv) and lib/common.glsl
// are prepended by web/viewer.js. See shaders/lib/common.glsl.

uniform float u_shift_intensity; // 0..1  strength of the chemistry mismatch
uniform float u_contrast_boost;  // 1..12 S-curve steepness
uniform float u_grain_amount;    // 0..0.3 grain visibility
uniform float u_saturation;      // 0..2  post saturation

void main() {
    vec3 c = texture2D(u_image, v_uv).rgb;
    float l = luma(c);

    // Tone weights: shadows / midtones / highlights each shift differently.
    float sh = 1.0 - smoothstep(0.0, 0.5, l);     // shadow weight
    float hi = smoothstep(0.5, 1.0, l);           // highlight weight
    float mid = 1.0 - sh - hi;                    // midtone weight

    // The signature shifts of C-41-in-E-6.
    vec3 shadowShift    = vec3(-0.02,  0.10, -0.06); // green shadows
    vec3 midtoneShift   = vec3( 0.12, -0.04,  0.10); // magenta midtones
    vec3 highlightShift = vec3( 0.14,  0.10, -0.12); // yellow highlights

    vec3 shift = shadowShift * sh + midtoneShift * mid + highlightShift * hi;
    c += shift * u_shift_intensity;

    // Aggressive S-curve, darker pivot (crushed blacks, blown highlights).
    c = sCurve(clamp(c, 0.0, 1.0), u_contrast_boost, 0.45);

    // Cross-processed film is saturated and channel-skewed.
    c = adjustSaturation(c, u_saturation);

    // Heavy, slightly colored grain — stronger in shadows.
    float g = grain(v_uv, u_resolution, 1.5, u_time * 0.0);
    c += g * u_grain_amount * (0.6 + sh);

    gl_FragColor = vec4(clamp(c, 0.0, 1.0), 1.0);
}
