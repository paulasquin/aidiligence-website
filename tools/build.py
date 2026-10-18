#!/usr/bin/env python3
"""Generate the static pages of aidiligence.eu.

Page content lives in the Python structures below, in French and English —
they are the source of truth. The build writes:

- index.html, with the French text tagged data-i18n (French is the default
  language of the HTML, as on paulasquin.com);
- assets/js/strings.js, the English of every tagged element, applied in the
  browser by assets/js/i18n.js when the visitor's language is English;
- legal/index.html (mentions légales), 404.html and the about/ redirect.

Internal links are relative, so the site works both at a domain root and under
a sub-path. Exception: 404.html uses absolute paths, since it is served from an
arbitrary URL.

Usage: python3 tools/build.py
"""

import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SITE = "AI Diligence"
URL = "https://aidiligence.eu/"
HUB = "https://paulasquin.com"
LINKEDIN = "https://www.linkedin.com/in/paulasquin"
EMAIL = "contact@aidiligence.eu"

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

# Language picked before first paint: ?lang=, then the visitor's saved choice,
# then the browser languages (same script as paulasquin.com).
LANG_SCRIPT = """<script>
    (function () {
      var ok = ['fr', 'en'], lang = null;
      try {
        var q = new URLSearchParams(location.search).get('lang');
        if (ok.indexOf(q) >= 0) { lang = q; localStorage.setItem('lang', q); }
        else if (ok.indexOf(localStorage.getItem('lang')) >= 0) lang = localStorage.getItem('lang');
      } catch (e) {}
      if (!lang) {
        var ls = navigator.languages || [navigator.language || ''];
        for (var i = 0; i < ls.length && !lang; i++) { var b = String(ls[i]).slice(0, 2).toLowerCase(); if (ok.indexOf(b) >= 0) lang = b; }
      }
      document.documentElement.lang = lang || 'en';
    })();
  </script>"""

# The nav logo rolls in once per session, large, then shrinks to its place; the
# page stays usable meanwhile. Not after the language switch, on a link to an
# anchor or with reduced motion; if the script has not started it within 6 s,
# the logo is simply shown at rest.
INTRO_SCRIPT = """<script>
    (function () {
      var r = document.documentElement;
      try {
        if (sessionStorage.getItem('intro') || sessionStorage.getItem('scrollY') || location.hash
            || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
        r.classList.add('intro');
        setTimeout(function () { if (!r.dataset.intro) r.classList.remove('intro'); }, 6000);
      } catch (e) {}
    })();
  </script>"""


def brand_lockup():
    with open(os.path.join(ROOT, "tools/brand-wheel.svg"), encoding="utf-8") as f:
        wheel = f.read().strip()  # written by tools/logo.py
    return (f'<span class="brand-lockup">{wheel}'
            '<span class="brand-text"><b>AI</b> Diligence</span></span>')


FONTS = ('<link rel="preload" as="font" type="font/woff2" href="assets/fonts/unbounded-latin.woff2" crossorigin>\n'
         '  <link rel="preload" as="font" type="font/woff2" href="assets/fonts/inter-latin.woff2" crossorigin>')

# --------------------------------------------------------------------------- #
# Translation
# --------------------------------------------------------------------------- #

EN = {}  # data-i18n key -> English, filled while the page is rendered


def tr(key, fr, en):
    """Register the English of `key` and return the French (both are HTML)."""
    EN[key] = en
    return fr


def t(tag, key, fr, en, attrs=""):
    return f'<{tag}{attrs} data-i18n="{key}">{tr(key, fr, en)}</{tag}>'


# --------------------------------------------------------------------------- #
# Content (French, English)
# --------------------------------------------------------------------------- #

META_TITLE = ("AI Diligence — Due diligence en intelligence artificielle",
              "AI Diligence — Artificial Intelligence Due Diligence")
META_DESC = ("Due diligence IA : une évaluation technique complète de la stack IA d'une entreprise — "
             "viabilité du produit, intégrité des modèles, coûts d'exploitation, licences et passage "
             "à l'échelle.",
             "AI due diligence: a comprehensive technical evaluation of a company's AI stack — "
             "product viability, model integrity, running costs, licensing and scalability.")

