// shaders/e6_in_c41.frag
// E-6 slide film developed in C-41 negative chemistry.
// Muted, pastel, low contrast, "faded postcard" look. Peach midtones,
// cyan shadows, lifted blacks, soft highlights.
//
// Header + lib/common.glsl are prepended by web/viewer.js.

uniform float u_fade_amount;        // 0..1  lift blacks / wash out
uniform float u_pastel_shift;       // 0..1  peach/cyan color cast strength
uniform float u_contrast_reduction; // 0..1  how much to flatten contrast
uniform float u_warmth;             // -1..1 overall warm/cool bias

void main() {
    vec3 c = texture2D(u_image, v_uv).rgb;
    float l = luma(c);

    // Flatten the contrast curve toward mid-gray.
    c = mix(c, vec3(mix(0.5, l, 0.5)), u_contrast_reduction * 0.6);

    // Lift the blacks (faded film never reaches true black).
    c = mix(c, c * 0.85 + 0.12, u_fade_amount);

    // Pastel split: peach in highlights, cyan in shadows.
    float hi = smoothstep(0.45, 0.95, l);
    float sh = 1.0 - smoothstep(0.05, 0.55, l);
    vec3 peach = vec3(1.0, 0.80, 0.67); // #FFCCAA-ish
    vec3 cyan  = vec3(0.67, 0.80, 1.0); // #AACCFF-ish
    vec3 cast = mix(vec3(1.0), peach, hi * u_pastel_shift)
              * mix(vec3(1.0), cyan, sh * u_pastel_shift);
    c *= cast;

    // Desaturate slightly — the colors are tired.
    c = adjustSaturation(c, 0.78);

    // Gentle warmth bias.
    c *= warmth(u_warmth);

    gl_FragColor = vec4(clamp(c, 0.0, 1.0), 1.0);
}
