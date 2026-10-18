#!/usr/bin/env python3
"""Draw the AI Diligence logo and export it.

The mark is half a stagecoach wheel standing on its axle, which draws the D
of Diligence: the stem is the axle, four spokes fan out from the hub to the
rim. Everything is computed here, so a change of proportion is a change of
the constants below.

Writes:
- brand/*.svg — mark and lockup, for dark and for light backgrounds; the
  lockup's text is outlined from assets/fonts/unbounded-latin.woff2;
- brand/*.png — the same, rendered by headless Chrome, plus a square avatar
  for LinkedIn;
- assets/img/mark.svg (the nav), assets/img/favicon.svg (follows the browser's light / dark theme) and
  assets/img/icon-256.png (the avatar, for touch icons) — the site icons.

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
AXLE_X, HUB_Y, RIM_R = 41, 64, 46
STROKE, SPOKE = 12, 6
HUB_R = 13
SPOKE_ANGLES = (-54, -18, 18, 54)  # degrees from the horizontal, rim ends at ±90


def gradient(gid, x1, y1, x2, y2):
    return (f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{x1}" y1="{y1}" '
            f'x2="{x2}" y2="{y2}"><stop offset="0" stop-color="{CYAN}"/>'
            f'<stop offset="1" stop-color="{VIOLET}"/></linearGradient>')


def mark_paths(ink, gid="g"):
    """The mark's shapes and its gradient; ink None: the stem and hub take class "ink"."""
    x, y, r = AXLE_X, HUB_Y, RIM_R
    fill = f'fill="{ink}"' if ink else 'class="ink"'
    stroke = f'stroke="{ink}"' if ink else 'class="ink"'
    top, bot = y - r, y + r
    out = [f"<defs>{gradient(gid, x - 11, top - 2, x + 55, bot + 2)}</defs>",
           f'<path d="M{x} {top} A{r} {r} 0 0 1 {x} {bot}" fill="none" stroke="url(#{gid})" '
           f'stroke-width="{STROKE}" stroke-linecap="round"/>']
    for a in SPOKE_ANGLES:
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        r0, r1 = HUB_R + 6, r - STROKE / 2 - 3
        out.append(f'<line x1="{x + r0 * c:.2f}" y1="{y + r0 * s:.2f}" x2="{x + r1 * c:.2f}" '
                   f'y2="{y + r1 * s:.2f}" stroke="url(#{gid})" stroke-width="{SPOKE}" '
                   f'stroke-linecap="round"/>')
    out.append(f'<path d="M{x} {y - HUB_R} A{HUB_R} {HUB_R} 0 0 1 {x} {y + HUB_R} Z" {fill}/>')
    out.append(f'<line x1="{x}" y1="{top}" x2="{x}" y2="{bot}" {stroke} '
               f'stroke-width="{STROKE}" stroke-linecap="round"/>')
    return "".join(out)


def svg(w, h, body, title="AI Diligence"):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" '
            f'height="{h}" role="img" aria-label="{title}"><title>{title}</title>{body}</svg>\n')


def mark_svg(ink):
    return svg(128, 128, mark_paths(ink))


def favicon_svg():
    """Ink stem on light browser chrome, light stem on dark."""
    style = (f"<style>path.ink{{fill:{INK_LIGHT_BG}}}line.ink{{stroke:{INK_LIGHT_BG}}}"
             f"@media (prefers-color-scheme: dark){{path.ink{{fill:{INK_DARK_BG}}}"
             f"line.ink{{stroke:{INK_DARK_BG}}}}}</style>")
    return svg(128, 128, style + mark_paths(None))


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
    left = AXLE_X - STROKE / 2 - 6  # crop the mark's box to the stem
    x0 = AXLE_X + RIM_R + STROKE / 2 + 20
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
    write("brand/avatar.html", avatar_html(400))
    render_pngs()
    os.remove(os.path.join(BRAND, "avatar.html"))


if __name__ == "__main__":
    main()