SERVICE_LINES = [
    ("Ingénierie IA &amp; MLOps", "AI &amp; MLOps Engineering"),
    ("Audit de stack IA (due diligence)", "AI Stack Due Diligence Audit"),
    ("Pilotage d'équipes et de projets IA", "AI Team &amp; Project Management"),
]

PILLARS = [
    ("#6fd6ff", ICON_BULB, ("L'IA dans l'innovation", "AI in Innovation"),
     ("Les technologies d'IA sont devenues un atout majeur des entreprises innovantes, en "
      "particulier dans une perspective d'investissement. La multiplication des acteurs interroge "
      "leur différenciation et leur compétitivité.",
      "AI technologies have become a main asset for innovative companies, especially when "
      "considering investments. The multiplication of actors raises questions on their "
      "differentiation and competitiveness.")),
    ("#4fe0c0", ICON_SEARCH, ("Due diligence technique", "Technical Due Diligence"),
     ("Nos services de due diligence IA offrent une évaluation complète des fondations "
      "technologiques d'une entreprise, en complément de la due diligence traditionnelle.",
      "Our AI due diligence services provide a comprehensive evaluation of a company's "
      "technological foundation, enhancing traditional due diligence efforts.")),
    ("#ffb37a", ICON_CHECK, ("Expertise IA", "AI Expertise"),
     ("Nous veillons à ce que votre investissement ne repose pas seulement sur un potentiel, mais "
      "sur une infrastructure technologique robuste. Nous formulons des recommandations "
      "technologiques précises.",
      "We ensure your investment is not only based on potential but grounded in a robust "
      "technological infrastructure. We provide precise technology recommendations.")),
    ("#a78bff", ICON_CHART, ("Éclairages", "Insights"),
     ("Nos services vous apportent des éclairages concrets, pour des investissements et des choix "
      "technologiques alignés sur les standards actuels du secteur et ses évolutions à venir.",
      "Our services empower you with actionable insights, ensuring investments and technological "
      "choices are aligned with current industry standards and future advancements.")),
]

FOCUS_AREAS = [
    (("Viabilité du produit", "Product Viability"),
     ("Le produit est-il prêt pour le marché, ou n'est-ce qu'une démo ? Peut-il être vendu en "
      "l'état, et quel est son potentiel de passage à l'échelle ?",
      "Is the product market-ready or just a demo? Can it be sold as is, and what is its "
      "scalability potential?")),
    (("Intégrité des modèles et des données", "Model and Data Integrity"),
     ("Examiner la robustesse des modèles, des sources de données et de la propriété "
      "intellectuelle. Évaluer la reproductibilité technique, au-delà des protections juridiques.",
      "Scrutinizing the robustness of models, data sources, and IP. Evaluating technical "
      "reproducibility, beyond legal protections.")),
    (("Pérennité et défendabilité de la technologie", "Technology Longevity and Defendability"),
     ("Évaluer la viabilité de la technologie à long terme. Identifier les sources de données et "
      "situer les performances des modèles par rapport à l'état de l'art.",
      "Assessing the long-term viability of the technology. Identifying data sources and model "
      "performances against the state of the art.")),
    (("Équipe et expertise", "Team and Expertise"),
     ("Évaluer l'équilibre et la diversité de l'équipe, et sa dépendance à des personnes clés.",
      "Assessing the team's balance, diversity, and dependence on key individuals.")),
    (("Mise en œuvre technique", "Technical Implementation"),
     ("Examiner la qualité du code, la conteneurisation et la couverture de tests. S'assurer de "
      "la documentation, du versionnement et de la pérennité.",
      "Examining code quality, containerisation and test coverage. Ensuring documentation, "
      "version control, and sustainability.")),
    (("Licences et passage à l'échelle", "Licensing and Scalability"),
     ("Évaluer le modèle de licence de la technologie. Projeter l'évolution des coûts avec la "
      "croissance de l'activité.",
      "Evaluating the technology licensing model. Projecting how costs will scale with "
      "operational growth.")),
    (("Coûts et performances", "Costs and Performances"),
     ("Examiner les choix techniques et les latences évitables, challenger les architectures et "
      "les technologies, développées sur mesure ou sur étagère.",
      "Examining technical choices and avoidable latencies, challenging architectures and "
      "technologies, both custom-made and off-the-shelf.")),
    (("Spécificités sectorielles", "Industry-specific Considerations"),
     ("Pour la santé, la souveraineté, les dispositifs médicaux et les autres secteurs "
      "réglementés, identifier les risques liés aux technologies de la stack — actuels et futurs, "
      "d'un point de vue technique.",
      "For healthcare, sovereignty, medical devices and other regulated fields, identifying the "
      "risks associated with the technologies in the stack — current and future, from a "
      "technical standpoint.")),
]

