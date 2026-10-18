// One particle field shared by the whole page (adapted from paulasquin.com).
// Every section names a shape (data-shape); the particles fly from the current
// shape to the next one. Each particle carries a "kind" (integer part of w) and
// a parameter (fraction of w) that the vertex shader animates: network forward
// pass, orbits, and a scan sweeping upwards through the AI mark and the stack.
import * as THREE from 'three';

const K = { STILL: 0, EDGE: 1, NODE: 2, ORBIT: 3, SWEEP: 4 };

/* ---------------- shapes ---------------- */

function rng(seed) {
  let s = seed >>> 0;
  return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296);
}

class Shape {
  constructor(n) {
    this.n = n;
    this.pos = new Float32Array(n * 4);
    this.col = new Float32Array(n * 3);
    this.i = 0;
  }
  push(x, y, z, kind, param, c) {
    if (this.i >= this.n) return;
    const i = this.i++;
    this.pos.set([x, y, z, kind + Math.min(param, 0.999)], i * 4);
    this.col.set([c.r, c.g, c.b], i * 3);
  }
  get full() { return this.i >= this.n; }
}

const C = (hex, k = 1) => new THREE.Color(hex).multiplyScalar(k);
const lerpC = (a, b, t) => a.clone().lerp(b, t);

function orb(n) {
  const s = new Shape(n), r = rng(1);
  const cyan = C('#6fd6ff'), violet = C('#8b7bff'), mint = C('#4fe0c0');
  const nSphere = Math.floor(n * 0.62);
  for (let i = 0; i < nSphere; i++) {
    const y = 1 - (2 * (i + 0.5)) / nSphere, rad = Math.sqrt(1 - y * y), a = i * 2.399963;
    const R = 1.45 + (r() - 0.5) * 0.05;
    s.push(Math.cos(a) * rad * R, y * R, Math.sin(a) * rad * R, K.STILL, 0, lerpC(violet, cyan, (y + 1) / 2).multiplyScalar(0.55 + r() * 0.45));
  }
  while (!s.full) {
    const a = r() * Math.PI * 2, R = 2.05 + Math.pow(r(), 1.6) * 1.05;
    const c = lerpC(mint, cyan, (R - 2.05) / 1.05).multiplyScalar(0.35 + r() * 0.6);
    s.push(Math.cos(a) * R, (r() - 0.5) * 0.04, Math.sin(a) * R, K.ORBIT, r(), c);
  }
  return s;
}

function galaxy(n) {
  const s = new Shape(n), r = rng(2);
  const core = C('#efeaff'), mid = C('#8b7bff'), rim = C('#6fd6ff');
  while (!s.full) {
    const arm = Math.floor(r() * 3), t = Math.pow(r(), 0.7), R = 0.15 + t * 3.1;
    const a = arm * (Math.PI * 2 / 3) + R * 1.35 + (r() - 0.5) * (0.5 + t * 0.4);
    const spread = (r() - 0.5) * 0.25 * (1 - t * 0.5);
    const c = (t < 0.4 ? lerpC(core, mid, t / 0.4) : lerpC(mid, rim, (t - 0.4) / 0.6)).multiplyScalar(0.5 + r() * 0.9);
    s.push(Math.cos(a) * R + spread, (r() - 0.5) * 0.14 * (1.2 - t), Math.sin(a) * R + spread, K.ORBIT, r(), c);
  }
  return s;
}

function net(n) {
  const s = new Shape(n), r = rng(3);
  const layers = [5, 8, 10, 8, 4], nodes = [];
  layers.forEach((count, li) => {
    const x = -2.1 + (4.2 * li) / (layers.length - 1);
    for (let j = 0; j < count; j++) {
      const y = (j - (count - 1) / 2) * 0.36;
      nodes.push({ li, x, y, z: -Math.cos(y * 0.8) * 0.35 + 0.35 });
    }
  });
  const nodeC = C('#efeaff'), a = C('#a78bff'), b = C('#4fe0c0');
  const perNode = Math.floor((n * 0.16) / nodes.length);
  for (const nd of nodes) {
    for (let k = 0; k < perNode; k++) {
      const u = r() * 2 - 1, th = r() * Math.PI * 2, rad = 0.075 * Math.cbrt(r()), q = Math.sqrt(1 - u * u);
      s.push(nd.x + q * Math.cos(th) * rad, nd.y + u * rad, nd.z + q * Math.sin(th) * rad, K.NODE, r(), nodeC.clone().multiplyScalar(0.6 + r() * 0.4));
    }
  }
  const edges = [];
  for (const p of nodes) for (const q of nodes) if (q.li === p.li + 1) edges.push([p, q]);
  while (!s.full) {
    const [p, q] = edges[Math.floor(r() * edges.length)], t = r();
    const c = lerpC(a, b, (p.x + t * (q.x - p.x) + 2.1) / 4.2).multiplyScalar(0.3 + r() * 0.4);
    s.push(p.x + (q.x - p.x) * t, p.y + (q.y - p.y) * t, p.z + (q.z - p.z) * t, K.EDGE, t, c);
  }
  return s;
}

