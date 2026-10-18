# aidiligence.eu

Site of AI Diligence, the AI services of Guardia SAS: AI project leadership (the *conduite* of
the name — a diligence is also a stagecoach), AI and MLOps engineering, and AI due diligence.
Sections: services, method, references (missions, then the founder's experience), the eight
due-diligence focus areas, expertise, products (Revela, Siflo), founder, contact.

Same visual language as [paulasquin.com](https://paulasquin.com): dark stage, a three.js
particle field that changes shape from section to section, GSAP (ScrollTrigger) reveals and
Lenis smooth scrolling. French and English, language picked automatically. The `revela.` and
`siflo.` subdomains are separate sites, not served from here.

**aidiligence.eu and paulasquin.com.** This site is the company; paulasquin.com
([paulasquin/paulasquin-site](https://github.com/paulasquin/paulasquin-site)) is the person:
career, projects, talks. Each fact lives on one site and the other links to it: the career is
only summed up here (references link to paulasquin.com's anchors), the services only summed up
there. The four founder facts are the one deliberate duplicate — keep them in step with
paulasquin.com's About card. Nothing is shared at runtime, since this site loads nothing from
other domains (below).

No external request at runtime — the legal notice says so, keep it true. Everything is served
from this repository:

- `assets/vendor/` — three.js 0.186.1 (`three.module.js` + `three.core.js`, the jsDelivr
  minified builds, renamed so the module's `./three.core.js` import resolves; mapped by the
  import map), GSAP 3.15.0 + ScrollTrigger, Lenis 1.3.27.
- `assets/fonts/` — Unbounded, Inter and JetBrains Mono, latin subset of the Google Fonts
  variable files (SIL Open Font License).

To upgrade a library, download the new pinned build into `assets/vendor/` under the same name.

## Build

```bash
python3 tools/build.py
```

The Python 3.12+ standard library is enough. All page content lives in `tools/build.py`, as
(French, English) pairs. The build writes:

- `index.html` — French text, each translatable element tagged `data-i18n="key"`;
- `assets/js/strings.js` — the English of every key (generated, do not edit by hand);
- `legal/index.html` (mentions légales, publisher in `PUBLISHER`), `404.html` and
  `about/index.html` (redirect to `/#about`).

Edit the content in `tools/build.py`, run the build, commit the generated files.

## Preview

```bash
python3 -m http.server 8767 --bind 127.0.0.1
```

Then <http://127.0.0.1:8767/> — `?lang=en` / `?lang=fr` force a language, `?debug` exposes
`window.__field`.

## Structure

- `assets/css/style.css` — styles (shared conventions with paulasquin.com).
- `assets/js/main.js` — brand intro, smooth scroll, reveals, nav, pointer effects, boot.
- `assets/js/i18n.js` — language handling (from `paulasquin/showcase-kit`). The inline script
  in `<head>` picks the language before first paint: `?lang=`, then the visitor's saved
  choice, then the browser languages; English is applied from `strings.js` at boot.
- `assets/js/field.js` — the particle field, adapted from paulasquin.com. Each section names
  a shape (`data-shape`) and the side of the screen it sits on (`data-side`: -1, 0, 1).
  Shapes: `mark` (the AI Diligence logo, drawn with the proportions of `tools/logo.py`,
  a pulse running from the hub out along the spokes), `galaxy`, `stack` (four layers of an AI stack scanned
  from bottom to top), `path` (the method's road: two wheel tracks and four staging posts, a
  pulse running along it), `net` (neural network with a forward pass), `orb`. Every shape must
  fill exactly `n` particles.
- `assets/og.jpg` — capture of the hero at 1200×630, used for link previews.

## Logo

Half a stagecoach wheel standing on its axle, which draws the D of Diligence: the axle is
the stem, the hub sits on it with its cap, five tapered spokes reach a wooden felloe bolted to
its iron tire — the stagecoach of the name, and an analysis that starts from one point and
covers the whole picture. The hub, the double rim and the bolts are what keep it a wheel
(a first version with four thick spokes read as a lemon slice).

```bash
uv run -q --with fonttools --with brotli --with playwright python tools/logo.py
```

writes `brand/` — mark and lockup as SVG and PNG, for dark (`-dark-bg`) and light
(`-light-bg`) backgrounds, and `aidiligence-linkedin-logo.png` (1200×1200, the mark on the
site's dark background) — plus the site icons `assets/img/mark.svg`, `favicon.svg` (follows
the browser theme) and `icon-256.png`. The lockup's text is outlined from Unbounded, so the
SVGs need no font. Colours: `#6fd6ff` → `#8b7bff` gradient, ink `#eceaf6` on dark,
`#14162b` on light.

### LinkedIn banners

```bash
uv run -q --with playwright python tools/banners.py
```

renders `tools/banner.html` — the hero's particle wheel and the site's copy — into
`brand/linkedin-banner-profile-{fr,en}.png` (personal profile, 1584 × 396) and
`brand/linkedin-banner-company-{fr,en}.png` (company page, 1128 × 191), at twice those sizes
for high-density screens. The bottom left is left empty: LinkedIn puts the profile photo and
the page logo there.

### Intro

The home page's nav logo is the whole wheel (`tools/brand-wheel.svg`, written by
`tools/logo.py`, inlined by `tools/build.py`); at rest its back half is hidden, which leaves
the mark. On a visitor's first page of the session it plays, without covering anything: drawn
large in the header, the wheel rolls in from past the name without slipping (whole turns, so
it stops as drawn), the name appears behind it, its back half fades and the axle grows from
the hub, then the logo shrinks to its place in the nav. The page is usable meanwhile; a click,
a key or a scroll speeds it up. Skipped after the language switch, on a link to an anchor and
with `prefers-reduced-motion`; if the script has not started within 6 s the logo is shown at
rest. The timeline is `brandIntro()` in `assets/js/main.js`. To see it again:
`sessionStorage.removeItem('intro')`, then reload.

The particle field builds its first shape at once and the others when the browser is idle:
building them all together held the main thread long enough to make the roll jump.

## Deployment

GitHub Pages, `main` branch, repository root. The domain is declared by the `CNAME` file.

`google3019c1d90aa83ac3.html` proves ownership of the site to Google Search Console (used for the
Google Play developer account). Keep it at the root, unchanged: removing it loses the verification.
