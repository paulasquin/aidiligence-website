import { registerStrings, applyStatic } from './i18n.js';
import { STATIC_EN } from './strings.js';

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
const fine = matchMedia('(hover: hover) and (pointer: fine)').matches;

document.documentElement.classList.add('js');
registerStrings(STATIC_EN);
applyStatic();
const track = $('.marquee-track');
track.innerHTML += track.innerHTML; // two copies for a seamless loop

gsap.registerPlugin(ScrollTrigger);
ScrollTrigger.config({ ignoreMobileResize: true });

/* ---------------- smooth scroll ---------------- */
const lenis = reduced ? null : new Lenis({ lerp: 0.09, wheelMultiplier: 0.9 });
if (lenis) {
  lenis.on('scroll', ScrollTrigger.update);
  gsap.ticker.add((time) => lenis.raf(time * 1000));
  gsap.ticker.lagSmoothing(0);
}
$$('a[href^="#"]').forEach((a) => a.addEventListener('click', (e) => {
  const id = a.getAttribute('href');
  if (id.length < 2 || !$(id)) return;
  e.preventDefault();
  lenis ? lenis.scrollTo(id, { duration: 1.8 }) : $(id).scrollIntoView({ behavior: 'smooth' });
}));

/* ---------------- particle field ---------------- */
function webglOK() {
  try { return !!document.createElement('canvas').getContext('webgl2'); } catch (e) { return false; }
}

async function setupField() {
  if (!webglOK()) { document.documentElement.classList.add('no-webgl'); return; }
  const { Field } = await import('./field.js');
  const small = innerWidth < 860 || (navigator.hardwareConcurrency || 8) <= 4;
  const field = new Field($('#field'), { count: small ? 9000 : 22000, reduced });
  if (location.search.includes('debug')) window.__field = field;
  let vel = 0;
  lenis?.on('scroll', (l) => { vel = l.velocity; });
  gsap.ticker.add((time) => { if (!document.hidden) field.update(time, vel); });
  $$('.scene[data-shape]').forEach((sec) => ScrollTrigger.create({
    trigger: sec, start: 'top 55%', end: 'bottom 55%',
    onToggle: (self) => self.isActive && field.morphTo(sec.dataset.shape, Number(sec.dataset.side)),
  }));
}

/* ---------------- brand intro ---------------- */
// The whole wheel rolls in from the right edge without slipping (whole turns, so it
// stops as drawn), the name appears behind it, then its back half fades and
// the axle grows from the hub: the logo. Any input speeds it up.
async function brandIntro() {
  const root = document.documentElement;
  if (!root.classList.contains('intro')) return;
  try { sessionStorage.setItem('intro', '1'); } catch (e) { /* private mode */ }
  const ov = $('.intro-overlay'), wheel = $('.intro-wheel'), text = $('.intro-text');
  const roll = $('.iw-roll', wheel), back = $('.iw-back', wheel), axle = $('.iw-axle', wheel);
  await document.fonts.ready;
  const w = wheel.getBoundingClientRect(), t = text.getBoundingClientRect();
  const R = (w.width / 2) * (48.25 / 49.25); // the tire's outer radius
  const cx = w.left + w.width / 2;
  const turns = Math.max(1, Math.ceil((Math.max(innerWidth, t.right + R) - cx + R) / (2 * Math.PI * R))); // in from the screen edge
  const reveal = () => {
    const hidden = Math.min(t.width, Math.max(0, cx + gsap.getProperty(wheel, 'x') + R - t.left)); // behind the rim
    text.style.clipPath = `inset(-20% 0 -20% ${hidden}px)`;
  };
  gsap.set(wheel, { x: 2 * Math.PI * R * turns, visibility: 'visible' });
  gsap.set(roll, { svgOrigin: '0 0', rotation: 0 });
  gsap.set(axle, { svgOrigin: '0 0', scaleY: 0 });
  reveal();
  await new Promise((resolve) => {
    const tl = gsap.timeline({ onComplete: resolve });
    tl.fromTo(wheel, { opacity: 0 }, { opacity: 1, duration: 0.35 }, 0)
      .to(wheel, { x: 0, duration: 2.4, ease: 'power2.out', onUpdate: reveal }, 0)
      .to(roll, { rotation: -360 * turns, duration: 2.4, ease: 'power2.out' }, 0)
      .to(roll, { rotation: -360 * turns + 6, duration: 0.16, ease: 'power1.out' })
      .to(roll, { rotation: -360 * turns, duration: 0.6, ease: 'elastic.out(1, 0.45)' })
      .to(back, { opacity: 0, duration: 0.5, ease: 'power2.out' }, '-=0.55')
      .to(axle, { scaleY: 1, duration: 0.65, ease: 'back.out(2)' }, '<')
      .to(ov, { opacity: 0, duration: 0.7, ease: 'power2.inOut' }, '+=0.45');
    const skip = () => tl.timeScale(6);
    ['pointerdown', 'keydown', 'wheel', 'touchstart'].forEach((e) => addEventListener(e, skip, { once: true, passive: true }));
  });
  root.classList.remove('intro');
  ov.remove();
}

