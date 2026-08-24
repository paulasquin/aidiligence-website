#!/usr/bin/env python3
"""Generate the static pages of aidiligence.eu.

Page content lives in the Python structures below — they are the source of
truth, the HTML files are produced from them.

Internal links are relative, so the site works both at the root of a domain and
under a sub-path. Exception: 404.html uses absolute paths, since it is served
from an arbitrary URL.

Usage: python3 tools/build.py
"""

import html
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SITE = "AI Diligence"
TAGLINE = "Artificial Intelligence Due Diligence"
LINKEDIN = "https://www.linkedin.com/in/paulasquin"

LINKEDIN_SVG = (
    '<svg viewBox="0 0 448 512" aria-hidden="true"><path d="M100.28 448H7.4V148.9h92.88zM53.79 '
    '108.1C24.09 108.1 0 83.5 0 53.8a53.79 53.79 0 0 1 107.58 0c0 29.7-24.1 54.3-53.79 54.3zM447.9 '
    '448h-92.68V302.4c0-34.7-12.4-58.4-43.4-58.4-23.7 0-37.8 15.9-44 31.3-2.3 5.5-2.9 13.2-2.9 '
    '20.9V448h-92.8s1.2-241.1 0-266.1h92.8v37.7c12.3-19 34.4-46.1 83.7-46.1 61.1 0 106.9 39.9 '
    '106.9 125.7V448z"/></svg>'
)


def link_button(label, ghost=False, on_band=False):
    cls = "btn ghost" if ghost else "btn"
    return (f'<a class="{cls}" href="{LINKEDIN}" target="_blank" rel="noopener noreferrer">'
            f'{LINKEDIN_SVG}<span>{html.escape(label)}</span></a>')


# --------------------------------------------------------------------------- #
# Content
# --------------------------------------------------------------------------- #

PILLARS = [
    ("AI in innovation",
     "AI technologies have become a main asset for innovative companies, especially when "
     "considering investments. The multiplication of actors raises questions on their "
     "differentiation and competitiveness."),
    ("Technical due diligence",
     "Our AI due diligence services provide a comprehensive evaluation of a company's "
     "technological foundation, enhancing traditional due diligence efforts."),
    ("AI expertise",
     "We ensure your investment is not only based on potential but grounded in a robust "
     "technological infrastructure, and we provide precise technology recommendations."),
    ("Insights",
     "Our services empower you with actionable insights, ensuring investments and "
     "technological choices are aligned with current industry standards and future "
     "advancements."),
]

FOCUS_AREAS = [
    ("Product viability",
     "Is the product market-ready or just a demo? Can it be sold as is, and what is its "
     "scalability potential?"),
    ("Technology longevity and defendability",
     "Assessing the long-term viability of the technology. Identifying data sources and "
     "model performances against the state of the art."),
    ("Technical implementation",
     "Examining code quality, containerisation and test coverage. Ensuring documentation, "
     "version control, and sustainability."),
    ("Costs and performances",
     "Examining technical choices and avoidable latencies, challenging architectures and "
     "technologies, both custom-made and off-the-shelf."),
    ("Model and data integrity",
     "Scrutinizing the robustness of models, data sources, and IP. Evaluating technical "
     "reproducibility, beyond legal protections."),
    ("Team and expertise",
     "Assessing the team's balance, diversity, and dependence on key individuals."),
    ("Licensing and scalability",
     "Evaluating the technology licensing model. Projecting how costs will scale with "
     "operational growth."),
    ("Industry-specific considerations",
     "For healthcare, sovereignty, medical devices and other regulated fields, identifying "
     "the risks associated with the technologies in the stack — current and future, from a "
     "technical standpoint."),
]

OFFERINGS = [
    "AI &amp; MLOps engineering",
    "AI stack due diligence audit",
    "AI team &amp; project management",
]

CAPABILITIES = [
    "Cloud or self-hosting running costs",
    "Model inference responsiveness",
    "Code base quality",
    "Model efficiency",
    "Prompt engineering",
    "Model benchmarking",
    "Project architecture",
    "Scalability",
]

FOUNDER_BIO = [
    "Experienced as Head of AI in vision and language processing, CTO of Guardia and AI "
    "freelancer, I graduated from Centrale Paris and hold two MScs: one in AI and computer "
    "science, the other in robotics.",
    "I created AI Diligence in 2023 to offer my expertise and network.",
]


# --------------------------------------------------------------------------- #
# Template
# --------------------------------------------------------------------------- #

def page(slug, title, body_fn, description, prefix=None):
    if prefix is None:
        prefix = "../" * slug.count("/")
    p = prefix
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<link rel="icon" type="image/png" href="{p}assets/img/ai-diligence-logo.png">
<link rel="stylesheet" href="{p}assets/css/style.css">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:type" content="website">
<meta property="og:image" content="https://aidiligence.eu/assets/img/ai-diligence-logo.png">
</head>
<body>

