// shaders/selective_cross_process.frag
// Apply a cross-process look to only part of the frame, driven by a mask.
// The mask can be the bundled radial/linear gradient (default) or a texture.
//
// Header + lib/common.glsl are prepended by web/viewer.js.

uniform sampler2D u_mask_texture;   // optional external mask (white = process)
uniform float     u_use_mask_tex;   // 0 = procedural gradient, 1 = use texture
uniform float     u_process_intensity; // 0..1 effect strength inside mask
uniform float     u_mask_blur;      // 0..0.5 softness of procedural mask edge
uniform vec2      u_mask_center;    // procedural mask center, default (0.5,0.5)
uniform float     u_mask_radius;    // procedural mask radius, default 0.35

// Inline the c41-in-e6 transform so this shader is self-contained.
vec3 crossProcess(vec3 c) {
    float l = luma(c);
    float sh = 1.0 - smoothstep(0.0, 0.5, l);
    float hi = smoothstep(0.5, 1.0, l);
    float mid = 1.0 - sh - hi;
    vec3 shift = vec3(-0.02, 0.10, -0.06) * sh
               + vec3( 0.12, -0.04, 0.10) * mid
               + vec3( 0.14, 0.10, -0.12) * hi;
    c += shift;
    c = sCurve(clamp(c, 0.0, 1.0), 6.0, 0.45);
    return adjustSaturation(c, 1.3);
}

void main() {
    vec3 c = texture2D(u_image, v_uv).rgb;

    float mask;
    if (u_use_mask_tex > 0.5) {
        mask = texture2D(u_mask_texture, v_uv).r;
    } else {
        float d = distance(v_uv, u_mask_center);
        float edge = max(u_mask_blur, 0.001);
        mask = 1.0 - smoothstep(u_mask_radius, u_mask_radius + edge, d);
    }

    vec3 processed = crossProcess(c);
    vec3 outc = mix(c, processed, mask * u_process_intensity);

    gl_FragColor = vec4(clamp(outc, 0.0, 1.0), 1.0);
}
