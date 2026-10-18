#!/usr/bin/env python3
"""Draw the AI Diligence logo and export it.

The mark is half a stagecoach wheel standing on its axle, which draws the D
of Diligence: the stem is the axle, the hub sits on it with its cap, five
tapered spokes reach a rim made of a wooden felloe and its iron tire, bolted
together. Everything is computed here, so a change of proportion is a change
of the constants below.

Writes:
- brand/*.svg — mark and lockup, for dark and for light backgrounds; the
  lockup's text is outlined from assets/fonts/unbounded-latin.woff2;
- brand/*.png — the same, rendered by headless Chrome, plus square avatars:
  aidiligence-linkedin-logo.png (the mark centred as a shape) and
  aidiligence-avatar-centred.png (the hub at the centre, for round crops);
- brand/mark-centred-*.svg — the mark in a square centred on the hub;
- assets/img/mark.svg (the nav), assets/img/favicon.svg (follows the browser's light / dark theme) and
  assets/img/icon-256.png (the avatar, for touch icons) — the site icons.
- tools/brand-wheel.svg — the whole wheel, inlined by tools/build.py as the
  home page's nav logo, which rolls in on arrival.

Usage: uv run -q --with fonttools --with brotli --with playwright python tools/logo.py
(Playwright renders with the installed Chrome: channel="chrome".)
"""

import math
import os

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAND = os.path.join(ROOT, "brand")

CYAN, VIOLET = "#6fd6ff", "#8b7bff"
INK_DARK_BG, INK_LIGHT_BG = "#eceaf6", "#14162b"
BG = "#04050c"

# Mark geometry, in a 128 × 128 box.
AXLE_X, HUB_Y, RIM_R = 46, 64, 46    # RIM_R: centre line of the tire
AXLE = 10                            # stem width
TIRE, FELLOE, RIM_GAP = 4.5, 7, 3.0  # iron tire, wooden felloe inside it, gap between
HUB_R, HUB_HOLE, CAP_R = 13, 8.5, 4.5
SPOKES = 5                           # in the half wheel: a 12-spoke wheel
SPOKE_HUB, SPOKE_RIM = 6, 3.6        # spoke width at the hub and at the felloe
BOLT_R = 2


def gradient(gid, x1, y1, x2, y2):
    return (f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{x1}" y1="{y1}" '
            f'x2="{x2}" y2="{y2}"><stop offset="0" stop-color="{CYAN}"/>'
            f'<stop offset="1" stop-color="{VIOLET}"/></linearGradient>')


def mark_paths(ink, gid="g"):
    """The mark's shapes and its gradient; ink None: the axle and hub take class "ink"."""
    x, y, r = AXLE_X, HUB_Y, RIM_R
    fill = f'fill="{ink}"' if ink else 'class="ink"'
    stroke = f'stroke="{ink}"' if ink else 'class="ink"'
    rf = r - TIRE / 2 - RIM_GAP - FELLOE / 2      # centre line of the felloe
    angles = [-90 + 180 * (i + 1) / (SPOKES + 1) for i in range(SPOKES)]
    arc = lambda rr: f"M{x} {y - rr:g} A{rr:g} {rr:g} 0 0 1 {x} {y + rr:g}"
    bolts = "".join(f'<circle cx="{x + rf * math.cos(math.radians(a)):.2f}" '
                    f'cy="{y + rf * math.sin(math.radians(a)):.2f}" r="{BOLT_R}" fill="black"/>'
                    for a in angles)
    out = [f"<defs>{gradient(gid, x - 16, y - r - 2, x + 50, y + r + 2)}"
           f'<mask id="{gid}b" maskUnits="userSpaceOnUse" x="0" y="0" width="128" height="128">'
           f'<rect width="128" height="128" fill="white"/>{bolts}</mask></defs>',
           f'<path d="{arc(r)}" fill="none" stroke="url(#{gid})" stroke-width="{TIRE}" stroke-linecap="round"/>',
           f'<path d="{arc(rf)}" fill="none" stroke="url(#{gid})" stroke-width="{FELLOE}" mask="url(#{gid}b)"/>']
    r1 = rf - FELLOE / 2 + 0.5
    for a in angles:
        c, s_ = math.cos(math.radians(a)), math.sin(math.radians(a))
        pts = [(x + c * rr + s_ * w / 2 * k, y + s_ * rr - c * w / 2 * k)
               for rr, w, k in ((HUB_HOLE, SPOKE_HUB, 1), (r1, SPOKE_RIM, 1), (r1, SPOKE_RIM, -1), (HUB_HOLE, SPOKE_HUB, -1))]
        out.append('<path d="M' + " L".join(f"{px:.2f} {py:.2f}" for px, py in pts) + f' Z" fill="url(#{gid})"/>')
    end = HUB_HOLE + AXLE / 2 + 0.5  # the axle stops under the hub ring, its hole stays open
    for y0, y1 in ((y - r, y - end), (y + end, y + r)):
        out.append(f'<line x1="{x}" y1="{y0:g}" x2="{x}" y2="{y1:g}" {stroke} '
                   f'stroke-width="{AXLE}" stroke-linecap="round"/>')
    ring = lambda rr: f"M{x - rr} {y} a{rr} {rr} 0 1 0 {2 * rr} 0 a{rr} {rr} 0 1 0 {-2 * rr} 0Z"
    out.append(f'<path d="{ring(HUB_R)}{ring(HUB_HOLE)}" fill-rule="evenodd" {fill}/>')
    out.append(f'<path d="{ring(CAP_R)}" {fill}/>')
    return "".join(out)