CAPABILITIES = [
    ("Coûts d'exploitation, cloud ou auto-hébergé", "Cloud or self-hosting running costs"),
    ("Réactivité de l'inférence des modèles", "Model inference responsiveness"),
    ("Qualité du code", "Code base quality"),
    ("Efficacité des modèles", "Model efficiency"),
    ("Prompt engineering", "Prompt engineering"),
    ("Benchmark de modèles", "Model benchmarking"),
    ("Architecture des projets", "Projects architecture"),
    ("Passage à l'échelle", "Scalability"),
]

FOUNDER_BIO = [
    ("Fort d'une expérience de Head of AI en vision et en traitement du langage, de CTO de Guardia "
     "et de freelance en IA, je suis diplômé de Centrale Paris et titulaire de deux MSc : l'un en "
     "intelligence artificielle et informatique, l'autre en robotique.",
     "Experienced as Head of AI in vision and language processing, CTO of Guardia and AI "
     "freelancer, I graduated from Centrale Paris and hold two MScs: one in AI and computer "
     "science, the other in robotics."),
    ("J'ai créé AI Diligence en 2023 pour mettre à disposition mon expertise et mon réseau.",
     "I created AI Diligence in 2023 to offer my expertise and network."),
]

FACTS = [
    ("Centrale Paris", ("ingénieur", "engineer")),
    ("2 MSc", ("IA &amp; informatique · robotique", "AI &amp; computer science · robotics")),
    ("Head of AI", ("vision &amp; langage", "vision &amp; language")),
    ("CTO", None),
]


# --------------------------------------------------------------------------- #
# Fragments
# --------------------------------------------------------------------------- #

def linkedin_button(key, fr, en, cls="btn btn-primary magnetic"):
    return (f'<a class="{cls}" href="{LINKEDIN}" target="_blank" rel="noopener noreferrer">'
            f'{LINKEDIN_SVG}{t("span", key, fr, en)}</a>')


