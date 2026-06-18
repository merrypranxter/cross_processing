// shaders/daylight_tungsten.frag
// Daylight-balanced film (5500K) shot under tungsten light (3200K).
// Strong orange cast — deep orange shadows, near-neutral highlights.
// The "1970s photograph / candlelight" look.
//
// Header + lib/common.glsl are prepended by web/viewer.js.

uniform float u_orange_shift;     // 0..1  overall warm cast strength
uniform float u_shadow_warm;      // 0..1  extra orange/brown in shadows
uniform float u_highlight_neutral;// 0..1  pull highlights back toward neutral

void main() {
    vec3 c = texture2D(u_image, v_uv).rgb;
    float l = luma(c);

    float sh = 1.0 - smoothstep(0.0, 0.55, l);
    float hi = smoothstep(0.55, 1.0, l);

    // Uniform warm cast.
    vec3 warmCast = vec3(1.18, 0.96, 0.74);
    c *= mix(vec3(1.0), warmCast, u_orange_shift);

    // Shadows go warm brown.
    c += vec3(0.12, 0.04, -0.06) * sh * u_shadow_warm;

    // Optionally pull highlights back toward neutral (eye adapts to white).
    vec3 neutralized = mix(c, vec3(luma(c)), 0.4);
    c = mix(c, neutralized, hi * u_highlight_neutral);

    c = adjustSaturation(c, 1.05);

    gl_FragColor = vec4(clamp(c, 0.0, 1.0), 1.0);
}
