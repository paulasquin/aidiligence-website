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

# Publisher of the site (mentions légales). By choice, neither the registered office nor a
# phone number is published: the SIREN number identifies the company.
PUBLISHER = {
    "name": "Guardia",
    "form": "société par actions simplifiée (SAS) au capital de 1\u00a0000\u00a0€",
    "siren": "910 991 140",
    "vat": "FR81910991140",
    "director": "Paul Asquin, Président",
    "email": "contact@aidiligence.eu",
}

LINKEDIN_SVG = (
    '<svg viewBox="0 0 448 512" aria-hidden="true"><path d="M100.28 448H7.4V148.9h92.88zM53.79 '
    '108.1C24.09 108.1 0 83.5 0 53.8a53.79 53.79 0 0 1 107.58 0c0 29.7-24.1 54.3-53.79 54.3zM447.9 '
    '448h-92.68V302.4c0-34.7-12.4-58.4-43.4-58.4-23.7 0-37.8 15.9-44 31.3-2.3 5.5-2.9 13.2-2.9 '
    '20.9V448h-92.8s1.2-241.1 0-266.1h92.8v37.7c12.3-19 34.4-46.1 83.7-46.1 61.1 0 106.9 39.9 '
    '106.9 125.7V448z"/></svg>'
)

# Line-art icons, drawn with primitives so they stay crisp at any size.
ICON_SEARCH = ('<svg viewBox="0 0 24 24" aria-hidden="true">'
               '<circle cx="10.4" cy="10.4" r="6"/>'
               '<path d="M14.9 14.9L20 20"/></svg>')
ICON_COMPASS = ('<svg viewBox="0 0 24 24" aria-hidden="true">'
                '<circle cx="12" cy="12" r="8.6"/>'
                '<path d="M14.9 9.1l-1.6 4.2-4.2 1.6 1.6-4.2z"/></svg>')
ICON_CODE = ('<svg viewBox="0 0 24 24" aria-hidden="true">'
             '<path d="M8.6 7.4L4 12l4.6 4.6M15.4 7.4L20 12l-4.6 4.6M13.4 5.6l-2.8 12.8"/></svg>')

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

META_TITLE = ("AI Diligence — Conduite et audit de projets d'IA",
              "AI Diligence — AI project leadership and due diligence")
META_DESC = ("AI Diligence conduit, construit et audite des projets d'intelligence artificielle : "
             "conduite de projets IA, ingénierie IA et MLOps, due diligence de stack IA.",
             "AI Diligence leads, builds and audits artificial intelligence projects: AI project "
             "leadership, AI and MLOps engineering, AI stack due diligence.")

# The name says both trades: due diligence, and the stagecoach — the diligence,
# driven from departure to arrival.
SERVICE_LINES = [
    ("Conduite de projets IA", "AI project leadership"),
    ("Ingénierie IA &amp; MLOps", "AI &amp; MLOps engineering"),
    ("Due diligence IA", "AI due diligence"),
]