def body_home():
    lines = "\n".join(
        f'            <li><span class="sl-num">0{i}</span>{t("span", f"hero.l{i}", fr, en)}</li>'
        for i, (fr, en) in enumerate(SERVICE_LINES, 1))
    pillars = "\n".join(f"""          <div class="tile pillar reveal" style="--accent:{colour}">
            <span class="pillar-icon">{icon}</span>
            {t("h3", f"pl{i}.t", *name)}
            {t("p", f"pl{i}.p", *text)}
          </div>""" for i, (colour, icon, name, text) in enumerate(PILLARS, 1))
    focus = "\n".join(f"""            <div class="focus-item">
              <span class="fi-num">0{i}</span>
              {t("h3", f"fa{i}.t", *title)}
              {t("p", f"fa{i}.p", *text)}
            </div>""" for i, (title, text) in enumerate(FOCUS_AREAS, 1))
    caps = "\n".join(f'              {t("li", f"cap{i}", fr, en)}'
                     for i, (fr, en) in enumerate(CAPABILITIES, 1))
    marquee = "\n".join(f'          {t("span", f"mq{i}", fr, en)}<b>✦</b>'
                        for i, (fr, en) in enumerate(CAPABILITIES, 1))
    bio = "\n".join(f'            {t("p", f"ab.p{i}", fr, en)}'
                    for i, (fr, en) in enumerate(FOUNDER_BIO, 1))
    facts = "\n".join(
        f'              <li><b>{name}</b>{t("span", f"ab.f{i}", *sub) if sub else "<span>Guardia</span>"}</li>'
        for i, (name, sub) in enumerate(FACTS, 1))

    return f"""    <!-- Hero -->
    <section id="top" class="scene hero" data-shape="mark" data-side="1">
      <div class="wrap">
        <div class="hero-content">
          <p class="eyebrow"><span class="pulse-dot"></span>{t("span", "hero.eyebrow", "Due diligence en intelligence artificielle", "Artificial Intelligence Due Diligence")}</p>
          <h1 class="hero-title">
            <span class="ht-line"><span class="ht-word">AI</span></span>
            <span class="ht-line"><span class="ht-word ht-glow">Diligence</span></span>
          </h1>
          <ul class="service-lines">
{lines}
          </ul>
          {t("p", "hero.sub", "Une évaluation technique complète de la stack IA d'une entreprise : viabilité du produit, intégrité des modèles, coûts d'exploitation, licences et passage à l'échelle.", "A comprehensive technical evaluation of a company's AI stack: product viability, model integrity, running costs, licensing and scalability.", ' class="hero-sub"')}
          <div class="hero-cta">
            {linkedin_button("hero.cta1", "Prendre contact", "Get in touch")}
            <a href="#due-diligence" class="btn btn-ghost magnetic">{t("span", "hero.cta2", "Les 8 axes d'audit", "The 8 focus areas")}</a>
          </div>
        </div>
      </div>
      <div class="scroll-cue" aria-hidden="true"><span></span>{t("i", "hero.scroll", "Défiler", "Scroll")}</div>
    </section>

    <!-- Approach -->
    <section id="approach" class="scene scene-short" data-shape="galaxy" data-side="0">
      <div class="wrap">
        <div class="intro reveal">
          {t("p", "ap.k", "Approche", "Approach", ' class="kicker"')}
          {t("h2", "ap.t", "Investir dans l'IA, <em>sur des bases solides</em>", "Investing in AI, <em>on solid ground</em>", ' class="title title-xl"')}
        </div>
        <div class="tiles pillars">
{pillars}
        </div>
      </div>
    </section>

    <!-- Focus areas -->
    <section id="due-diligence" class="scene" data-shape="stack" data-side="1">
      <div class="wrap">
        <div class="card card-wide reveal">
          {t("p", "fa.k", "Due diligence · 8 axes", "Due diligence · 8 focus areas", ' class="kicker"')}
          {t("h2", "fa.t", "Les axes clés de <em>notre due diligence IA</em>", "Key focus areas in <em>our AI due diligence</em>", ' class="title"')}
          {t("p", "fa.p", "Huit angles d'évaluation, de la maturité du produit à l'économie des licences et à l'exposition réglementaire propre à chaque secteur.", "Eight angles of assessment, from product readiness to licensing economics and sector-specific regulatory exposure.", ' class="lede"')}
          <div class="focus">
{focus}
          </div>
        </div>
      </div>
    </section>

    <!-- Expertise -->
    <section id="expertise" class="scene" data-shape="net" data-side="-1">
      <div class="wrap wrap-right">
        <div class="card reveal">
          {t("p", "ex.k", "Expertise · améliorer vos projets d'IA", "Expertise · improve your AI projects", ' class="kicker"')}
          {t("h2", "ex.t", "Plus de notre <em>expertise IA</em>", "More from <em>our AI expertise</em>", ' class="title"')}
          {t("p", "ex.p", "Profitez de notre expérience pour améliorer :", "Leverage our experience to improve:", ' class="lede"')}
          <ul class="caps">
{caps}
          </ul>
          {t("p", "ex.more", "Et plus encore — contactez-nous pour une démonstration sur vos propres cas d'usage.", "And more — get in touch for a demonstration on your own use cases.", ' class="more"')}
          <div class="card-cta">{linkedin_button("ex.cta", "Parler d'un cas d'usage", "Discuss a use case")}</div>
        </div>
      </div>
      <div class="marquee" aria-hidden="true">
        <div class="marquee-track">
{marquee}
        </div>
      </div>
    </section>

    <!-- About -->
    <section id="about" class="scene" data-shape="orb" data-side="1">
      <div class="wrap">
        <div class="card about reveal">
          <img class="portrait" src="assets/img/paul-asquin.jpg" alt="Paul Asquin" loading="lazy" width="601" height="800">
          <div>
            {t("p", "ab.k", "À propos · Fondateur", "About · Founder", ' class="kicker"')}
            <h2 class="title">Paul <em>Asquin</em></h2>
{bio}
            <ul class="facts">
{facts}
            </ul>
            <p class="card-cta"><a class="btn btn-ghost magnetic" href="{HUB}" target="_blank" rel="noopener">{t("span", "ab.hub", "Mes projets sur paulasquin.com", "My projects on paulasquin.com")}<span class="arrow">↗</span></a></p>
          </div>
        </div>
      </div>
    </section>

    <!-- Contact -->
    <section id="contact" class="scene contact" data-shape="galaxy" data-side="0">
      <div class="wrap">
        <div class="intro reveal">
          {t("p", "ct.k", "Contact", "Contact", ' class="kicker"')}
          {t("h2", "ct.t", "Vous évaluez <em>une stack IA ?</em>", "Assessing <em>an AI stack?</em>", ' class="title title-xl"')}
          {t("p", "ct.p", "Contactez-moi et parlons du périmètre. Je réponds sur LinkedIn ou par e-mail.", "Reach out and let's talk about the scope. I answer on LinkedIn or by email.", ' class="lede center"')}
          <div class="hero-cta center">
            {linkedin_button("ct.cta", "M'écrire sur LinkedIn", "Message me on LinkedIn")}
            <a class="btn btn-ghost magnetic" href="mailto:{EMAIL}">{EMAIL}</a>
          </div>
        </div>
      </div>
      <footer class="footer">
        <span>© {SITE} — {t("span", "ft.tag", "Due diligence en intelligence artificielle", "Artificial Intelligence Due Diligence")}</span>
        <span><a href="{HUB}" target="_blank" rel="noopener">paulasquin.com</a> · <a href="{LINKEDIN}" target="_blank" rel="noopener noreferrer">LinkedIn</a> · <a href="mailto:{EMAIL}">{EMAIL}</a> · {t("a", "ft.legal", "Mentions légales", "Legal notice", ' href="legal/"')}</span>
      </footer>
    </section>"""


