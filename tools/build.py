#!/usr/bin/env python3
"""Generate the static pages of aidiligence.eu.

Page content lives in the Python structures below — they are the source of
truth, the HTML files are produced from them.

Internal links are relative, so the site works both at a domain root and under
a sub-path. Exception: 404.html uses absolute paths, since it is served from an
arbitrary URL.

Usage: python3 tools/build.py
"""

import html
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SITE = "AI Diligence"
TAGLINE = "Artificial Intelligence Due Diligence"
LINKEDIN = "https://www.linkedin.com/in/paulasquin"

# Publisher of the site (mentions légales, LCEN art. 6).
PUBLISHER = {
    "name": "Guardia",
    "form": "société par actions simplifiée (SAS) au capital de 1\u00a0000\u00a0€",
    "rcs": "RCS Nanterre 910 991 140",
    "vat": "FR81910991140",
    "address": "6 rue des Romains, 92270 Bois-Colombes, France",
    "director": "Paul Asquin, Président",
    "email": "contact@aidiligence.eu",
    "phone": "+33 7 67 86 10 73",
}

LINKEDIN_SVG = (
    '<svg viewBox="0 0 448 512" aria-hidden="true"><path d="M100.28 448H7.4V148.9h92.88zM53.79 '
    '108.1C24.09 108.1 0 83.5 0 53.8a53.79 53.79 0 0 1 107.58 0c0 29.7-24.1 54.3-53.79 54.3zM447.9 '
    '448h-92.68V302.4c0-34.7-12.4-58.4-43.4-58.4-23.7 0-37.8 15.9-44 31.3-2.3 5.5-2.9 13.2-2.9 '
    '20.9V448h-92.8s1.2-241.1 0-266.1h92.8v37.7c12.3-19 34.4-46.1 83.7-46.1 61.1 0 106.9 39.9 '
    '106.9 125.7V448z"/></svg>'
)

# Line-art icons, drawn with primitives so they stay crisp at any size.
ICON_BULB = ('<svg viewBox="0 0 24 24" aria-hidden="true">'
             '<circle cx="12" cy="9.8" r="4.6"/>'
             '<path d="M9.7 16.9h4.6M10.5 19.8h3"/></svg>')
ICON_SEARCH = ('<svg viewBox="0 0 24 24" aria-hidden="true">'
               '<circle cx="10.4" cy="10.4" r="6"/>'
               '<path d="M14.9 14.9L20 20"/></svg>')
ICON_CHECK = ('<svg viewBox="0 0 24 24" aria-hidden="true">'
              '<circle cx="12" cy="12" r="8.6"/>'
              '<path d="M8.1 12.4l2.8 2.8 5.1-5.6"/></svg>')
ICON_CHART = ('<svg viewBox="0 0 24 24" aria-hidden="true">'
              '<path d="M4 19.6h16" stroke-width="1.9"/>'
              '<path d="M7.6 19.6V13M12 19.6V8.4M16.4 19.6V11.2" stroke-width="2.6"/></svg>')


def linkedin_button(label, on_photo=False):
    cls = "btn on-photo" if on_photo else "btn"
    return (f'<a class="{cls}" href="{LINKEDIN}" target="_blank" rel="noopener noreferrer">'
            f'{LINKEDIN_SVG}<span>{html.escape(label)}</span></a>')


# --------------------------------------------------------------------------- #
# Content
# --------------------------------------------------------------------------- #

SERVICE_LINES = [
    "AI &amp; MLOps Engineering",
    "AI Stack Due Diligence Audit",
    "AI Team &amp; Project Management",
]

PILLARS = [
    ("blue", ICON_BULB, "AI in Innovation",
     "AI technologies have become a main asset for innovative companies, especially when "
     "considering investments. The multiplication of actors raises questions on their "
     "differentiation and competitiveness."),
    ("green", ICON_SEARCH, "Technical Due Diligence",
     "Our AI due diligence services provide a comprehensive evaluation of a company's "
     "technological foundation, enhancing traditional due diligence efforts."),
    ("amber", ICON_CHECK, "AI Expertise",
     "We ensure your investment is not only based on potential but grounded in a robust "
     "technological infrastructure. We provide precise technology recommendations."),
    ("purple", ICON_CHART, "Insights",
     "Our services empower you with actionable insights, ensuring investments and "
     "technological choices are aligned with current industry standards and future "
     "advancements."),
]