<header class="site-header">
  <div class="wrap">
    <a class="logo" href="{p or './'}">
      <img src="{p}assets/img/ai-diligence-mark.png" alt="" height="38">
      <span>AI Diligence</span>
    </a>
    <nav class="nav">
      <a href="{p}#services">Due diligence</a>
      <a href="{p}#expertise">Expertise</a>
      <a href="{p}#about">About</a>
      <a href="{LINKEDIN}" target="_blank" rel="noopener noreferrer">Contact</a>
    </nav>
  </div>
</header>

<main>
{body_fn(p)}
</main>

<footer class="site-footer">
  <div class="wrap">
    <p>&copy; {html.escape(SITE)} — {html.escape(TAGLINE)}</p>
    <p><a href="{LINKEDIN}" target="_blank" rel="noopener noreferrer">LinkedIn</a></p>
  </div>
</footer>

</body>
</html>
"""


def write(rel, content):
    dest = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(dest) or ROOT, exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  written  {rel:34} {len(content):>7} chars")


def cards(items):
    return "\n".join(f"""        <div class="card">
          <h3>{html.escape(t)}</h3>
          <p>{html.escape(d)}</p>
        </div>""" for t, d in items)


# --------------------------------------------------------------------------- #
# Pages
# --------------------------------------------------------------------------- #

def body_home(p):
    caps = "\n".join(f"        <li>{html.escape(c)}</li>" for c in CAPABILITIES)
    offer = "\n".join(f"        <li>{o}</li>" for o in OFFERINGS)
    bio = "\n".join(f"      <p>{html.escape(b)}</p>" for b in FOUNDER_BIO)
    return f"""  <section class="hero">
    <div class="wrap">
      <span class="badge">French Crédit Impôt Recherche approved — projects up to 30% back-financed</span>
      <h1>Artificial Intelligence Due Diligence</h1>
      <p class="lede">A comprehensive evaluation of a company's AI stack — what the technology
        actually does, what it costs to run, and how well it holds up under scrutiny.</p>
      <ul class="offer">
{offer}
      </ul>
      <div class="actions">
        {link_button("Get in touch on LinkedIn")}
      </div>
    </div>
  </section>

  <section class="section" id="services">
    <div class="wrap">
      <h2>Why technical due diligence on AI</h2>
      <div class="grid two">
{cards(PILLARS)}
      </div>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <h2>Key focus areas</h2>
      <p class="intro">Eight angles of assessment, from product readiness to licensing
        economics and sector-specific regulatory exposure.</p>
      <div class="grid">
{cards(FOCUS_AREAS)}
      </div>
    </div>
  </section>

  <section class="section" id="expertise">
    <div class="wrap">
      <h2>Improve your AI projects</h2>
      <p class="intro">Beyond due diligence, the same expertise applies directly to
        systems already in production.</p>
      <ul class="caps">
{caps}
      </ul>
      <div class="actions">
        {link_button("Discuss a specific use case", ghost=True)}
      </div>
    </div>
  </section>

  <section class="section" id="about">
    <div class="wrap">
      <h2>About</h2>
      <div class="founder">
        <img src="{p}assets/img/paul-asquin.jpg" alt="Paul Asquin" loading="lazy">
        <div>
          <h3>Paul Asquin</h3>
          <p class="role">Founder</p>
{bio}
        </div>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div class="band">
        <h2>Assessing an AI stack?</h2>
        <p>Reach out on LinkedIn and let's talk about the scope.</p>
        {link_button("Message me on LinkedIn")}
      </div>
    </div>
  </section>
"""


def body_404(p):
    return """  <section class="hero">
    <div class="wrap">
      <h1>Page not found</h1>
      <p class="lede">This address does not exist, or no longer does.</p>
      <div class="actions">
        <a class="btn" href="/">Back to home</a>
      </div>
    </div>
  </section>
"""


def redirect_stub(target, canonical):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Redirecting — {SITE}</title>
<meta http-equiv="refresh" content="0; url={target}">
<link rel="canonical" href="https://aidiligence.eu/{canonical}">
<meta name="robots" content="noindex">
</head>
<body>
<p>This page has moved. <a href="{target}">Continue to AI Diligence</a>.</p>
</body>
</html>
"""


def main():
    print("Building AI Diligence:")
    write("index.html", page(
        "", f"{SITE} — {TAGLINE}", body_home,
        "AI due diligence: a comprehensive technical evaluation of a company's AI stack — "
        "product viability, model integrity, running costs, licensing and scalability."))

    write("404.html", page("", f"Page not found — {SITE}", body_404,
                           "Page not found.", prefix="/"))

    # The former /about/ page is now a section of the home page.
    write("about/index.html", redirect_stub("../#about", "about/"))
    print("Done.")


if __name__ == "__main__":
    main()
