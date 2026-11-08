#!/usr/bin/env python3
"""Learn hub + one static page per subject, generated from learn/subjects.json.

  python3 learn/build.py            build learn/index.html and learn/<slug>/index.html
  python3 learn/build.py list       list subjects

Static pages (not JS routing) so every subject has its own URL and its own
share preview. Edit subjects.json, then run this again.
"""
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SUBJECTS = os.path.join(HERE, "subjects.json")
SITE = os.path.join(ROOT, "site.json")
LANGS = ("en", "bn", "ar")

FONTS = ("https://fonts.googleapis.com/css2?family=Galada&family=Cormorant+Garamond:wght@500;600"
         "&family=Tiro+Bangla&family=Hind+Siliguri:wght@400;500;600"
         "&family=Noto+Naskh+Arabic:wght@400;600&family=JetBrains+Mono:wght@400;500&display=swap")

UI = {
    "home":        {"en": "Nijer Khata", "bn": "নিজের খাতা", "ar": "نيجِر خاتا"},
    "learn":       {"en": "Learn", "bn": "শেখার কেন্দ্র", "ar": "مركز التعلم"},
    "learnLead":   {"en": "Structured learning paths, one page per subject. Pick a subject to see its phases.",
                    "bn": "সুশৃঙ্খল শেখার পথ, প্রতিটি বিষয়ের আলাদা পেজ। বিষয় বেছে নিন, ধাপগুলো দেখুন।",
                    "ar": "مسارات تعلّم منظمة، صفحة مستقلة لكل موضوع. اختر موضوعًا لتتعرف على مراحله."},
    "back":        {"en": "Back to Learn", "bn": "শেখার কেন্দ্রে ফিরুন", "ar": "العودة إلى مركز التعلم"},
    "home2":       {"en": "Home", "bn": "হোম", "ar": "الرئيسية"},
    "phase":       {"en": "Phase", "bn": "ধাপ", "ar": "المرحلة"},
    "subjects":    {"en": "subjects", "bn": "বিষয়", "ar": "موضوعات"},
    "phases":      {"en": "phases", "bn": "ধাপ", "ar": "مراحل"},
    "planned":     {"en": "Planned", "bn": "পরিকল্পিত", "ar": "مخطط"},
    "active":      {"en": "In progress", "bn": "চলমান", "ar": "قيد التنفيذ"},
    "done":        {"en": "Completed", "bn": "সম্পন্ন", "ar": "مكتمل"},
    "logTitle":    {"en": "Log your progress", "bn": "আপনার অগ্রগতি লিখুন", "ar": "سجّل تقدمك"},
    "logLead":     {"en": "From the shell in the project folder, record what you studied. The entry is saved with Dhaka and UTC time.",
                    "bn": "প্রজেক্ট ফোল্ডারের শেল থেকে যা পড়লেন তা লিখুন। এন্ট্রিতে ঢাকা ও ইউটিসি সময় যুক্ত হবে।",
                    "ar": "من الطرفية داخل مجلد المشروع، سجّل ما درسته. يُحفظ الإدخال مع توقيت دكا والتوقيت العالمي."},
    "prev":        {"en": "Previous", "bn": "আগের বিষয়", "ar": "السابق"},
    "next":        {"en": "Next", "bn": "পরের বিষয়", "ar": "التالي"},
    "footer":      {"en": "Track every step. Keep it inheritable.", "bn": "প্রতিটি ধাপ লিখে রাখুন। উত্তরাধিকারযোগ্য রাখুন।",
                    "ar": "تتبّع كل خطوة. واجعلها قابلة للتوارث."},
    "mj":          {"en": "MJ Ahmad", "bn": "এম জে আহমদ", "ar": "إم جي أحمد"},
    "mjBack":      {"en": "Main site", "bn": "মূল সাইট", "ar": "الموقع الرئيسي"},
    "theme":       {"en": "Theme", "bn": "থিম", "ar": "المظهر"},
}


def esc(v):
    return html.escape(str(v), quote=True)


def bi(d):
    """Render a {lang: text} dict as data-* attributes; learn.js picks the active one."""
    return " ".join(f'data-{k}="{esc(d[k])}"' for k in LANGS if d.get(k))


