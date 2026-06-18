// shaders/expired_film_xpro.frag
// Expired film, cross-processed. Maximum chaos: spatially-varying color
// shifts, uneven contrast, chaotic grain. Every frame is a unique disaster.
//
// Header + lib/common.glsl are prepended by web/viewer.js.
// NOTE: animate u_time to make the chemistry "breathe".

uniform float u_chaos_level;     // 0..1  overall instability
uniform float u_color_randomness;// 0..1  spatial color-shift variation
uniform float u_grain_chaos;     // 0..1  grain size/intensity variation
// u_time drives slow drift of the chaos field.

void main() {
    vec3 c = texture2D(u_image, v_uv).rgb;
    float l = luma(c);

    // A low-frequency, slowly drifting field of "decay" across the frame.
    vec2 fieldUV = v_uv * 3.0 + vec2(u_time * 0.05, -u_time * 0.03);
    float decayR = valueNoise(fieldUV + 11.0);
    float decayG = valueNoise(fieldUV + 37.0);
    float decayB = valueNoise(fieldUV + 71.0);
    vec3 decay = (vec3(decayR, decayG, decayB) - 0.5) * 2.0;

    // Spatially-varying color shift — some patches wild, some barely touched.
    c += decay * u_color_randomness * 0.35 * u_chaos_level;

    // Uneven contrast: the curve steepness itself varies across the frame.
    float localContrast = mix(2.0, 9.0, valueNoise(fieldUV * 1.7 + 5.0));
    c = sCurve(clamp(c, 0.0, 1.0), localContrast, mix(0.4, 0.6, decayR));

    // Patchy fading (lost sensitivity lifts random regions).
    float fade = smoothstep(0.6, 1.0, valueNoise(fieldUV * 0.8 + 19.0));
    c = mix(c, c * 0.8 + 0.18, fade * u_chaos_level);

    c = adjustSaturation(c, mix(0.7, 1.5, decayG * 0.5 + 0.5));

    // Chaotic grain: size and intensity both vary spatially.
    float gsize = mix(1.0, 4.0, valueNoise(fieldUV * 2.3));
    float g = grain(v_uv, u_resolution, gsize, u_time);
    c += g * (0.06 + 0.20 * u_grain_chaos) * (0.4 + abs(decayB));

    gl_FragColor = vec4(clamp(c, 0.0, 1.0), 1.0);
}