/* ---------------- hero intro ---------------- */
function heroIntro() {
  document.body.classList.remove('is-loading');
  if (reduced) return;
  const tl = gsap.timeline({ defaults: { ease: 'power4.out' } });
  tl.fromTo('.topnav', { opacity: 0, y: -20 }, { opacity: 1, y: 0, duration: 1.2 }, 0.2)
    .fromTo('.ht-word', { yPercent: 115, letterSpacing: '0.12em' }, { yPercent: 0, letterSpacing: '-0.045em', duration: 1.6, stagger: 0.14 }, 0.1)
    .fromTo(['.hero .eyebrow', '.service-lines li', '.hero .hero-cta', '.scroll-cue'], { opacity: 0, y: 26 }, { opacity: 1, y: 0, duration: 1.2, stagger: 0.1 }, 0.6)
    .add(() => gsap.set(['.ht-word', '.hero .eyebrow', '.service-lines li', '.hero .hero-cta', '.scroll-cue', '.topnav'], { clearProps: 'transform' }));
  // Safety net: Android Chrome has been seen freezing intros.
  setTimeout(() => { if (tl.progress() < 1) tl.progress(1); }, 4000);
}

/* ---------------- reveals ---------------- */
function reveals() {
  if (reduced) return;
  $$('.reveal').forEach((el) => {
    gsap.fromTo(el, { opacity: 0, y: 40 }, {
      opacity: 1, y: 0, duration: 1.2, ease: 'power3.out', clearProps: 'transform',
      scrollTrigger: { trigger: el, start: 'top 88%', once: true },
    });
    const kids = $$('.kicker, .title, .lede, .focus-item, .caps li, .facts li, .hero-cta, .card-cta', el);
    if (kids.length) {
      gsap.fromTo(kids, { opacity: 0, y: 18, clipPath: 'inset(0 0 100% 0)' }, {
        opacity: 1, y: 0, clipPath: 'inset(0 0 -20% 0)', duration: 1, ease: 'power3.out', stagger: 0.06,
        clearProps: 'clipPath,transform',
        scrollTrigger: { trigger: el, start: 'top 80%', once: true },
      });
    }
  });
}

/* ---------------- nav + progress ---------------- */
function chrome() {
  const nav = $('.topnav'), bar = $('.scroll-progress span');
  ScrollTrigger.create({
    start: 0, end: 'max',
    onUpdate: (self) => {
      nav.classList.toggle('scrolled', self.scroll() > 40);
      bar.style.transform = `scaleX(${self.progress})`;
    },
  });
  $$('.nav-links a[href^="#"]').forEach((a) => {
    const sec = $(a.getAttribute('href'));
    ScrollTrigger.create({ trigger: sec, start: 'top 50%', end: 'bottom 50%', onToggle: (s) => a.classList.toggle('on', s.isActive) });
  });
}

/* ---------------- pointer effects ---------------- */
function pointerFx() {
  if (!fine || reduced) return;
  $$('.card, .tile').forEach((el) => el.addEventListener('pointermove', (e) => {
    const r = el.getBoundingClientRect();
    el.style.setProperty('--mx', `${e.clientX - r.left}px`);
    el.style.setProperty('--my', `${e.clientY - r.top}px`);
  }));
  $$('.tile').forEach((el) => {
    el.addEventListener('pointermove', (e) => {
      const r = el.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
      gsap.to(el, { rotateY: x * 7, rotateX: -y * 7, transformPerspective: 900, duration: 0.6, ease: 'power2.out' });
    });
    el.addEventListener('pointerleave', () => gsap.to(el, { rotateY: 0, rotateX: 0, duration: 0.9, ease: 'elastic.out(1, 0.5)' }));
  });
  $$('.magnetic').forEach((el) => {
    const xTo = gsap.quickTo(el, 'x', { duration: 0.5, ease: 'power3.out' });
    const yTo = gsap.quickTo(el, 'y', { duration: 0.5, ease: 'power3.out' });
    el.addEventListener('pointermove', (e) => {
      const r = el.getBoundingClientRect();
      xTo((e.clientX - r.left - r.width / 2) * 0.25);
      yTo((e.clientY - r.top - r.height / 2) * 0.35);
    });
    el.addEventListener('pointerleave', () => { xTo(0); yTo(0); });
  });
}

/* ---------------- boot ---------------- */
chrome();
pointerFx();
reveals();
setupField();
brandIntro().finally(heroIntro);

let y = null;
try { y = sessionStorage.getItem('scrollY'); sessionStorage.removeItem('scrollY'); } catch (e) { /* private mode */ }
if (y) requestAnimationFrame(() => (lenis ? lenis.scrollTo(Number(y), { immediate: true }) : scrollTo(0, Number(y))));
