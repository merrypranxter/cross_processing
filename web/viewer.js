/* web/viewer.js — minimal WebGL1 viewer for the cross_processing shaders.
 *
 * Loads a .frag from ../shaders/, prepends a standard header + lib/common.glsl,
 * binds an image to u_image, and exposes each shader's custom uniforms as
 * sliders / color pickers.
 *
 * Serve over HTTP (fetch can't read file://). From the repo root:
 *     python -m http.server
 * then open http://localhost:8000/web/
 */

// Standard preamble prepended before lib/common.glsl and the shader body.
const HEADER = `
precision highp float;
uniform sampler2D u_image;
uniform vec2  u_resolution;
uniform float u_time;
varying vec2  v_uv;
`;

const VERT = `
attribute vec2 a_pos;
varying vec2 v_uv;
void main() {
  v_uv = a_pos * 0.5 + 0.5;
  gl_Position = vec4(a_pos, 0.0, 1.0);
}
`;

// Per-shader uniform UI config. type: "range" -> slider, "color" -> RGB picker.
// Uniforms not listed (u_image, u_resolution, u_time) are handled automatically.
const SHADERS = {
  "c41_in_e6": {
    u_shift_intensity: { type: "range", min: 0, max: 1, value: 0.8 },
    u_contrast_boost:  { type: "range", min: 1, max: 12, value: 6 },
    u_grain_amount:    { type: "range", min: 0, max: 0.3, value: 0.06 },
    u_saturation:      { type: "range", min: 0, max: 2, value: 1.35 },
  },
  "e6_in_c41": {
    u_fade_amount:        { type: "range", min: 0, max: 1, value: 0.7 },
    u_pastel_shift:       { type: "range", min: 0, max: 1, value: 0.6 },
    u_contrast_reduction: { type: "range", min: 0, max: 1, value: 0.6 },
    u_warmth:             { type: "range", min: -1, max: 1, value: 0.2 },
  },
  "bw_in_c41": {
    u_tint_color:     { type: "color", value: [1.0, 0.85, 0.65] },
    u_tint_intensity: { type: "range", min: 0, max: 1, value: 0.5 },
    u_grain_size:     { type: "range", min: 0.5, max: 4, value: 1.5 },
  },
  "push_processed_xpro": {
    u_push_stops:     { type: "range", min: 0, max: 3, value: 1.5 },
    u_aggression:     { type: "range", min: 0, max: 1, value: 0.8 },
    u_highlight_clip: { type: "range", min: 0, max: 1, value: 0.6 },
    u_shadow_crush:   { type: "range", min: 0, max: 1, value: 0.6 },
  },
  "expired_film_xpro": {
    u_chaos_level:      { type: "range", min: 0, max: 1, value: 0.7 },
    u_color_randomness: { type: "range", min: 0, max: 1, value: 0.7 },
    u_grain_chaos:      { type: "range", min: 0, max: 1, value: 0.6 },
    animated: true,
  },
  "tungsten_daylight": {
    u_blue_shift:     { type: "range", min: 0, max: 1, value: 0.7 },
    u_shadow_cool:    { type: "range", min: 0, max: 1, value: 0.7 },
    u_highlight_warm: { type: "range", min: 0, max: 1, value: 0.5 },
  },
  "daylight_tungsten": {
    u_orange_shift:      { type: "range", min: 0, max: 1, value: 0.7 },
    u_shadow_warm:       { type: "range", min: 0, max: 1, value: 0.7 },
    u_highlight_neutral: { type: "range", min: 0, max: 1, value: 0.4 },
  },
  "selective_cross_process": {
    u_use_mask_tex:      { type: "range", min: 0, max: 1, value: 0 },
    u_process_intensity: { type: "range", min: 0, max: 1, value: 1 },
    u_mask_blur:         { type: "range", min: 0, max: 0.5, value: 0.15 },
    u_mask_radius:       { type: "range", min: 0, max: 0.8, value: 0.35 },
    // u_mask_center is fixed at (0.5,0.5); u_mask_texture left unbound (uses gradient)
  },
  "split_tone_xpro": {
    u_shadow_color:     { type: "color", value: [0.0, 0.55, 0.65] },
    u_highlight_color:  { type: "color", value: [1.0, 0.55, 0.15] },
    u_split_smoothness: { type: "range", min: 0.05, max: 0.5, value: 0.25 },
    u_balance:          { type: "range", min: -0.5, max: 0.5, value: 0.0 },
  },
  // digital_xpro_lut needs LUT textures; omitted from the default UI.
};

const gl = document.getElementById("gl").getContext("webgl");
if (!gl) alert("WebGL is not available in this browser.");

let program = null;
let imageTex = null;
let imageSize = [900, 600];
let current = null;       // current shader name
let uniformState = {};    // name -> value
let startTime = performance.now();

function compile(type, src) {
  const s = gl.createShader(type);
  gl.shaderSource(s, src);
  gl.compileShader(s);
  if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
    throw new Error(gl.getShaderInfoLog(s) + "\n---\n" + src);
  }
  return s;
}

function buildProgram(fragBody, common) {
  const fragSrc = HEADER + "\n" + common + "\n" + fragBody;
  const p = gl.createProgram();
  gl.attachShader(p, compile(gl.VERTEX_SHADER, VERT));
  gl.attachShader(p, compile(gl.FRAGMENT_SHADER, fragSrc));
  gl.linkProgram(p);
  if (!gl.getProgramParameter(p, gl.LINK_STATUS)) {
    throw new Error(gl.getProgramInfoLog(p));
  }
  return p;
}