# Facts (roles, dates, team sizes, missions) come from paulasquin.com, where the
# full career is told; this site only points to it.
SERVICES = [
    ("lead", "#6fd6ff", ICON_COMPASS, ("Conduite de projets IA", "AI project leadership"),
     ("Faire aboutir un projet d'IA, du cadrage à la mise en production : choix des modèles et de "
      "l'architecture, constitution et encadrement de l'équipe, priorités alignées sur les besoins "
      "du métier.",
      "Taking an AI project from framing to production: choice of models and architecture, building "
      "and leading the team, priorities aligned with business needs."),
     [("Head of AI ou Lead AI à temps partagé", "Fractional Head of AI or Lead AI"),
      ("Cadrage, faisabilité et budget", "Framing, feasibility and budget"),
      ("Recrutement et montée en compétence de l'équipe", "Hiring and upskilling the team"),
      ("Feuille de route et suivi de la livraison", "Roadmap and delivery follow-up")],
     ("Head of AI chez AIVE, Acolad et Ocus, avec des équipes jusqu'à 7 ingénieurs et docteurs.",
      "Head of AI at AIVE, Acolad and Ocus, with teams of up to 7 engineers and PhDs.")),
    ("build", "#4fe0c0", ICON_CODE, ("Ingénierie IA &amp; MLOps", "AI &amp; MLOps engineering"),
     ("Concevoir, entraîner et mettre en production des systèmes d'IA, puis les faire vivre : "
      "qualité, coûts et performances suivis dans la durée.",
      "Designing, training and taking AI systems to production, then keeping them running: quality, "
      "costs and performance monitored over time."),
     [("Vision : CNN, vision transformers, estimation de pose", "Vision: CNNs, vision transformers, pose estimation"),
      ("Langage : LLM, RAG, agents, appels de fonctions", "Language: LLMs, RAG, agents, function calling"),
      ("IA embarquée, sans envoi dans le cloud", "Embedded AI, with nothing sent to the cloud"),
      ("AWS, Azure, GCP, Scaleway, Modal, Kubernetes", "AWS, Azure, GCP, Scaleway, Modal, Kubernetes")],
     ("Agents RAG pour Bivwak!, plateforme médicale Alveo, caméra embarquée de Guardia.",
      "RAG agents for Bivwak!, the Alveo medical platform, Guardia's embedded camera.")),
    ("audit", "#a78bff", ICON_SEARCH, ("Due diligence IA", "AI due diligence"),
     ("Nos services de due diligence IA offrent une évaluation complète des fondations "
      "technologiques d'une entreprise, en complément de la due diligence traditionnelle.",
      "Our AI due diligence services provide a comprehensive evaluation of a company's "
      "technological foundation, enhancing traditional due diligence efforts."),
     [("Avant un investissement, une acquisition ou un choix stratégique",
       "Before an investment, an acquisition or a strategic choice"),
      ("Huit axes, du produit aux coûts et aux licences", "Eight focus areas, from product to costs and licensing"),
      ("Des recommandations techniques précises", "Precise technology recommendations")],
     ("Audit de la stack technique de Bivwak!, l'incubateur de start-up de BNP Paribas.",
      "Audit of the tech stack of Bivwak!, BNP Paribas' startup incubator.")),
]

STEPS = [
    (("Cadrer", "Frame"),
     ("Le besoin, les données disponibles, la faisabilité, le budget et les critères de réussite.",
      "The need, the data at hand, feasibility, budget and success criteria.")),
    (("Évaluer", "Assess"),
     ("L'existant et l'état de l'art : audit de la stack, comparaison de modèles, choix "
      "d'architecture.",
      "What exists and the state of the art: stack audit, model comparison, architecture choices.")),
    (("Construire", "Build"),
     ("Un prototype, puis les modèles, les pipelines et l'intégration au produit, par itérations "
      "courtes.",
      "A prototype, then the models, the pipelines and the product integration, in short "
      "iterations.")),
    (("Livrer et transmettre", "Ship and hand over"),
     ("La mise en production, le suivi des coûts et des performances, la formation des équipes.",
      "Production deployment, cost and performance monitoring, team training.")),
]

MISSIONS = [
    ("Bivwak!", ("Lead AI · 2025–2026", "Lead AI · 2025–2026"),
     ("Incubateur de start-up de BNP Paribas", "BNP Paribas' startup incubator"),
     ("un agent IA <em>sous haute sécurité</em>", "an AI agent <em>under strict security</em>"),
     ("Audit de la stack technique, puis conception et développement d'une IA agentique fondée sur "
      "du RAG et des appels de fonctions, sous de fortes contraintes de sécurité. Elle ingère des "
      "PDF, des présentations, des pages web et des podcasts ; les profils juniors ont été formés.",
      "An audit of the tech stack, then the design and development of an agentic AI based on RAG "
      "and function calling, under strict security constraints. It ingests PDFs, slide decks, web "
      "pages and podcasts; the junior staff were trained."),
     [("Agents", "Agents"), ("RAG", "RAG"), ("Appel de fonctions", "Function calling"),
      ("LangChain", "LangChain"), ("AWS", "AWS")], "bivwak"),
    ("Alveo", ("Lead AI · 2025–2026", "Lead AI · 2025–2026"),
     ("Logiciel médical · réanimation", "Medical software · intensive care"),
     ("analyser <em>la ventilation pulmonaire</em>", "analysing <em>lung ventilation</em>"),
     ("Une plateforme web qui analyse les enregistrements de tomographie par impédance électrique "
      "(EIT) des patients en réanimation : lecture des fichiers Dräger et SenTec, reconstruction "
      "des images de ventilation, calcul de la surdistension et du collapsus pour déterminer la PEP "
      "optimale.",
      "A web platform that analyses electrical impedance tomography (EIT) recordings of "
      "intensive-care patients: reading Dräger and SenTec files, reconstructing ventilation "
      "images, computing overdistension and collapse to find the optimal PEEP."),
     [("Reconstruction d'images EIT", "EIT image reconstruction"),
      ("Interface web · CLI · API Python", "Web interface · CLI · Python API")], "alveo"),
]

