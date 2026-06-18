// shaders/digital_xpro_lut.frag
// Digital LUT-based cross-process simulation.
//
// WebGL1 has no 3D textures, so the 3D LUT is packed into a 2D "tiled grid"
// image: a cube of size N is laid out as a sqrt(N) x sqrt(N) grid of NxN tiles
// (the classic Hald/tiled CLUT). For N=64 that's a 512x512 PNG. Generate one
// with notebooks/xpro_lut_generator.ipynb or tools/xpro_lut_applier.py.
//
// Three LUTs are blended by input tone (shadow / midtone / highlight) because
// real cross-processing is exposure-dependent and a single LUT is never enough.
//
// Header + lib/common.glsl are prepended by web/viewer.js.

uniform sampler2D u_lut_shadow;
uniform sampler2D u_lut_mid;
uniform sampler2D u_lut_high;
uniform float u_lut_size;   // N, e.g. 64.0
uniform float u_amount;     // 0..1 blend between original and graded

// Sample a tiled-grid 2D LUT with manual trilinear interpolation.
vec3 sampleLUT(sampler2D lut, vec3 color, float n) {
    color = clamp(color, 0.0, 1.0);
    float tilesPerRow = floor(sqrt(n) + 0.5);  // e.g. 8 for N=64
    float texSize = n * tilesPerRow;           // e.g. 512

    // Blue index selects which tile (slice). Interpolate between two slices.
    float blue = color.b * (n - 1.0);
    float slice0 = floor(blue);
    float slice1 = min(slice0 + 1.0, n - 1.0);
    float fb = blue - slice0;

    // Within-tile position from red/green, with half-texel inset.
    vec2 rg = color.rg * (n - 1.0) + 0.5;

    // Convert a slice index + rg to a UV in the packed texture.
    // (declared as a lambda-style inline since GLSL ES has no closures)
    vec2 tile0 = vec2(mod(slice0, tilesPerRow), floor(slice0 / tilesPerRow));
    vec2 tile1 = vec2(mod(slice1, tilesPerRow), floor(slice1 / tilesPerRow));

    vec2 uv0 = (tile0 * n + rg) / texSize;
    vec2 uv1 = (tile1 * n + rg) / texSize;

    vec3 c0 = texture2D(lut, uv0).rgb;
    vec3 c1 = texture2D(lut, uv1).rgb;
    return mix(c0, c1, fb);
}

void main() {
    vec3 src = texture2D(u_image, v_uv).rgb;
    float l = luma(src);

    // Tone weights for the three LUTs.
    float sh = 1.0 - smoothstep(0.0, 0.5, l);
    float hi = smoothstep(0.5, 1.0, l);
    float mid = clamp(1.0 - sh - hi, 0.0, 1.0);
    float wsum = sh + mid + hi + 1e-5;

    vec3 graded = (sampleLUT(u_lut_shadow, src, u_lut_size) * sh
                 + sampleLUT(u_lut_mid,    src, u_lut_size) * mid
                 + sampleLUT(u_lut_high,   src, u_lut_size) * hi) / wsum;

    gl_FragColor = vec4(clamp(mix(src, graded, u_amount), 0.0, 1.0), 1.0);
}