FOCUS_AREAS = [
    ("Product Viability",
     "Is the product market-ready or just a demo? Can it be sold as is, and what is its "
     "scalability potential?"),
    ("Model and Data Integrity",
     "Scrutinizing the robustness of models, data sources, and IP. Evaluating technical "
     "reproducibility, beyond legal protections."),
    ("Technology Longevity and Defendability",
     "Assessing the long-term viability of the technology. Identifying data sources and "
     "model performances against the state of the art."),
    ("Team and Expertise",
     "Assessing the team's balance, diversity, and dependence on key individuals."),
    ("Technical Implementation",
     "Examining code quality, containerisation and test coverage. Ensuring documentation, "
     "version control, and sustainability."),
    ("Licensing and Scalability",
     "Evaluating the technology licensing model. Projecting how costs will scale with "
     "operational growth."),
    ("Costs and Performances",
     "Examining technical choices and avoidable latencies, challenging architectures and "
     "technologies, both custom-made and off-the-shelf."),
    ("Industry-specific Considerations",
     "For healthcare, sovereignty, medical devices and other regulated fields, identifying "
     "the risks associated with the technologies in the stack — current and future, from a "
     "technical standpoint."),
]

CAPABILITIES = [
    "Cloud or self-hosting running costs",
    "Model inference responsiveness",
    "Code base quality",
    "Model efficiency",
    "Prompt engineering",
    "Model benchmarking",
    "Projects architecture",
    "Scalability",
]

FOUNDER_BIO = [
    "Experienced as Head of AI in vision and language processing, CTO of Guardia and AI "
    "freelancer, I graduated from Centrale Paris and hold two MScs: one in AI and computer "
    "science, the other in robotics.",
    "I created AI Diligence in 2023 to offer my expertise and network.",
]

HEADER_SCRIPT = """<script>
(function () {
  var h = document.querySelector('.site-header'), hero = document.querySelector('.hero');
  if (!h || !hero) return;
  function sync() { h.classList.toggle('over-hero', window.scrollY < hero.offsetHeight - 70); }
  sync();
  addEventListener('scroll', sync, { passive: true });
  addEventListener('resize', sync);
})();
</script>"""


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
<link rel="preload" as="font" type="font/woff2" href="{p}assets/fonts/montserrat-latin.woff2" crossorigin>
<link rel="preload" as="font" type="font/woff2" href="{p}assets/fonts/opensans-latin.woff2" crossorigin>
<link rel="stylesheet" href="{p}assets/css/style.css">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:type" content="website">
<meta property="og:image" content="https://aidiligence.eu/assets/img/ai-diligence-logo.png">
</head>
<body>

<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{p or './'}">
      <img src="{p}assets/img/ai-diligence-mark.png" alt="" height="30">
      <span>AI Diligence</span>
    </a>
    <nav class="nav">
      <a href="{p}#due-diligence">Due diligence</a>
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
    <p>&copy; {html.escape(SITE)} — {html.escape(TAGLINE)} ·
      <a href="{LINKEDIN}" target="_blank" rel="noopener noreferrer">LinkedIn</a> ·
      <a href="{p}legal/">Mentions légales</a></p>
  </div>
</footer>

