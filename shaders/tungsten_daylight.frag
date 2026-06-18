// shaders/tungsten_daylight.frag
// Tungsten-balanced film (3200K) shot in daylight (5500K), no filter.
// Strong blue cast — deep blue shadows, less-affected (warmer) highlights.
// A cold scene with a split-tone feel.
//
// Header + lib/common.glsl are prepended by web/viewer.js.

uniform float u_blue_shift;     // 0..1  overall blue cast strength
uniform float u_shadow_cool;    // 0..1  extra blue in shadows
uniform float u_highlight_warm; // 0..1  warmth retained in highlights

void main() {
    vec3 c = texture2D(u_image, v_uv).rgb;
    float l = luma(c);

    float sh = 1.0 - smoothstep(0.0, 0.55, l);
    float hi = smoothstep(0.55, 1.0, l);

    // Uniform blue cast (tungsten film over-reads blue in daylight).
    vec3 coolCast = vec3(0.82, 0.92, 1.18); // boosts blue, cuts red
    c *= mix(vec3(1.0), coolCast, u_blue_shift);

    // Shadows go deep blue.
    c += vec3(-0.04, 0.0, 0.14) * sh * u_shadow_cool;

    // Highlights keep some warmth (they read near white).
    c += vec3(0.10, 0.04, -0.06) * hi * u_highlight_warm;

    c = adjustSaturation(c, 1.05);

    gl_FragColor = vec4(clamp(c, 0.0, 1.0), 1.0);
}