def svg(w, h, body, title="AI Diligence"):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" '
            f'height="{h}" role="img" aria-label="{title}"><title>{title}</title>{body}</svg>\n')


def mark_svg(ink):
    return svg(128, 128, mark_paths(ink))


# Centred on the hub, for round crops (LinkedIn, Instagram): the rim is then
# concentric with the circle the network draws around the picture.
CENTRED_HALF = RIM_R + TIRE / 2 + 6


def mark_centred_svg(ink):
    h = CENTRED_HALF
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{AXLE_X - h:g} {HUB_Y - h:g} {2 * h:g} {2 * h:g}" '
            f'width="128" height="128" role="img" aria-label="AI Diligence"><title>AI Diligence</title>'
            f'{mark_paths(ink)}</svg>\n')


def favicon_svg():
    """Ink stem on light browser chrome, light stem on dark."""
    style = (f"<style>path.ink{{fill:{INK_LIGHT_BG}}}line.ink{{stroke:{INK_LIGHT_BG}}}"
             f"@media (prefers-color-scheme: dark){{path.ink{{fill:{INK_DARK_BG}}}"
             f"line.ink{{stroke:{INK_DARK_BG}}}}}</style>")
    return svg(128, 128, style + mark_paths(None))


def wheel_svg(ink):
    """The whole wheel, hub at (0, 0): the home page's nav logo (assets/js/main.js).

    .iw-roll turns while the svg moves; its .iw-back half fades out once the
    wheel stops and .iw-axle grows from the hub: what is left is the mark. At
    rest (the stylesheet's default) .iw-back is hidden: the mark as drawn.
    """
    r = RIM_R
    rf = r - TIRE / 2 - RIM_GAP - FELLOE / 2
    r1 = rf - FELLOE / 2 + 0.5
    pol = lambda rr, a: (rr * math.cos(math.radians(a)), rr * math.sin(math.radians(a)))
    bolts = "".join('<circle cx="%.2f" cy="%.2f" r="%g" fill="black"/>' % (*pol(rf, a), BOLT_R)
                    for a in range(0, 360, 30))

    def spoke(a):
        c, s_ = math.cos(math.radians(a)), math.sin(math.radians(a))
        pts = [(c * rr + s_ * w / 2 * k, s_ * rr - c * w / 2 * k)
               for rr, w, k in ((HUB_HOLE, SPOKE_HUB, 1), (r1, SPOKE_RIM, 1), (r1, SPOKE_RIM, -1), (HUB_HOLE, SPOKE_HUB, -1))]
        return '<path d="M' + " L".join(f"{px:.2f} {py:.2f}" for px, py in pts) + '" fill="url(#iwg)"/>'

    def half(sign):  # sign 1: the right half (it stays), -1: the left one
        arc = lambda rr: f"M0 {-sign * rr:g} A{rr:g} {rr:g} 0 0 1 0 {sign * rr:g}"
        spokes = "".join(spoke(a if sign > 0 else a + 180) for a in (-60, -30, 0, 30, 60))
        if sign < 0:
            spokes += spoke(90) + spoke(-90)  # the axle takes their place
        return (f'<path d="{arc(r)}" fill="none" stroke="url(#iwg)" stroke-width="{TIRE}" stroke-linecap="round"/>'
                f'<path d="{arc(rf)}" fill="none" stroke="url(#iwg)" stroke-width="{FELLOE}" mask="url(#iwb)"/>'
                + spokes)

    end = HUB_HOLE + AXLE / 2 + 0.5
    ring = lambda rr: f"M{-rr} 0 a{rr} {rr} 0 1 0 {2 * rr} 0 a{rr} {rr} 0 1 0 {-2 * rr} 0Z"
    o = r + TIRE / 2 + 1
    return (f'<svg class="brand-wheel" viewBox="{-o:g} {-o:g} {2 * o:g} {2 * o:g}" aria-hidden="true">'
            f"<defs>{gradient('iwg', -16, -r - 2, 50, r + 2)}"
            f'<mask id="iwb" maskUnits="userSpaceOnUse" x="{-o:g}" y="{-o:g}" width="{2 * o:g}" height="{2 * o:g}">'
            f'<rect x="{-o:g}" y="{-o:g}" width="{2 * o:g}" height="{2 * o:g}" fill="white"/>{bolts}</mask></defs>'
            f'<g class="iw-roll"><g class="iw-back">{half(-1)}</g><g class="iw-front">{half(1)}</g></g>'
            f'<g class="iw-axle"><line x1="0" y1="{-r}" x2="0" y2="{-end:g}" stroke="{ink}" stroke-width="{AXLE}" stroke-linecap="round"/>'
            f'<line x1="0" y1="{end:g}" x2="0" y2="{r}" stroke="{ink}" stroke-width="{AXLE}" stroke-linecap="round"/></g>'
            f'<path d="{ring(HUB_R)}{ring(HUB_HOLE)}" fill-rule="evenodd" fill="{ink}"/>'
            f'<path d="{ring(CAP_R)}" fill="{ink}"/></svg>\n')