def txt(d):
    return d.get("en", "")


def ui(key):
    return bi(UI[key])


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_config():
    cfg = load_json(SUBJECTS, None)
    if cfg is None:
        sys.exit(f"Error: {SUBJECTS} not found")
    subjects = cfg.get("subjects", [])
    groups = cfg.get("groups", {})
    slugs = [s["slug"] for s in subjects]
    if len(set(slugs)) != len(slugs):
        sys.exit("Error: duplicate slug in subjects.json")
    for s in subjects:
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", s["slug"]):
            sys.exit(f"Error: bad slug '{s['slug']}' (use a-z, 0-9, dash)")
        if s.get("group") not in groups:
            sys.exit(f"Error: unknown group '{s.get('group')}' for {s['slug']}")
    return subjects, groups


def head(title, desc, url, depth_css, lang_default="en"):
    return f"""<!DOCTYPE html>
<html lang="{lang_default}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="theme-color" content="#0d1b1f">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Nijer Khata · নিজের খাতা">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{esc(url)}">
<meta property="og:image" content="{esc(url.split('/learn')[0])}/assets/branding/og/og-1200x630.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<link rel="icon" type="image/png" sizes="32x32" href="{depth_css}assets/branding/logos/favicon/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="{depth_css}assets/branding/logos/app-icons/ios-icon-180.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{depth_css}learn/learn.css">
</head>"""


def header_html(home_rel):
    return f"""<header class="top">
  <a class="brand" href="{home_rel}">
    <img src="{home_rel}assets/logo.png" alt="" width="44" height="44" onerror="this.remove()">
    <span class="brand-name" {ui('home')}>{esc(txt(UI['home']))}</span>
  </a>
  <div class="tools">
    <div class="lang" role="group" aria-label="Language">
      <button type="button" data-lang="en" aria-pressed="true">EN</button>
      <button type="button" data-lang="bn" aria-pressed="false">বাংলা</button>
      <button type="button" data-lang="ar" aria-pressed="false">العربية</button>
    </div>
    <button type="button" id="theme" class="theme-btn" aria-label="Theme"></button>
  </div>
</header>"""


FOOT_JS = '<script src="{rel}learn/learn.js"></script>\n</body>\n</html>\n'


def footer_html(mj_rel):
    return f"""<footer class="site-foot">
  <span {ui('footer')}>{esc(txt(UI['footer']))}</span>
  <a href="{mj_rel}"><span {ui('mjBack')}>{esc(txt(UI['mjBack']))}</span> · <span {ui('mj')}>{esc(txt(UI['mj']))}</span> ←</a>
</footer>"""


def hub_page(subjects, groups, site_url):
    url = f"{site_url}/learn/"
    title = f"{txt(UI['learn'])} · {txt(UI['home'])}"
    desc = txt(UI["learnLead"])
    parts = [head(title, desc, url, "../")]
    parts.append('<body>\n<div class="wrap">\n' + header_html("../"))
    parts.append(f'<section class="hero"><p class="kicker" {ui("learn")}>{esc(txt(UI["learn"]))}</p>'
                 f'<h1 {ui("learn")}>{esc(txt(UI["learn"]))}</h1>'
                 f'<p class="lead" {ui("learnLead")}>{esc(txt(UI["learnLead"]))}</p>'
                 f'<p class="count">{len(subjects)} <span {ui("subjects")}>{esc(txt(UI["subjects"]))}</span></p></section>')
    for gkey, gname in groups.items():
        items = [s for s in subjects if s["group"] == gkey]
        if not items:
            continue
        parts.append(f'<section class="group"><h2 {bi(gname)}>{esc(txt(gname))}</h2><div class="cards">')
        for s in items:
            parts.append(f"""<a class="card" href="{s['slug']}/">
  <span class="card-name" {bi(s['name'])}>{esc(txt(s['name']))}</span>
  <span class="card-sum" {bi(s.get('summary', {}))}>{esc(txt(s.get('summary', {})))}</span>
  <span class="card-meta"><span {ui('phases')}>{esc(txt(UI['phases']))}</span> · {len(s['phases'])} · <span {ui(s.get('status', 'planned'))}>{esc(txt(UI.get(s.get('status', 'planned'), UI['planned'])))}</span></span>
</a>""")
        parts.append("</div></section>")
    parts.append(footer_html("../../"))
    parts.append("</div>\n" + FOOT_JS.format(rel="../"))
    return "\n".join(parts)