{HEADER_SCRIPT}
</body>
</html>
"""


def write(rel, content):
    dest = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(dest) or ROOT, exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  written  {rel:34} {len(content):>7} chars")


# --------------------------------------------------------------------------- #
# Pages
# --------------------------------------------------------------------------- #

def body_home(p):
    lines = "\n".join(f"        <li>{s}</li>" for s in SERVICE_LINES)
    pillars = "\n".join(f"""      <div class="pillar">
        <div class="icon {colour}">{icon}</div>
        <h3>{html.escape(name)}</h3>
        <p>{html.escape(text)}</p>
      </div>""" for colour, icon, name, text in PILLARS)
    focus = "\n".join(f"""        <div>
          <h3>{html.escape(t)}</h3>
          <p>{html.escape(d)}</p>
        </div>""" for t, d in FOCUS_AREAS)
    caps = "\n".join(f"          <li>{html.escape(c)}</li>" for c in CAPABILITIES)
    bio = "\n".join(f"          <p>{html.escape(b)}</p>" for b in FOUNDER_BIO)

    return f"""  <section class="hero">
    <div class="wrap">
      <h1>AI Diligence</h1>
      <ul class="service-lines">
{lines}
      </ul>
      {linkedin_button("Get in touch", on_photo=True)}
    </div>
  </section>

  <div class="panel-holder">
    <div class="wrap">
      <div class="panel">
{pillars}
      </div>
    </div>
  </div>

  <section class="section" id="due-diligence">
    <div class="wrap">
      <h2 class="section-title">Key Focus Areas in Our AI Due Diligence</h2>
      <p class="lede">Eight angles of assessment, from product readiness to licensing
        economics and sector-specific regulatory exposure.</p>
      <div class="focus">
{focus}
      </div>
    </div>
  </section>

  <section class="photo-section" id="expertise">
    <div class="wrap">
      <div class="float-card">
        <h2 class="section-title">More from our AI expertise</h2>
        <p class="section-kicker">Improve your AI projects</p>
        <p>Leverage on our experience to improve:</p>
        <ul class="caps">
{caps}
        </ul>
        <p>And more — get in touch for a demonstration on your own use cases.</p>
        <p style="margin-top:26px">{linkedin_button("Discuss a use case")}</p>
      </div>
    </div>
  </section>

  <section class="section" id="about">
    <div class="wrap">
      <h2 class="section-title">About</h2>
      <p class="section-kicker">Founder</p>
      <div class="founder">
        <img src="{p}assets/img/paul-asquin.jpg" alt="Paul Asquin" loading="lazy">
        <div>
          <h3>Paul Asquin</h3>
{bio}
        </div>
      </div>
    </div>
  </section>

  <section class="cta-band">
    <div class="wrap">
      <h2>Assessing an AI stack?</h2>
      <p>Reach out and let's talk about the scope.</p>
      {linkedin_button("Message me on LinkedIn")}
    </div>
  </section>
"""


def body_legal(p):
    g = {k: html.escape(v) for k, v in PUBLISHER.items()}
    return f"""  <section class="section legal">
    <div class="wrap">
      <h1 class="section-title">Mentions légales</h1>

      <h2>Éditeur</h2>
      <p>Le site aidiligence.eu est édité par <strong>{g["name"]}</strong>, {g["form"]},
        immatriculée au {g["rcs"]}, TVA intracommunautaire {g["vat"]}.<br>
        Siège social : {g["address"]}.<br>
        Directeur de la publication : {g["director"]}.<br>
        Contact : <a href="mailto:{g["email"]}">{g["email"]}</a> — {g["phone"]}.</p>

      <h2>Hébergement</h2>
      <p>GitHub, Inc. (GitHub Pages), 88 Colin P. Kelly Jr. Street, San Francisco, CA 94107,
        États-Unis — <a href="https://pages.github.com">pages.github.com</a>.</p>

      <h2>Données personnelles et cookies</h2>
      <p>Ce site est statique : il ne dépose aucun cookie, n'utilise aucun outil de mesure
        d'audience et ne collecte aucune donnée personnelle. Il ne charge aucune ressource
        externe. Les prises de contact se font par e-mail ou via LinkedIn.</p>

      <h2>Propriété intellectuelle</h2>
      <p>Les textes, images et logos de ce site appartiennent à {g["name"]}, sauf mention
        contraire. La photo d'en-tête provient de pxhere (licence CC0).</p>

      <h2>Legal notice (English)</h2>
      <p>Published by {g["name"]} SAS, {g["rcs"]}, VAT {g["vat"]}, {g["address"]}.
        Publication director: Paul Asquin. Contact: <a href="mailto:{g["email"]}">{g["email"]}</a>.
        Hosted by GitHub, Inc. No cookies, no tracking, no personal data collected.</p>
    </div>
  </section>
"""


def body_404(p):
    return """  <section class="hero">
    <div class="wrap">
      <h1>Page not found</h1>
      <p>This address does not exist, or no longer does.</p>
      <p style="margin-top:28px"><a class="btn on-photo" href="/">Back to home</a></p>
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

    write("legal/index.html", page("legal/", f"Mentions légales — {SITE}", body_legal,
                                   f"Mentions légales du site aidiligence.eu, édité par Guardia SAS."))

    # The former /about/ page is now a section of the home page.
    write("about/index.html", redirect_stub("../#about", "about/"))
    print("Done.")


if __name__ == "__main__":
    main()