def page_home():
    title = tr("meta.title", *META_TITLE)
    desc = tr("meta.description", *META_DESC)
    body = body_home()
    return f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{html.escape(desc)}">
  <meta name="theme-color" content="#04050c">
  <link rel="canonical" href="{URL}">
  <link rel="alternate" hreflang="fr" href="{URL}?lang=fr">
  <link rel="alternate" hreflang="en" href="{URL}?lang=en">
  <link rel="alternate" hreflang="x-default" href="{URL}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{URL}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{html.escape(desc)}">
  <meta property="og:image" content="{URL}assets/og.jpg">
  <meta name="twitter:card" content="summary_large_image">
  {LANG_SCRIPT}
  {INTRO_SCRIPT}
  <link rel="icon" type="image/svg+xml" href="assets/img/favicon.svg">
  <link rel="apple-touch-icon" href="assets/img/icon-256.png">
  {FONTS}
  <link href="assets/css/style.css" rel="stylesheet">
  <script type="importmap">
  {{
    "imports": {{
      "three": "./assets/vendor/three.module.js"
    }}
  }}
  </script>
</head>
<body class="is-loading">
  <canvas id="field" class="field" aria-hidden="true"></canvas>
  <div class="veil" aria-hidden="true"></div>
  <div class="scroll-progress" aria-hidden="true"><span></span></div>

  <nav class="topnav" aria-label="{tr("nav.aria", "Navigation principale", "Main navigation")}" data-i18n-aria="nav.aria">
    <a href="#top" class="brand" aria-label="AI Diligence">{brand_lockup()}</a>
    <div class="nav-links">
      {t("a", "nav.approach", "Approche", "Approach", ' href="#approach"')}
      <a href="#due-diligence">Due diligence</a>
      <a href="#expertise">Expertise</a>
      {t("a", "nav.about", "À propos", "About", ' href="#about"')}
      <a href="#contact">Contact</a>
      <a class="nav-hub" href="{HUB}" target="_blank" rel="noopener">paulasquin.com ↗</a>
    </div>
    <div class="lang-switch" role="group" aria-label="{tr("nav.lang", "Langue", "Language")}" data-i18n-aria="nav.lang">
      <button type="button" data-lang="fr">FR</button><button type="button" data-lang="en">EN</button>
    </div>
  </nav>

  <main>
{body}
  </main>

  <script src="assets/vendor/gsap.min.js"></script>
  <script src="assets/vendor/ScrollTrigger.min.js"></script>
  <script src="assets/vendor/lenis.min.js"></script>
  <script type="module" src="assets/js/main.js"></script>
