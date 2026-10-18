#!/usr/bin/env python3
"""Render the LinkedIn banners from tools/banner.html (the site's particle wheel).

Writes brand/linkedin-banner-{profile,company}-{fr,en}.png at twice LinkedIn's
recommended size (personal profile 1584 × 396, company page 1128 × 191), so
they stay sharp on high-density screens.

Usage: uv run -q --with playwright python tools/banners.py
(Playwright renders with the installed Chrome: channel="chrome"; the WebGL
field needs its GPU, the default.)
"""

import functools
import http.server
import os
import threading

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIZES = {"profile": (1584, 396), "company": (1128, 191)}


def main():
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    handler = functools.partial(Quiet, directory=ROOT)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_port}/tools/banner.html"
    print("LinkedIn banners:")
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")
        for kind, (w, h) in SIZES.items():
            for lang in ("fr", "en"):
                page = browser.new_page(viewport={"width": w, "height": h}, device_scale_factor=2)
                page.goto(f"{base}?kind={kind}&lang={lang}")
                page.wait_for_selector("body[data-ready]")
                out = f"brand/linkedin-banner-{kind}-{lang}.png"
                page.screenshot(path=os.path.join(ROOT, out))
                page.close()
                print(f"  rendered {out}  ({2 * w}×{2 * h})")
        browser.close()
    server.shutdown()


if __name__ == "__main__":
    main()