# --------------------------------------------------------------------------- #
# Wordmark: "AI" bold in the gradient, "Diligence" regular in ink
# --------------------------------------------------------------------------- #

def load_font(weight):
    font = TTFont(os.path.join(ROOT, "assets/fonts/unbounded-latin.woff2"))
    return instantiateVariableFont(font, {"wght": weight})


def text_path(font, text, x, baseline, size, tracking=0.0):
    """Outline `text` from `font`; returns (svg path data, end x)."""
    cmap, gs, hmtx = font.getBestCmap(), font.getGlyphSet(), font["hmtx"]
    k = size / font["head"].unitsPerEm
    pen = SVGPathPen(gs)
    for ch in text:
        name = cmap[ord(ch)]
        gs[name].draw(TransformPen(pen, (k, 0, 0, -k, x, baseline)))
        x += hmtx[name][0] * k + tracking * size
    return pen.getCommands(), x


def lockup_svg(ink):
    bold, regular = load_font(700), load_font(400)
    size = 58
    cap = bold["OS/2"].sCapHeight * size / bold["head"].unitsPerEm
    baseline = HUB_Y + cap / 2
    left = AXLE_X - HUB_R - 4  # crop the mark's box to the hub
    x0 = AXLE_X + RIM_R + TIRE / 2 + 22
    ai, x = text_path(bold, "AI", x0, baseline, size, -0.02)
    x += regular["hmtx"]["space"][0] * size / regular["head"].unitsPerEm * 0.9
    dil, x = text_path(regular, "Diligence", x, baseline, size, -0.02)
    w = math.ceil(x + 8 - left)
    body = (f'<g transform="translate({-left} 0)">' + mark_paths(ink)
            + f"<defs>{gradient('t', x0, baseline - cap, x0 + 2.2 * size, baseline)}</defs>"
            + f'<path d="{ai}" fill="url(#t)"/><path d="{dil}" fill="{ink}"/></g>')
    return svg(w, 128, body)