EXPERIENCE = [  # company, role (fr, en), years, what (fr, en), anchor on paulasquin.com
    ("Ocus", ("Head of AI", "Head of AI"), "2025",
     ("l'image retravaillée par l'IA", "images reworked by AI"), "ocus"),
    ("Acolad", ("Head of AI", "Head of AI"), "2024",
     ("l'IA au service des langues", "AI for languages"), "acolad"),
    ("AIVE", ("Head of AI", "Head of AI"), "2022–2024",
     ("le montage vidéo par l'IA", "AI-powered video editing"), "aive"),
    ("Baracoda", ("Data scientist senior en vision · Lead MLOps", "Senior computer vision data scientist · MLOps lead"),
     "2021–2022", ("analyser la peau", "analysing skin"), "baracoda"),
    ("Guardia", ("Cofondateur &amp; CTO", "Co-founder &amp; CTO"), "2020–2023",
     ("protéger les enfants au bord de la piscine", "protecting children around the pool"), "guardia"),
    ("Meero", ("Data scientist en vision par ordinateur", "Computer vision data scientist"), "2019–2021",
     ("sublimer les photos", "enhancing photos"), "meero"),
]

PRODUCTS = [
    ("Revela", "https://revela.aidiligence.eu", "revela.png",
     ("Retoucher ses photos sur Android avec les réglages de Lightroom : mêmes curseurs, rendu "
      "proche, préréglages .xmp. Tout est traité sur le téléphone.",
      "Edit photos on Android with Lightroom's adjustments: the same sliders, a close rendering, "
      ".xmp presets. Everything is processed on the phone.")),
    ("Siflo", "https://siflo.aidiligence.eu", "siflo.png",
     ("Transmettre les signaux de sifflet et les messages d'un groupe, de téléphone à téléphone, "
      "même sans réseau, en canyon, en escalade ou en spéléo.",
      "Pass whistle signals and messages within a group, from phone to phone, even without a "
      "network, when canyoning, climbing or caving.")),
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
    ("Diplômé de Centrale Paris (MSc en intelligence artificielle et informatique) et de Centrale "
     "Nantes (MSc en robotique), j'ai été data scientist en vision par ordinateur chez Meero puis "
     "chez Baracoda, cofondateur et CTO de Guardia, Head of AI chez AIVE, Acolad et Ocus, et Lead AI "
     "pour Bivwak!",
     "A graduate of Centrale Paris (MSc in artificial intelligence and computer science) and "
     "Centrale Nantes (MSc in robotics), I was a computer vision data scientist at Meero, then at "
     "Baracoda, co-founder and CTO of Guardia, Head of AI at AIVE, Acolad and Ocus, and Lead AI for "
     "Bivwak!"),
    ("J'ai créé AI Diligence en 2023 pour mettre cette expérience au service d'autres équipes : "
     "conduire leurs projets d'IA, les construire avec elles, ou les évaluer avant une décision.",
     "I created AI Diligence in 2023 to put this experience at the service of other teams: "
     "leading their AI projects, building them together, or assessing them before a decision."),
]