// The AI Diligence mark (circuit brain), from points sampled out of the logo
// image, bent on a shallow shell, in a slowly turning cloud of dust.
function mark(n, pts) {
  if (!pts?.length) return orb(n);
  const s = new Shape(n), r = rng(7);
  const cyan = C('#6fd6ff'), violet = C('#8b7bff'), white = C('#f4f0ff');
  const nMark = Math.floor(n * 0.78);
  for (let i = 0; i < nMark; i++) {
    const [px, py] = pts[Math.floor(r() * pts.length)];
    const x = px + (r() - 0.5) * 0.018, y = py + (r() - 0.5) * 0.018;
    const z = -0.35 * x * x + (r() - 0.5) * 0.06;
    const c = lerpC(cyan, violet, (x + 1.45) / 2.9);
    s.push(x, y, z, K.SWEEP, r(), (r() < 0.08 ? white : c).clone().multiplyScalar(0.45 + r() * 0.55));
  }
  while (!s.full) {
    const u = r() * 2 - 1, a = r() * Math.PI * 2, R = 1.85 + Math.pow(r(), 1.5) * 0.9, q = Math.sqrt(1 - u * u);
    s.push(Math.cos(a) * q * R, u * R * 0.85, Math.sin(a) * q * R, K.ORBIT, r(), lerpC(violet, cyan, r()).multiplyScalar(0.12 + r() * 0.35));
  }
  return s;
}

// An AI stack seen from above: four layers (infrastructure, data, models,
// product) on a lattice, joined by vertical links, scanned from bottom to top.
function stack(n) {
  const s = new Shape(n), r = rng(8);
  const ys = [-1.05, -0.35, 0.35, 1.05], half = 1.25, step = 0.125;
  const cols = ['#4fe0c0', '#6fd6ff', '#8b7bff', '#c08bff'].map((h) => C(h));
  const nPlate = Math.floor(n * 0.17), nLink = Math.floor(n * 0.12);
  const cells = Math.round((2 * half) / step);
  ys.forEach((y, li) => {
    const c = cols[li];
    for (let i = 0; i < nPlate; i++) {
      const u = r();
      let x, z, k;
      if (u < 0.45) { // lattice nodes
        x = -half + Math.floor(r() * (cells + 1)) * step + (r() - 0.5) * 0.02;
        z = -half + Math.floor(r() * (cells + 1)) * step + (r() - 0.5) * 0.02;
        k = 0.45 + r() * 0.45;
      } else if (u < 0.72) { // plate border
        const t = (r() * 2 - 1) * half, e = r() < 0.5 ? -half : half;
        [x, z] = r() < 0.5 ? [t, e] : [e, t];
        k = 0.7 + r() * 0.3;
      } else { // faint surface
        x = (r() * 2 - 1) * half; z = (r() * 2 - 1) * half;
        k = 0.15 + r() * 0.2;
      }
      s.push(x, y + (r() - 0.5) * 0.012, z, K.SWEEP, r(), c.clone().multiplyScalar(k));
    }
  });
  const links = [];
  for (let g = 0; g < ys.length - 1; g++) {
    for (let j = 0; j < 9; j++) links.push([g, -half + Math.floor(r() * (cells + 1)) * step, -half + Math.floor(r() * (cells + 1)) * step]);
  }
  for (let i = 0; i < nLink; i++) {
    const [g, x, z] = links[Math.floor(r() * links.length)], t = r();
    s.push(x, ys[g] + t * (ys[g + 1] - ys[g]), z, K.SWEEP, t, lerpC(cols[g], cols[g + 1], t).multiplyScalar(0.55 + r() * 0.35));
  }
  while (!s.full) {
    const a = r() * Math.PI * 2, R = 1.9 + Math.pow(r(), 1.4) * 1.3;
    s.push(Math.cos(a) * R, (r() * 2 - 1) * 1.3, Math.sin(a) * R, K.ORBIT, r(), lerpC(cols[1], cols[3], r()).multiplyScalar(0.15 + r() * 0.35));
  }
  return s;
}