def subject_page(s, idx, subjects, site_url):
    slug = s["slug"]
    name, summ = s["name"], s.get("summary", {})
    status = s.get("status", "planned")
    url = f"{site_url}/learn/{slug}/"
    title = f"{txt(name)} · {txt(UI['learn'])} · {txt(UI['home'])}"
    desc = txt(summ) or txt(UI["learnLead"])
    phases = []
    for i, p in enumerate(s["phases"], 1):
        items = "".join(f"<li>{esc(it)}</li>" for it in p["items"])
        phases.append(f"""<li class="phase"><span class="phase-no mono">{i:02d}</span>
  <div><h2 {bi(p['title'])}>{esc(txt(p['title']))}</h2><ul>{items}</ul></div></li>""")
    prev_s = subjects[idx - 1] if idx > 0 else None
    next_s = subjects[idx + 1] if idx < len(subjects) - 1 else None
    nav = []
    if prev_s:
        nav.append(f'<a href="../{prev_s["slug"]}/" class="pn"><small {ui("prev")}>{esc(txt(UI["prev"]))}</small>'
                   f'<span {bi(prev_s["name"])}>{esc(txt(prev_s["name"]))}</span></a>')
    if next_s:
        nav.append(f'<a href="../{next_s["slug"]}/" class="pn pn-next"><small {ui("next")}>{esc(txt(UI["next"]))}</small>'
                   f'<span {bi(next_s["name"])}>{esc(txt(next_s["name"]))}</span></a>')
    parts = [head(title, desc, url, "../../")]
    parts.append('<body>\n<div class="wrap">\n' + header_html("../../"))
    parts.append(f"""<nav class="crumbs" aria-label="breadcrumb">
  <a href="../../" {ui('home2')}>{esc(txt(UI['home2']))}</a> <span>/</span>
  <a href="../" {ui('learn')}>{esc(txt(UI['learn']))}</a> <span>/</span>
  <span {bi(name)}>{esc(txt(name))}</span>
</nav>
<section class="hero">
  <span class="status s-{esc(status)}" {ui(status)}>{esc(txt(UI.get(status, UI['planned'])))}</span>
  <h1 {bi(name)}>{esc(txt(name))}</h1>
  <p class="lead" {bi(summ)}>{esc(txt(summ))}</p>
</section>
<ol class="phases">
{chr(10).join(phases)}
</ol>
<section class="log-box">
  <h2 {ui('logTitle')}>{esc(txt(UI['logTitle']))}</h2>
  <p {ui('logLead')}>{esc(txt(UI['logLead']))}</p>
  <pre class="mono">./khata log "{esc(txt(name))}: today's progress" --category learning --tag {slug}</pre>
</section>
<nav class="pn-row" aria-label="subjects">{''.join(nav)}</nav>
""")
    parts.append(footer_html("../../../"))
    parts.append("</div>\n" + FOOT_JS.format(rel="../../"))
    return "\n".join(parts)


def main():
    subjects, groups = load_config()
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        for s in subjects:
            print(f"{s['slug']:12s} {txt(s['name']):14s} {s['group']:10s} {s.get('status', 'planned')}")
        return
    site_url = load_json(SITE, {}).get("site_url", "").rstrip("/")
    if not site_url.startswith("http"):
        sys.exit("Error: site.json needs a site_url starting with http(s)://")

    os.makedirs(HERE, exist_ok=True)
    with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as f:
        f.write(hub_page(subjects, groups, site_url))
    for i, s in enumerate(subjects):
        d = os.path.join(HERE, s["slug"])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
            f.write(subject_page(s, i, subjects, site_url))
    print(f"Built learn hub + {len(subjects)} subject pages")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:  # e.g. piping into head
        sys.exit(0)
