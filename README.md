# aidiligence.eu

Static site for AI Diligence.

Plain HTML and CSS, no dependencies.

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