const BUILDERS = { orb, galaxy, net, mark, stack };

// How each shape is presented: tilt, and an optional slow sway.
const VIEW = {
  orb: { rx: 0.32, ry: 0, rz: -0.38, scale: 1 },
  galaxy: { rx: 1.05, ry: 0, rz: 0.22, scale: 1 },
  net: { rx: 0.05, ry: -0.42, rz: 0, scale: 0.8, sway: 0.18 },
  mark: { rx: 0.04, ry: -0.18, rz: 0, scale: 1.05, sway: 0.22 },
  stack: { rx: 0.5, ry: 0.62, rz: 0, scale: 0.74, sway: 0.3 },
};

/* ---------------- shaders ---------------- */

const vert = /* glsl */ `
  attribute vec4 aFrom;
  attribute vec4 aTo;
  attribute vec3 cFrom;
  attribute vec3 cTo;
  attribute vec4 aRand;
  uniform float uTime, uMix, uSize, uPixel;
  uniform vec2 uPointer;
  uniform float uAspect;
  varying vec3 vColor;
  varying float vAlpha;

  vec3 animate(vec4 p, out float boost) {
    float kind = floor(p.w), prm = fract(p.w);
    vec3 q = p.xyz;
    boost = 1.0;
    if (kind == 1.0 || kind == 2.0) { // network: a forward pass sweeps left to right
      float X = mod(uTime * 1.1, 6.5) - 3.0;
      float w = exp(-pow((q.x - X) * 3.2, 2.0));
      boost = (kind == 2.0 ? 1.0 : 0.85) + w * (kind == 2.0 ? 1.8 : 3.2);
    } else if (kind == 3.0) {     // orbit around y, inner faster
      float R = length(q.xz);
      float a = uTime * (0.32 / max(R, 0.5)) * 0.6;
      float c = cos(a), s = sin(a);
      q.xz = mat2(c, -s, s, c) * q.xz;
    } else if (kind == 4.0) {     // scan: a bright band climbs through the shape
      float Y = mod(uTime * 0.75, 4.4) - 2.2;
      float w = exp(-pow((q.y - Y) * 3.5, 2.0));
      boost = 0.8 + w * 2.4 + 0.15 * sin(uTime * 2.0 + prm * 6.28);
    }
    return q;
  }

  void main() {
    float m = clamp(uMix * 1.5 - aRand.x * 0.5, 0.0, 1.0);
    m = m * m * (3.0 - 2.0 * m);
    float bA, bB;
    vec3 a = animate(aFrom, bA);
    vec3 b = animate(aTo, bB);
    vec3 p = mix(a, b, m);
    float swirl = sin(3.14159 * m);
    p += (aRand.yzw - 0.5) * 1.6 * swirl;
    p += vec3(sin(uTime * 0.6 + aRand.y * 40.0), cos(uTime * 0.5 + aRand.z * 40.0), sin(uTime * 0.4 + aRand.w * 40.0)) * 0.012;

    vec4 mv = modelViewMatrix * vec4(p, 1.0);
    vec4 clip = projectionMatrix * mv;
    vec2 ndc = clip.xy / clip.w;
    vec2 d = (ndc - uPointer) * vec2(uAspect, 1.0);
    float f = smoothstep(0.32, 0.0, length(d));
    mv.xy += normalize(d + 1e-5) * f * 0.35;

    gl_Position = projectionMatrix * mv;
    float size = uSize * (0.55 + aRand.y * 0.9) * (1.0 + swirl * 0.6);
    gl_PointSize = size * uPixel / -mv.z;
    vColor = mix(cFrom, cTo, m);
    vAlpha = mix(bA, bB, m) * (1.0 + f * 1.2);
  }
`;

