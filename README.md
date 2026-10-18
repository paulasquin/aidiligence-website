# aidiligence.eu

Static site for AI Diligence, in the visual language of [paulasquin.com](https://paulasquin.com):
dark stage, a three.js particle field that changes shape from section to section, GSAP
(ScrollTrigger) reveals and Lenis smooth scrolling. French and English, language picked
automatically. The `revela.` and `siflo.` subdomains are separate sites, not served from here.

No build step at runtime: three.js 0.186 via an import map, GSAP 3.15 and Lenis 1.3 from
jsDelivr, fonts (Unbounded, Inter, JetBrains Mono) from Google Fonts.

## Build

```bash
python3 tools/build.py
```

The Python 3 standard library is enough. All page content lives in `tools/build.py`, as
(French, English) pairs. The build writes:

- `index.html` — French text, each translatable element tagged `data-i18n="key"`;
- `assets/js/strings.js` — the English of every key (generated, do not edit by hand);
- `404.html` and `about/index.html` (redirect to `/#about`).

Edit the content in `tools/build.py`, run the build, commit the generated files.

## Preview

```bash
python3 -m http.server 8767 --bind 127.0.0.1
```

Then <http://127.0.0.1:8767/> — `?lang=en` / `?lang=fr` force a language, `?debug` exposes
`window.__field`.

## Structure

- `assets/css/style.css` — styles (shared conventions with paulasquin.com).
- `assets/js/main.js` — smooth scroll, reveals, nav, pointer effects, boot.
- `assets/js/i18n.js` — language handling (from `paulasquin/showcase-kit`). The inline script
  in `<head>` picks the language before first paint: `?lang=`, then the visitor's saved
  choice, then the browser languages; English is applied from `strings.js` at boot.
- `assets/js/field.js` — the particle field, adapted from paulasquin.com. Each section names
  a shape (`data-shape`) and the side of the screen it sits on (`data-side`: -1, 0, 1).
  Shapes: `mark` (the AI Diligence logo, sampled at runtime from
  `assets/img/ai-diligence-mark.png`), `galaxy`, `stack` (four layers of an AI stack scanned
  from bottom to top), `net` (neural network with a forward pass), `orb`. Every shape must
  fill exactly `n` particles.
- `assets/og.jpg` — capture of the hero at 1200×630, used for link previews.

## Deployment

GitHub Pages, `main` branch, repository root. The domain is declared by the `CNAME` file.