# Same four facts as paulasquin.com's About card.
FACTS = [
    ("Centrale Paris", ("MSc IA &amp; informatique", "MSc AI &amp; computer science")),
    ("Centrale Nantes", ("MSc robotique", "MSc robotics")),
    ("Head of AI", ("AIVE · Acolad · Ocus", "AIVE · Acolad · Ocus")),
    ("CTO", ("Guardia · 2020–2023", "Guardia · 2020–2023")),
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
    services = "\n".join(f"""          <article class="tile offer reveal" style="--accent:{colour}">
            <span class="pillar-icon">{icon}</span>
            <span class="offer-num">0{i}</span>
            {t("h3", f"sv.{key}.t", *name)}
            {t("p", f"sv.{key}.p", *text)}
            <ul class="offer-list">
{chr(10).join(f'              {t("li", f"sv.{key}.b{j}", *b)}' for j, b in enumerate(bullets, 1))}
            </ul>
            {t("p", f"sv.{key}.proof", *proof, ' class="offer-proof"')}{
            f'''
            <a class="offer-link" href="#due-diligence">{t("span", "sv.audit.more", "Les 8 axes d'audit", "The 8 focus areas")} <span class="arrow">→</span></a>''' if key == "audit" else ""}
          </article>""" for i, (key, colour, icon, name, text, bullets, proof) in enumerate(SERVICES, 1))
    steps = "\n".join(f"""            <li class="step">
              <span class="step-num">0{i}</span>
              {t("h3", f"st{i}.t", *title)}
              {t("p", f"st{i}.p", *text)}
            </li>""" for i, (title, text) in enumerate(STEPS, 1))
    missions = "\n".join(f"""          <article class="tile mission reveal">
            <p class="mission-tag"><b>{t("span", f"ms{i}.role", *role)}</b>{t("span", f"ms{i}.ctx", *ctx)}</p>
            <h3><span class="mission-name">{name},</span> {t("span", f"ms{i}.t", *title)}</h3>
            {t("p", f"ms{i}.p", *text)}
            <ul class="chips">{"".join(t("li", f"ms{i}.c{j}", *c) for j, c in enumerate(chips, 1))}</ul>
            <a class="offer-link" href="{HUB}/#{anchor}" target="_blank" rel="noopener">paulasquin.com <span class="arrow">↗</span></a>
          </article>""" for i, (name, role, ctx, title, text, chips, anchor) in enumerate(MISSIONS, 1))
    experience = "\n".join(
        f'            <li><a href="{HUB}/#{anchor}" target="_blank" rel="noopener">'
        f'<span class="xp-name">{name}</span>{t("span", f"xp{i}.role", *role, " class=\"xp-role\"")}'
        f'{t("span", f"xp{i}.what", *what, " class=\"xp-what\"")}<span class="xp-year">{years}</span></a></li>'
        for i, (name, role, years, what, anchor) in enumerate(EXPERIENCE, 1))
    products = "\n".join(f"""          <a class="tile product reveal" href="{url}" target="_blank" rel="noopener">
            <img src="assets/img/{img}" alt="" width="64" height="64" loading="lazy">
            <span class="product-body">
              {t("span", f"pr{i}.tag", "Application Android", "Android app", ' class="product-tag"')}
              <span class="product-name">{name}</span>
              {t("span", f"pr{i}.p", *text, ' class="product-text"')}
              <span class="product-link">{url.removeprefix("https://")} ↗</span>
            </span>
          </a>""" for i, (name, url, img, text) in enumerate(PRODUCTS, 1))
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
    facts = "\n".join(f'              <li><b>{name}</b>{t("span", f"ab.f{i}", *sub)}</li>'
                      for i, (name, sub) in enumerate(FACTS, 1))

    return f"""    <!-- Hero -->
    <section id="top" class="scene hero" data-shape="mark" data-side="1">
      <div class="wrap">
        <div class="hero-content">
          <p class="eyebrow"><span class="pulse-dot"></span>{t("span", "hero.eyebrow", "Conduite et audit de projets d'IA", "AI project leadership and due diligence")}</p>
          <h1 class="hero-title">
            <span class="ht-line"><span class="ht-word">AI</span></span>
            <span class="ht-line"><span class="ht-word ht-glow">Diligence</span></span>
          </h1>
          <ul class="service-lines">
{lines}
          </ul>
          {t("p", "hero.sub", "Cadrer, construire, mettre en production, ou évaluer avant d'investir : AI Diligence conduit vos projets d'intelligence artificielle, de la vision par ordinateur aux agents de langage.", "Framing, building, taking to production, or assessing before you invest: AI Diligence leads your artificial intelligence projects, from computer vision to language agents.", ' class="hero-sub"')}
          <div class="hero-cta">
            {linkedin_button("hero.cta1", "Parler de votre projet", "Discuss your project")}
            <a href="#services" class="btn btn-ghost magnetic">{t("span", "hero.cta2", "Nos services", "Our services")}</a>
          </div>
        </div>
      </div>
      <div class="scroll-cue" aria-hidden="true"><span></span>{t("i", "hero.scroll", "Défiler", "Scroll")}</div>
    </section>

    <!-- Services -->
    <section id="services" class="scene scene-short" data-shape="galaxy" data-side="0">
      <div class="wrap">
        <div class="intro reveal">
          {t("p", "sv.k", "Services", "Services", ' class="kicker"')}
          {t("h2", "sv.t", "Conduire, construire, <em>évaluer</em>", "Lead, build, <em>assess</em>", ' class="title title-xl"')}
          {t("p", "sv.p", "Diligence : le soin de l'audit, et la voiture qu'on mène jusqu'à destination. Trois façons d'intervenir sur un projet d'intelligence artificielle, seules ou combinées.", "Diligence: the care of an audit, and the stagecoach driven all the way to its destination. Three ways to work on an artificial intelligence project, alone or combined.", ' class="lede center"')}
        </div>
        <div class="tiles offers">
{services}
        </div>
      </div>
    </section>

    <!-- Method -->
    <section id="method" class="scene" data-shape="path" data-side="1">
      <div class="wrap">
        <div class="card card-wide reveal">
          {t("p", "st.k", "Méthode · la conduite", "Method · the driving", ' class="kicker"')}
          {t("h2", "st.t", "Un projet d'IA, <em>conduit de bout en bout</em>", "An AI project, <em>driven end to end</em>", ' class="title"')}
          {t("p", "st.p", "Comme une diligence : un itinéraire clair, des relais, et quelqu'un aux rênes jusqu'à l'arrivée.", "Like a stagecoach: a clear route, staging posts, and someone at the reins until arrival.", ' class="lede"')}
          <ol class="steps">
{steps}
          </ol>
        </div>
      </div>
    </section>

    <!-- References -->
    <section id="references" class="scene" data-shape="net" data-side="-1">
      <div class="wrap">
        <div class="intro reveal">
          {t("p", "rf.k", "Références", "References", ' class="kicker"')}
          {t("h2", "rf.t", "Des missions <em>menées de bout en bout</em>", "Missions <em>carried end to end</em>", ' class="title title-xl"')}
        </div>
        <div class="tiles missions">
{missions}
        </div>
        <div class="xp reveal">
          {t("p", "xp.k", "Avant AI Diligence : l'expérience du fondateur", "Before AI Diligence: the founder's experience", ' class="kicker"')}
          <ul class="xp-list">
{experience}
          </ul>
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
    <section id="expertise" class="scene" data-shape="orb" data-side="-1">
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

    <!-- Products -->
    <section id="products" class="scene scene-short" data-shape="galaxy" data-side="0">
      <div class="wrap">
        <div class="intro reveal">
          {t("p", "pr.k", "Produits", "Products", ' class="kicker"')}
          {t("h2", "pr.t", "Des applications <em>développées en interne</em>", "Apps <em>built in-house</em>", ' class="title"')}
        </div>
        <div class="tiles products">
{products}
        </div>
      </div>
    </section>

    <!-- About -->
    <section id="about" class="scene" data-shape="mark" data-side="1">
      <div class="wrap">
        <div class="card about reveal">
          <img class="portrait" src="assets/img/paul-asquin.jpg" alt="Paul Asquin" loading="lazy" width="720" height="960">
          <div>
            {t("p", "ab.k", "À propos · Fondateur", "About · Founder", ' class="kicker"')}
            <h2 class="title">Paul <em>Asquin</em></h2>
{bio}
            <ul class="facts">
{facts}
            </ul>
            <p class="card-cta"><a class="btn btn-ghost magnetic" href="{HUB}" target="_blank" rel="noopener">{t("span", "ab.hub", "Tout le parcours sur paulasquin.com", "The full story on paulasquin.com")}<span class="arrow">↗</span></a></p>
          </div>
        </div>
      </div>
    </section>

    <!-- Contact -->
    <section id="contact" class="scene contact" data-shape="galaxy" data-side="0">
      <div class="wrap">
        <div class="intro reveal">
          {t("p", "ct.k", "Contact", "Contact", ' class="kicker"')}
          {t("h2", "ct.t", "Un projet d'IA <em>à conduire ou à évaluer ?</em>", "An AI project <em>to lead or to assess?</em>", ' class="title title-xl"')}
          {t("p", "ct.p", "Parlons de votre besoin. Réponse sur LinkedIn ou par e-mail.", "Let's talk about your needs. Answers on LinkedIn or by email.", ' class="lede center"')}
          <div class="hero-cta center">
            {linkedin_button("ct.cta", "Écrire sur LinkedIn", "Write on LinkedIn")}
            <a class="btn btn-ghost magnetic" href="mailto:{EMAIL}">{EMAIL}</a>
          </div>
        </div>
      </div>
      <footer class="footer">
        <span>© {SITE} · Guardia SAS — {t("span", "ft.tag", "Conduite et audit de projets d'IA", "AI project leadership and due diligence")}</span>
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
      <a href="#services">Services</a>
      {t("a", "nav.method", "Méthode", "Method", ' href="#method"')}
      {t("a", "nav.refs", "Références", "References", ' href="#references"')}
      <a href="#due-diligence">Due diligence</a>
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
            SIREN {g["siren"]}, TVA intracommunautaire {g["vat"]}.<br>
            Directeur de la publication : {g["director"]}.<br>
            Contact : <a href="mailto:{g["email"]}">{g["email"]}</a>.</p>

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
          <p>Published by {g["name"]} SAS, SIREN {g["siren"]}, VAT {g["vat"]}.
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