def avatar_html(size):
    """Square avatar: the mark on the site's dark background (LinkedIn logo)."""
    return f"""<html><body style="margin:0">
<div style="width:{size}px;height:{size}px;display:grid;place-items:center;
background:radial-gradient(70% 70% at 50% 42%, #161c4c 0%, #0a0d1f 55%, {BG} 100%)">
<img src="mark-dark-bg.svg" style="width:{size * 0.66:.0f}px;height:{size * 0.66:.0f}px">
</div></body></html>"""


def avatar_centred_html(size, rim=0.31):
    """Square avatar with the hub at its centre, the rim at `rim` × size from it."""
    img = size * rim * 2 * CENTRED_HALF / (RIM_R + TIRE / 2)
    return f"""<html><body style="margin:0">
<div style="width:{size}px;height:{size}px;display:grid;place-items:center;
background:radial-gradient(60% 60% at 50% 50%, #161c4c 0%, #0a0d1f 60%, {BG} 100%)">
<img src="mark-centred-dark-bg.svg" style="width:{img:.1f}px;height:{img:.1f}px">
</div></body></html>"""


def write(rel, content):
    dest = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  written  {rel}")


def render_pngs():
    from playwright.sync_api import sync_playwright

    jobs = [  # (source in brand/, output, css width, css height, scale, background)
        ("mark-dark-bg.svg", "brand/aidiligence-mark-dark-bg.png", 128, 128, 8, None),
        ("mark-light-bg.svg", "brand/aidiligence-mark-light-bg.png", 128, 128, 8, None),
        ("lockup-dark-bg.svg", "brand/aidiligence-lockup-dark-bg.png", None, 128, 6, None),
        ("lockup-light-bg.svg", "brand/aidiligence-lockup-light-bg.png", None, 128, 6, None),
        ("avatar.html", "brand/aidiligence-linkedin-logo.png", 400, 400, 3, BG),
        ("mark-centred-dark-bg.svg", "brand/aidiligence-mark-centred-dark-bg.png", 128, 128, 8, None),
        ("mark-centred-light-bg.svg", "brand/aidiligence-mark-centred-light-bg.png", 128, 128, 8, None),
        ("avatar-centred.html", "brand/aidiligence-avatar-centred.png", 400, 400, 3, BG),
        ("avatar.html", "assets/img/icon-256.png", 400, 400, 0.64, BG),
    ]
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")
        for src, out, w, h, scale, bg in jobs:
            path = os.path.join(BRAND, src)
            if w is None:  # lockups: width from the SVG
                with open(path, encoding="utf-8") as f:
                    w = int(f.read().split('width="', 1)[1].split('"', 1)[0])
            page = browser.new_page(viewport={"width": w, "height": h}, device_scale_factor=scale)
            page.goto(f"file://{path}")
            page.screenshot(path=os.path.join(ROOT, out), omit_background=bg is None)
            page.close()
            print(f"  rendered {out}  ({w * scale}×{h * scale})")
        browser.close()


def main():
    print("AI Diligence logo:")
    write("brand/mark-dark-bg.svg", mark_svg(INK_DARK_BG))
    write("brand/mark-light-bg.svg", mark_svg(INK_LIGHT_BG))
    write("brand/lockup-dark-bg.svg", lockup_svg(INK_DARK_BG))
    write("brand/lockup-light-bg.svg", lockup_svg(INK_LIGHT_BG))
    write("assets/img/favicon.svg", favicon_svg())
    write("assets/img/mark.svg", mark_svg(INK_DARK_BG))
    write("tools/brand-wheel.svg", wheel_svg(INK_DARK_BG))
    write("brand/mark-centred-dark-bg.svg", mark_centred_svg(INK_DARK_BG))
    write("brand/mark-centred-light-bg.svg", mark_centred_svg(INK_LIGHT_BG))
    write("brand/avatar.html", avatar_html(400))
    write("brand/avatar-centred.html", avatar_centred_html(400))
    render_pngs()
    for f in ("avatar.html", "avatar-centred.html"):
        os.remove(os.path.join(BRAND, f))


if __name__ == "__main__":
    main()
