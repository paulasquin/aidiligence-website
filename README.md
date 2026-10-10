# aidiligence.eu

Static site for AI Diligence.

Plain HTML and CSS. No framework, no external request at runtime — the two
webfonts are served from this repository.

## Build

```bash
python3 tools/build.py
```

The Python 3 standard library is enough. Page content lives in `tools/build.py`.

## Preview

```bash
python3 -m http.server 8767 --directory .
```

Then <http://localhost:8767>.

## Deployment

GitHub Pages, `main` branch, repository root. The domain is declared by the `CNAME` file.

`google3019c1d90aa83ac3.html` proves ownership of the site to Google Search Console (used for the
Google Play developer account). Keep it at the root, unchanged: removing it loses the verification.

## Assets

`assets/img/canyon.jpg` comes from [pxhere](https://pxhere.com) and is released
under CC0.