const frag = /* glsl */ `
  varying vec3 vColor;
  varying float vAlpha;
  void main() {
    float d = length(gl_PointCoord - 0.5);
    float a = smoothstep(0.5, 0.0, d);
    a = a * a + smoothstep(0.12, 0.0, d) * 0.6;
    vec3 c = vColor * a * vAlpha;
    gl_FragColor = vec4(c, max(c.r, max(c.g, c.b))); // premultiplied: light added over the page
  }
`;

/* ---------------- field ---------------- */

export class Field {
  constructor(canvas, { count, reduced, markPoints, start = 'mark' }) {
    this.reduced = reduced;
    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: false, alpha: true, powerPreference: 'high-performance' });
    this.dpr = Math.min(devicePixelRatio || 1, 1.75);
    this.renderer.setPixelRatio(this.dpr);
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(40, 1, 0.1, 100);
    this.camera.position.set(0, 0, 7.2);

    this.n = count;
    this.shapes = {};
    for (const [k, fn] of Object.entries(BUILDERS)) this.shapes[k] = fn(count, markPoints);

    const g = new THREE.BufferGeometry();
    const rand = new Float32Array(count * 4), r = rng(99);
    for (let i = 0; i < rand.length; i++) rand[i] = r();
    const first = this.shapes[start];
    g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(count * 3), 3));
    g.setAttribute('aFrom', new THREE.BufferAttribute(first.pos.slice(), 4));
    g.setAttribute('aTo', new THREE.BufferAttribute(first.pos.slice(), 4));
    g.setAttribute('cFrom', new THREE.BufferAttribute(first.col.slice(), 3));
    g.setAttribute('cTo', new THREE.BufferAttribute(first.col.slice(), 3));
    g.setAttribute('aRand', new THREE.BufferAttribute(rand, 4));
    g.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 50);
    this.geo = g;
    this.rand = rand;

    this.uniforms = {
      uTime: { value: 0 }, uMix: { value: 1 }, uSize: { value: count > 12000 ? 20 : 24 },
      uPixel: { value: this.dpr }, uPointer: { value: new THREE.Vector2(9, 9) }, uAspect: { value: 1 },
    };
    const mat = new THREE.ShaderMaterial({
      vertexShader: vert, fragmentShader: frag, uniforms: this.uniforms,
      transparent: true, depthWrite: false, blending: THREE.CustomBlending,
      blendSrc: THREE.OneFactor, blendDst: THREE.OneFactor, blendSrcAlpha: THREE.OneFactor, blendDstAlpha: THREE.OneFactor,
    });
    this.points = new THREE.Points(g, mat);
    this.pivot = new THREE.Group();
    this.holder = new THREE.Group();
    this.pivot.add(this.points);
    this.holder.add(this.pivot);
    this.scene.add(this.holder);

    this.current = start;
    this.side = 0;
    this.pointer = new THREE.Vector2(9, 9);
    this.look = new THREE.Vector2();
    this.scrollSpin = 0;
    this.resize();
    addEventListener('resize', () => this.resize());
    addEventListener('pointermove', (e) => {
      this.pointer.set((e.clientX / innerWidth) * 2 - 1, -(e.clientY / innerHeight) * 2 + 1);
    }, { passive: true });
    document.addEventListener('pointerleave', () => this.pointer.set(9, 9));
    this.applyView(true);
  }

  resize() {
    const w = innerWidth, h = innerHeight;
    if (this.lastW === w && Math.abs((this.lastH || 0) - h) < 150) return; // mobile URL bar
    this.lastW = w; this.lastH = h;
    this.renderer.setSize(w, h, false);
    this.camera.aspect = w / h;
    this.camera.fov = w / h < 0.8 ? 52 : 40;
    this.camera.updateProjectionMatrix();
    this.uniforms.uAspect.value = w / h;
    this.applyView(true);
  }

  /** Visible half-size of the z = 0 plane. */
  frame() {
    const hh = Math.tan(THREE.MathUtils.degToRad(this.camera.fov / 2)) * this.camera.position.z;
    return { hw: hh * this.camera.aspect, hh };
  }

  /** Placement for a side (-1 left, 0 centre, 1 right) — away from the text card. */
  placement(side) {
    const { hw, hh } = this.frame(), portrait = this.camera.aspect < 0.9;
    if (side === 0) return { x: 0, y: -hh * 0.62, s: portrait ? 0.75 : 1.25 }; // a horizon under centred text
    if (portrait) return { x: 0, y: hh * 0.4, s: Math.min(1, hw / 2.6) * 0.95 };
    return { x: side * hw * 0.48, y: 0, s: THREE.MathUtils.clamp(hw / 3.8, 0.6, 1.1) };
  }

  applyView(instant) {
    const v = VIEW[this.current], p = this.placement(this.side);
    const to = { x: p.x, y: p.y };
    const sc = v.scale * p.s;
    const rot = { x: v.rx, y: v.ry, z: v.rz };
    if (instant) {
      this.holder.position.set(to.x, to.y, 0);
      this.holder.scale.setScalar(sc);
      this.pivot.rotation.set(rot.x, rot.y, rot.z);
      return;
    }
    gsap.to(this.holder.position, { ...to, duration: 1.8, ease: 'power3.inOut', overwrite: true });
    gsap.to(this.holder.scale, { x: sc, y: sc, z: sc, duration: 1.8, ease: 'power3.inOut', overwrite: true });
    gsap.to(this.pivot.rotation, { ...rot, duration: 2.2, ease: 'power3.inOut', overwrite: true });
  }

  /** Fly to a shape, starting from wherever the particles are now. */
  morphTo(name, side) {
    if (!this.shapes[name]) return;
    if (name === this.current && side === this.side) return;
    this.side = side;
    if (name === this.current) { this.applyView(false); return; }
    const aF = this.geo.attributes.aFrom, aT = this.geo.attributes.aTo;
    const cF = this.geo.attributes.cFrom, cT = this.geo.attributes.cTo;
    const mix = this.uniforms.uMix.value;
    if (mix >= 1) {
      aF.array.set(aT.array);
      cF.array.set(cT.array);
    } else {
      for (let i = 0; i < this.n; i++) {
        let m = Math.min(1, Math.max(0, mix * 1.5 - this.rand[i * 4] * 0.5));
        m = m * m * (3 - 2 * m);
        for (let k = 0; k < 3; k++) {
          aF.array[i * 4 + k] += (aT.array[i * 4 + k] - aF.array[i * 4 + k]) * m;
          cF.array[i * 3 + k] += (cT.array[i * 3 + k] - cF.array[i * 3 + k]) * m;
        }
        if (m >= 0.5) aF.array[i * 4 + 3] = aT.array[i * 4 + 3];
      }
    }
    aT.array.set(this.shapes[name].pos);
    cT.array.set(this.shapes[name].col);
    aF.needsUpdate = aT.needsUpdate = cF.needsUpdate = cT.needsUpdate = true;
    this.current = name;
    this.uniforms.uMix.value = 0;
    gsap.to(this.uniforms.uMix, { value: 1, duration: this.reduced ? 0.01 : 2.4, ease: 'power2.inOut', overwrite: true });
    this.applyView(false);
  }

  update(t, scrollVel) {
    this.uniforms.uTime.value = this.reduced ? 0 : t;
    this.uniforms.uPointer.value.lerp(this.pointer, 0.12);
    this.look.lerp(this.pointer.x > 5 ? new THREE.Vector2() : this.pointer, 0.04);
    const v = VIEW[this.current];
    this.scrollSpin += (THREE.MathUtils.clamp(scrollVel * 0.0006, -0.06, 0.06) - this.scrollSpin) * 0.08;
    this.holder.rotation.y += this.scrollSpin;
    this.holder.rotation.y *= 0.985;
    if (v.sway && !this.reduced) this.pivot.rotation.y = v.ry + Math.sin(t * 0.25) * v.sway;
    this.camera.position.x = this.look.x * 0.35;
    this.camera.position.y = this.look.y * 0.22;
    this.camera.lookAt(0, 0, 0);
    this.renderer.render(this.scene, this.camera);
  }
}

/** Points of the logo's opaque pixels, centred, 2.9 units tall. */
export async function markPoints(src) {
  const img = new Image();
  img.src = src;
  await img.decode();
  const w = img.naturalWidth, h = img.naturalHeight, cv = document.createElement('canvas');
  cv.width = w; cv.height = h;
  const ctx = cv.getContext('2d');
  ctx.drawImage(img, 0, 0);
  const data = ctx.getImageData(0, 0, w, h).data, k = 2.9 / h, pts = [];
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) if (data[(y * w + x) * 4 + 3] > 128) pts.push([(x - w / 2) * k, (h / 2 - y) * k]);
  }
  return pts;
}