// Fullscreen triangle.
const quad = gl.createBuffer();
gl.bindBuffer(gl.ARRAY_BUFFER, quad);
gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);

function makeTexture(source) {
  const tex = gl.createTexture();
  gl.bindTexture(gl.TEXTURE_2D, tex);
  gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
  gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, source);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
  return tex;
}

// A synthetic default image so the viewer works with no upload.
function syntheticImage() {
  const c = document.createElement("canvas");
  c.width = 512; c.height = 384;
  const x = c.getContext("2d");
  const grad = x.createLinearGradient(0, 0, c.width, c.height);
  grad.addColorStop(0, "#102030"); grad.addColorStop(0.5, "#a08060");
  grad.addColorStop(1, "#f0e0c0");
  x.fillStyle = grad; x.fillRect(0, 0, c.width, c.height);
  const patches = ["#d02020", "#20a040", "#3050d0", "#e0e0e0", "#202020"];
  patches.forEach((p, i) => { x.fillStyle = p; x.fillRect(20 + i * 90, 20, 70, 70); });
  x.fillStyle = "#fff"; x.font = "20px sans-serif";
  x.fillText("cross_processing", 24, 360);
  return c;
}

function setImage(source, w, h) {
  imageTex = makeTexture(source);
  imageSize = [w, h];
  const canvas = gl.canvas;
  canvas.width = w; canvas.height = h;
}

function buildUniformUI(name) {
  const cfg = SHADERS[name];
  const host = document.getElementById("uniforms");
  host.innerHTML = "";
  uniformState = {};
  for (const [u, spec] of Object.entries(cfg)) {
    if (u === "animated") continue;
    uniformState[u] = spec.value;
    const div = document.createElement("div");
    div.className = "uniform";
    if (spec.type === "range") {
      div.innerHTML =
        `<div class="row"><span>${u}</span><span id="v_${u}">${spec.value}</span></div>`;
      const input = document.createElement("input");
      input.type = "range"; input.min = spec.min; input.max = spec.max;
      input.step = (spec.max - spec.min) / 200; input.value = spec.value;
      input.oninput = () => {
        uniformState[u] = parseFloat(input.value);
        document.getElementById("v_" + u).textContent = (+input.value).toFixed(3);
      };
      div.appendChild(input);
    } else if (spec.type === "color") {
      const hex = rgbToHex(spec.value);
      div.innerHTML = `<label>${u}</label>`;
      const input = document.createElement("input");
      input.type = "color"; input.value = hex;
      input.oninput = () => { uniformState[u] = hexToRgb(input.value); };
      div.appendChild(input);
    }
    host.appendChild(div);
  }
}

function rgbToHex(c) {
  const h = (v) => Math.round(v * 255).toString(16).padStart(2, "0");
  return "#" + h(c[0]) + h(c[1]) + h(c[2]);
}
function hexToRgb(hex) {
  return [parseInt(hex.slice(1, 3), 16) / 255,
          parseInt(hex.slice(3, 5), 16) / 255,
          parseInt(hex.slice(5, 7), 16) / 255];
}

async function loadShader(name) {
  const [frag, common] = await Promise.all([
    fetch(`../shaders/${name}.frag`).then((r) => r.text()),
    fetch(`../shaders/lib/common.glsl`).then((r) => r.text()),
  ]);
  if (program) gl.deleteProgram(program);
  program = buildProgram(frag, common);
  current = name;
  buildUniformUI(name);
}

function render() {
  requestAnimationFrame(render);
  if (!program || !imageTex) return;
  gl.viewport(0, 0, gl.canvas.width, gl.canvas.height);
  gl.useProgram(program);

  const posLoc = gl.getAttribLocation(program, "a_pos");
  gl.bindBuffer(gl.ARRAY_BUFFER, quad);
  gl.enableVertexAttribArray(posLoc);
  gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0);

  gl.activeTexture(gl.TEXTURE0);
  gl.bindTexture(gl.TEXTURE_2D, imageTex);
  setUniform("u_image", 0, "1i");
  setUniform("u_resolution", imageSize, "2f");
  setUniform("u_time", (performance.now() - startTime) / 1000, "1f");

  for (const [u, val] of Object.entries(uniformState)) {
    if (Array.isArray(val)) setUniform(u, val, "3f");
    else setUniform(u, val, "1f");
  }

  gl.drawArrays(gl.TRIANGLES, 0, 3);
}

function setUniform(name, val, kind) {
  const loc = gl.getUniformLocation(program, name);
  if (loc === null) return;
  if (kind === "1i") gl.uniform1i(loc, val);
  else if (kind === "1f") gl.uniform1f(loc, val);
  else if (kind === "2f") gl.uniform2f(loc, val[0], val[1]);
  else if (kind === "3f") gl.uniform3f(loc, val[0], val[1], val[2]);
}

// --- wire up UI ---
const sel = document.getElementById("shader");
Object.keys(SHADERS).forEach((name) => {
  const o = document.createElement("option");
  o.value = name; o.textContent = name;
  sel.appendChild(o);
});
sel.onchange = () => loadShader(sel.value).catch((e) => alert(e.message));

document.getElementById("image").onchange = (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const img = new Image();
  img.onload = () => setImage(img, img.width, img.height);
  img.src = URL.createObjectURL(file);
};

document.getElementById("save").onclick = () => {
  const a = document.createElement("a");
  a.download = `${current || "render"}.png`;
  a.href = gl.canvas.toDataURL("image/png");
  a.click();
};

// boot
const synth = syntheticImage();
setImage(synth, synth.width, synth.height);
loadShader(sel.value).catch((e) => alert(e.message));
render();