</body>
</html>
"""


def strings_js():
    lines = "\n".join(f"  {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)}," for k, v in EN.items())
    return ("// Generated by tools/build.py — do not edit by hand.\n"
            "// English for the elements of index.html tagged data-i18n / data-i18n-aria.\n"
            f"export const STATIC_EN = {{\n{lines}\n}};\n")


def subpage(p, title, desc, body, robots=""):
    """A page without the particle field: 404 and legal notice."""
    return f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(desc)}">{robots}
  <meta name="theme-color" content="#04050c">
  <link rel="icon" type="image/svg+xml" href="{p}assets/img/favicon.svg">
  <link href="{p}assets/css/style.css" rel="stylesheet">
</head>
<body class="subpage">
  <nav class="topnav scrolled">
    <a href="{p or './'}" class="brand"><img class="brand-mark" src="{p}assets/img/mark.svg" alt="" width="28" height="28">AI Diligence</a>
  </nav>
  <main>
{body}
  </main>
</body>
</html>
"""


def page_404():
    return subpage("/", f"Page introuvable · Page not found — {SITE}", "Page not found.", """    <section class="scene contact">
      <div class="wrap">
        <div class="intro">
          <p class="kicker">404</p>
          <h1 class="title title-xl">Page introuvable <em>· Page not found</em></h1>
          <p class="lede center">Cette adresse n'existe pas, ou plus. · This address does not exist, or no longer does.</p>
          <div class="hero-cta center"><a class="btn btn-primary" href="/">AI Diligence</a></div>
        </div>
      </div>
    </section>""", robots='\n  <meta name="robots" content="noindex">')


def page_legal():
    g = {k: html.escape(v) for k, v in PUBLISHER.items()}
    return subpage("../", f"Mentions légales — {SITE}",
                   "Mentions légales du site aidiligence.eu, édité par Guardia SAS.", f"""    <section class="scene legal">
      <div class="wrap">
        <div class="card">
          <p class="kicker">Legal notice</p>
          <h1 class="title">Mentions <em>légales</em></h1>

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
            contraire.</p>

          <h2>Legal notice (English)</h2>
          <p>Published by {g["name"]} SAS, {g["rcs"]}, VAT {g["vat"]}, {g["address"]}.
            Publication director: Paul Asquin. Contact: <a href="mailto:{g["email"]}">{g["email"]}</a>.
            Hosted by GitHub, Inc. No cookies, no tracking, no personal data collected.</p>
        </div>
      </div>
    </section>""")


def redirect_stub(target, canonical):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Redirecting — {SITE}</title>
<meta http-equiv="refresh" content="0; url={target}">
<link rel="canonical" href="{URL}{canonical}">
<meta name="robots" content="noindex">
</head>
<body>
<p>This page has moved. <a href="{target}">Continue to AI Diligence</a>.</p>
</body>
</html>
"""


def write(rel, content):
    dest = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(dest) or ROOT, exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  written  {rel:34} {len(content):>7} chars")


def main():
    print("Building AI Diligence:")
    write("index.html", page_home())
    write("assets/js/strings.js", strings_js())
    write("404.html", page_404())
    write("legal/index.html", page_legal())
    # The former /about/ page is now a section of the home page.
    write("about/index.html", redirect_stub("../#about", "about/"))
    print("Done.")


if __name__ == "__main__":
    main()
