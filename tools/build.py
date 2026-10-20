#!/usr/bin/env python3
"""Build docs/ from src/i18n/<lang>.json + src/data.json.

  python3 tools/build.py            every language with a translation file
  python3 tools/build.py --cards    also redraw the share cards (docs/<lang>/card.png)

English sits at the root, every other language under /<code>/. Each page gets a
plain-text twin (guide.txt), a QR code, hreflang links and JSON-LD.
"""
import html, json, pathlib, sys, urllib.parse
from datetime import date

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / "src", ROOT / "docs"
DATA = json.loads((SRC / "data.json").read_text())
SITE = DATA["site"]
CHECKED = "2026-10-20"

# order shown in the language menu
ORDER = ["en", "es", "tl", "th", "vi", "ko", "ja", "de", "it", "zh", "lo", "km"]
WEBFONT = {"th": "Noto+Sans+Thai", "lo": "Noto+Sans+Lao", "km": "Noto+Sans+Khmer"}
# share buttons, most-used apps first for each language
SHARE_ORDER = {
    "en": ["whatsapp", "facebook", "messenger", "email", "sms", "line", "telegram", "x", "bluesky", "reddit"],
    "es": ["whatsapp", "facebook", "messenger", "sms", "email", "telegram", "x", "bluesky"],
    "tl": ["messenger", "facebook", "viber", "whatsapp", "sms", "email", "telegram", "x"],
    "th": ["line", "facebook", "messenger", "whatsapp", "sms", "email", "telegram", "x"],
    "vi": ["facebook", "messenger", "viber", "whatsapp", "telegram", "sms", "email", "x"],
    "ko": ["facebook", "sms", "telegram", "whatsapp", "line", "email", "x"],
    "ja": ["line", "x", "facebook", "messenger", "sms", "email", "whatsapp"],
    "de": ["whatsapp", "facebook", "telegram", "email", "sms", "messenger", "x", "bluesky"],
    "it": ["whatsapp", "facebook", "telegram", "email", "sms", "messenger", "x"],
    "zh": ["whatsapp", "telegram", "line", "facebook", "email", "sms", "x"],
    "lo": ["whatsapp", "facebook", "messenger", "line", "telegram", "sms", "email"],
    "km": ["telegram", "facebook", "messenger", "whatsapp", "line", "sms", "email"],
}
APP_NAME = {"whatsapp": "WhatsApp", "facebook": "Facebook", "messenger": "Messenger", "line": "LINE",
            "telegram": "Telegram", "viber": "Viber", "x": "X", "bluesky": "Bluesky", "reddit": "Reddit",
            "email": "Email", "sms": "SMS"}
COPY = {"en": "Copy", "es": "Copiar", "tl": "Kopyahin", "th": "คัดลอก", "vi": "Sao chép", "ko": "복사", "ja": "コピー",
        "de": "Kopieren", "it": "Copia", "zh": "复制", "lo": "ສຳເນົາ", "km": "ចម្លង"}
LINE_DESK = "https://line.me/R/ti/p/@964yxgnk"
HONGDAM = "https://hongdam.net/"
CMVD = "https://chiangmaivisadesk.com/"

e = html.escape


def ver(name):
    import hashlib
    return hashlib.sha1((OUT / "assets" / name).read_bytes()).hexdigest()[:8]


def q(s):
    return urllib.parse.quote(s, safe="")


def path_of(code):
    return "" if code == "en" else f"{code}/"


def url_of(code):
    return SITE + path_of(code)


def share_links(code, t, url):
    text = f'{t["meta"]["share_text"]}'
    both = f"{text} {url}"
    hrefs = {
        "whatsapp": f"https://wa.me/?text={q(both)}",
        "facebook": f"https://www.facebook.com/sharer/sharer.php?u={q(url)}",
        "messenger": f"fb-messenger://share/?link={q(url)}",
        "line": f"https://line.me/R/share?text={q(both)}",
        "telegram": f"https://t.me/share/url?url={q(url)}&text={q(text)}",
        "viber": f"viber://forward?text={q(both)}",
        "x": f"https://twitter.com/intent/tweet?text={q(text)}&url={q(url)}",
        "bluesky": f"https://bsky.app/intent/compose?text={q(both)}",
        "reddit": f"https://www.reddit.com/submit?url={q(url)}&title={q(t['meta']['title'])}",
        "email": f"mailto:?subject={q(t['meta']['title'])}&body={q(text + chr(10) + chr(10) + url)}",
        "sms": f"sms:?&body={q(both)}",
    }
    out = []
    for k in SHARE_ORDER.get(code, SHARE_ORDER["en"]):
        out.append(f'<a class="app app-{k}" href="{e(hrefs[k])}" target="_blank" rel="noopener" data-app="{k}">{APP_NAME[k]}</a>')
    return "".join(out)


def toolbar(code, t, url, where):
    u = t["ui"]
    return f"""<div class="kit" data-where="{where}">
  <p class="cta">{e(u['cta'])}</p>
  <div class="kit-main">
    <button class="btn primary js-share" type="button">{e(u['share'])}</button>
    <button class="btn js-copy" type="button" data-copied="{e(u['copied'])}">{e(u['copy_link'])}</button>
    <button class="btn js-qr" type="button">{e(u['show_qr'])}</button>
    <button class="btn js-print" type="button">{e(u['print'])}</button>
    <button class="btn js-install" type="button" hidden>{e(u['save_home'])}</button>
    <a class="btn" href="guide.txt" download>{e(u['download_text'])}</a>
  </div>
  <div class="apps">{share_links(code, t, url)}</div>
</div>"""


def sec(id_, h, body, t, cls=""):
    return f"""<section id="{id_}" class="{cls}">
<div class="sec-head"><h2>{e(h)}</h2><button class="sec-share js-sec-share" type="button" data-id="{id_}" aria-label="{e(t['ui']['share_this_section'])}: {e(h)}" title="{e(t['ui']['share_this_section'])}">↗</button></div>
{body}
</section>"""


def ul(items, cls=""):
    return f'<ul class="{cls}">' + "".join(f"<li>{e(i)}</li>" for i in items) + "</ul>"


def linkify(s):
    """Escape, then turn bare domains/paths we wrote into links."""
    out = e(s)
    for dom in ["va.gov/get-help-from-accredited-representative/find-rep", "veteranscrisisline.net/get-help-now/chat",
                "findahelpline.com", "thaipoliceonline.go.th", "ssa.gov/foreign"]:
        if dom in out:
            out = out.replace(dom, f'<a href="https://{dom}" rel="noopener">{dom}</a>', 1)
    return out


def build_page(code, t, langs):
    u, m = t["ui"], t["meta"]
    url = url_of(code)
    up = "" if code == "en" else "../"
    font = WEBFONT.get(code)
    font_link = (f'<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
                 f'<link href="https://fonts.googleapis.com/css2?family={font}:wght@400;600;700&display=swap" rel="stylesheet">') if font else ""
    alts = "".join(f'<link rel="alternate" hreflang="{langs[c]["meta"]["lang"]}" href="{url_of(c)}">' for c in langs)
    alts += f'<link rel="alternate" hreflang="x-default" href="{url_of("en")}">'
    cur = ' aria-current="page"'
    menu = "".join(f'<a href="{up}{path_of(c)}" lang="{langs[c]["meta"]["lang"]}"{cur if c == code else ""}>{e(langs[c]["meta"]["native"])}</a>' for c in langs)

    # start cards
    cards = "".join(f'<a class="card" href="#{c["to"]}"><b>{e(c["title"])}</b><span>{e(c["line"])}</span></a>' for c in t["start"]["cards"])

    # checklist
    b = t["before"]
    groups = ""
    for gi, g in enumerate(b["groups"]):
        items = "".join(f'<li><label><input type="checkbox" class="tick" data-k="g{gi}i{ii}"> <span>{e(i)}</span></label></li>' for ii, i in enumerate(g["items"]))
        groups += f'<div class="group"><h3>{e(g["h"])}</h3><ul class="checks">{items}</ul></div>'
    before = f'<p class="intro">{e(b["intro"])}</p>{groups}<p class="callout">{e(b["two"])}</p><p class="small">{e(u["ticked"])}</p>'

    helping = ul(t["helping"]["items"], "steps-list")

    c = t["credentials"]
    rows = "".join(f'<tr><th scope="row">{e(r["name"])}</th><td>{e(r["abroad"])}</td><td>{e(r["needs"])}</td></tr>' for r in c["rows"])
    creds = (f'<p class="intro">{e(c["intro"])}</p><div class="table-wrap"><table><thead><tr>'
             + "".join(f"<th scope=\"col\">{e(x)}</th>" for x in c["cols"]) + f'</tr></thead><tbody>{rows}</tbody></table></div><p>{e(c["note"])}</p>')

    i = t["idme"]
    steps = "".join(f'<li><h3>{e(s["h"])}</h3><p>{e(s["body"])}</p></li>' for s in i["steps"])
    idme = f'<ol class="steps">{steps}</ol><div class="callout"><h3>{e(i["nossn_h"])}</h3><p>{e(i["nossn"])}</p></div>'

    w = t["wrong"]
    wrong = f'<p class="intro">{e(w["intro"])}</p>' + "".join(
        f'<details id="w{n+1}"><summary>{e(it["q"])}</summary><p>{e(it["a"])}</p></details>' for n, it in enumerate(w["items"]))

    d = t["death"]
    death = f'<p class="intro">{e(d["intro"])}</p>' + "".join(f'<div class="block"><h3>{e(x["h"])}</h3><p>{e(x["body"])}</p></div>' for x in d["items"])

    p = t["paper"]
    L = p["labels"]
    routes = ""
    for r in DATA["routes"]:
        tr = p["routes"][r["id"]]
        rows = ""
        if r.get("form"):
            rows += f'<dt>{e(L["form"])}</dt><dd><a href="{e(r["form_url"])}" rel="noopener">{e(r["form"])}</a></dd>'
        if r.get("mail"):
            rows += f'<dt>{e(L["mail"])}</dt><dd class="addr" translate="no">{e(r["mail"])} <button class="mini js-copytext" type="button" data-text="{e(r["mail"])}" data-copied="{e(u["copied"])}">{COPY.get(code, "Copy")}</button></dd>'
        if r.get("fax"):
            rows += f'<dt>{e(L["fax"])}</dt><dd>{e(r["fax"])}' + (f' <span class="flag">{e(L["check"])}</span>' if r.get("fax_check") else "") + "</dd>"
        if r.get("phone"):
            rows += f'<dt>{e(L["phone"])}</dt><dd>' + " · ".join(f'<a href="tel:{x.replace(" ", "")}">{e(x)}</a>' for x in r["phone"].split(" · ")) + "</dd>"
        if r.get("email"):
            rows += f'<dt>{e(L["email"])}</dt><dd><a href="mailto:{e(r["email"])}">{e(r["email"])}</a></dd>'
        note = f'<p class="small">{linkify(tr["note"])}</p>' if tr.get("note") else ""
        routes += f'<div class="route" id="r-{r["id"]}"><h3>{e(tr["h"])}</h3><dl>{rows}</dl>{note}<p class="src"><a href="{e(r["src"])}" rel="noopener">↗ {e(urllib.parse.urlparse(r["src"]).netloc)}</a></p></div>'
    paper = f'<p class="intro">{e(p["intro"])}</p><div class="routes">{routes}</div>'

    ph = t["phone"]
    lines = ""
    for ln in DATA["lines"]:
        hours = ""
        if ln.get("tz"):
            hours = f'<span class="hours js-hours" data-tz="{ln["tz"]}" data-days="{",".join(map(str, ln["days"]))}" data-open="{ln["open"]}" data-close="{ln["close"]}" data-label="{e(u["your_time"])}" data-on="{e(u["open_now"])}" data-off="{e(u["closed_now"])}">{e(ph["days"])}, {ln["open"]}–{ln["close"]} ET</span>'
        elif ln.get("always"):
            hours = f'<span class="hours">{e(ph["anytime"])}</span>'
        lines += f'<li><b>{e(ph["lines"][ln["id"]])}</b> <a class="tel" href="tel:{ln["tel"]}">{e(ln["show"])}</a> {hours}</li>'
    phone = f'<p class="intro">{e(ph["intro"])}</p><ul class="lines">{lines}</ul>'

    help_ = "<ul>" + "".join(f"<li>{linkify(x)}</li>" for x in t["help"]["items"]) + "</ul>"
    s = t["scammers"]
    scams = (f'<p class="intro">{e(s["intro"])}</p><div class="two"><div><h3>{e(s["signs_h"])}</h3>'
             + "<ul class='signs'>" + "".join(f"<li>{e(x)}</li>" for x in s["signs"]) + "</ul></div>"
             + f'<div><h3>{e(s["do_h"])}</h3><ol class="do">' + "".join(f"<li>{e(x)}</li>" for x in s["do"]) + "</ol></div></div>")
    th = "<ul>" + "".join(f"<li>{linkify(x)}</li>" for x in t["thailand"]["items"]) + "</ul>"
    care = f'<p class="intro">{e(t["care"]["intro"])}</p><ul class="care">' + "".join(f"<li>{linkify(x)}</li>" for x in t["care"]["items"]) + "</ul>"
    share = "".join(f"<p>{e(x)}</p>" for x in t["share"]["lines"]) + toolbar(code, t, url, "end") + f'<figure class="qr-print"><img src="qr.svg" alt="QR" width="180" height="180"><figcaption>{e(url)}</figcaption></figure>'
    bots = f'<p>{e(t["bots"]["body"])}</p><p class="small"><a href="guide.txt">guide.txt</a> · <a href="{up}llms.txt">llms.txt</a> · <a href="{up}sitemap.xml">sitemap.xml</a></p>'
    sources = "<ol class='sources'>" + "".join(f'<li><a href="{e(x[1])}" rel="noopener">{e(x[0])}</a></li>' for x in DATA["sources"]) + "</ol>"

    toc_ids = [("before", t["before"]["h"]), ("helping", t["helping"]["h"]), ("credentials", t["credentials"]["h"]),
               ("idme", t["idme"]["h"]), ("wrong", t["wrong"]["h"]), ("death", t["death"]["h"]), ("paper", t["paper"]["h"]),
               ("phone", t["phone"]["h"]), ("help", t["help"]["h"]), ("scammers", t["scammers"]["h"]),
               ("thailand", t["thailand"]["h"]), ("care", t["care"]["h"]), ("share", t["share"]["h"])]
    toc = "".join(f'<li><a href="#{a}">{e(b)}</a></li>' for a, b in toc_ids)

    ld = [
        {"@context": "https://schema.org", "@type": "WebPage", "name": m["title"], "description": m["description"],
         "url": url, "inLanguage": m["lang"], "isAccessibleForFree": True, "dateModified": CHECKED,
         "audience": {"@type": "Audience", "audienceType": "US veterans and surviving spouses living outside the United States"},
         "publisher": {"@type": "Organization", "name": "Hongdam", "url": HONGDAM},
         "about": [{"@type": "GovernmentService", "name": "VA.gov sign-in"}, {"@type": "Thing", "name": "ID.me"},
                   {"@type": "GovernmentService", "name": "Dependency and Indemnity Compensation"}]},
        {"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": m["lang"],
         "mainEntity": [{"@type": "Question", "name": it["q"], "acceptedAnswer": {"@type": "Answer", "text": it["a"]}} for it in w["items"]]},
        {"@context": "https://schema.org", "@type": "HowTo", "name": i["h"], "inLanguage": m["lang"],
         "step": [{"@type": "HowToStep", "name": s_["h"], "text": s_["body"]} for s_ in i["steps"]]},
    ]
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)

    suggest = {c: {"name": langs[c]["meta"]["native"], "href": f"{up}{path_of(c)}"} for c in langs if c != code}

    return f"""<!doctype html>
<html lang="{m['lang']}" dir="{m['dir']}" translate="no" class="notranslate">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="google" content="notranslate">
<title>{e(m['title'])}</title>
<meta name="description" content="{e(m['description'])}">
<link rel="canonical" href="{url}">
{alts}
<meta property="og:type" content="website">
<meta property="og:title" content="{e(m['title'])}">
<meta property="og:description" content="{e(m['description'])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{url}card.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:locale" content="{m['lang'].replace('-', '_')}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(m['title'])}">
<meta name="twitter:description" content="{e(m['description'])}">
<meta name="twitter:image" content="{url}card.png">
<meta name="theme-color" content="#24406E">
<link rel="manifest" href="{up}manifest.webmanifest">
<link rel="icon" href="{up}assets/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{up}assets/icon-192.png">
{font_link}
<link rel="stylesheet" href="{up}assets/style.css?v={ver("style.css")}">
{ld_html}
</head>
<body class="notranslate lang-{code}" data-url="{url}" data-title="{e(m['title'])}" data-text="{e(m['share_text'])}" data-sw="{up}sw.js" data-ios="{e(u['save_home_ios'])}">
<a class="skip" href="#start">{e(t['start']['h'])}</a>
<header class="top">
  <div class="wrap top-row">
    <a class="brand" href="#">{e(m['card_title'])}</a>
    <div class="top-tools">
      <div class="size" role="group" aria-label="{e(u['text_size'])}"><button type="button" data-size="-1" aria-label="{e(u['text_size'])} −">A−</button><button type="button" data-size="1" aria-label="{e(u['text_size'])} +">A+</button></div>
      <details class="langs"><summary aria-label="{e(u['languages'])}">🌐 {e(m['native'])}</summary><nav class="lang-menu">{menu}</nav></details>
    </div>
  </div>
</header>
<div class="suggest" hidden data-langs='{e(json.dumps(suggest, ensure_ascii=False))}'></div>
<main>
<div class="hero"><div class="wrap">
  <p class="kicker">{e(t['hero']['kicker'])}</p>
  <h1>{e(t['hero']['h1'])}</h1>
  <p class="lede">{e(t['hero']['lede'])}</p>
  <p class="free">{e(u['free'])} {e(u['checked'])}</p>
  {toolbar(code, t, url, "top")}
</div></div>
<div class="wrap">
<section id="start"><h2>{e(t['start']['h'])}</h2><div class="cards">{cards}</div></section>
<nav class="toc" aria-label="{e(u['contents'])}"><h2>{e(u['contents'])}</h2><ol>{toc}</ol></nav>
{sec("before", b["h"], before, t)}
{sec("helping", t["helping"]["h"], helping, t)}
{sec("credentials", c["h"], creds, t)}
{sec("idme", i["h"], idme, t)}
{sec("wrong", w["h"], wrong, t)}
{sec("death", d["h"], death, t)}
{sec("paper", p["h"], paper, t)}
{sec("phone", ph["h"], phone, t)}
{sec("help", t["help"]["h"], help_, t)}
{sec("scammers", s["h"], scams, t, "alert")}
{sec("thailand", t["thailand"]["h"], th, t)}
{sec("care", t["care"]["h"], care, t, "care")}
{sec("share", t["share"]["h"], share, t, "share")}
{sec("bots", t["bots"]["h"], bots, t, "bots")}
</div>
</main>
<footer class="foot"><div class="wrap">
  <p>{e(t['foot']['made'])} <a href="{HONGDAM}">Hongdam</a> · <a href="{CMVD}">Chiang Mai Visa Desk</a> · <a href="{LINE_DESK}">{e(t['foot']['line'])}</a></p>
  <p>{e(t['foot']['not_gov'])} {e(u['checked'])}</p>
  <nav class="lang-foot">{menu}</nav>
  <details><summary>{e(u['sources'])}</summary>{sources}</details>
  <p><a href="#" class="top-link">↑ {e(u['top'])}</a></p>
</div></footer>
<dialog class="qr-dialog"><img src="qr.svg" alt="QR" width="300" height="300"><p>{e(u['qr_hint'])}</p><p class="small">{e(url)}</p><form method="dialog"><button class="btn primary">{e(u['close'])}</button></form></dialog>
<script src="{up}assets/app.js?v={ver("app.js")}" defer></script>
</body>
</html>
"""


def guide_txt(code, t):
    """Plain text twin: same content, one paragraph per line."""
    L = []
    a = L.append
    m, u = t["meta"], t["ui"]
    a(m["title"].upper()); a(url_of(code)); a(u["cta"]); a(u["checked"]); a("")
    a(t["hero"]["lede"]); a("")
    def head(h): a(""); a(h.upper())
    head(t["before"]["h"]); a(t["before"]["intro"])
    for g in t["before"]["groups"]:
        a(""); a(g["h"]); [a("[ ] " + x) for x in g["items"]]
    a(""); a(t["before"]["two"])
    head(t["helping"]["h"]); [a("- " + x) for x in t["helping"]["items"]]
    c = t["credentials"]; head(c["h"]); a(c["intro"])
    for r in c["rows"]:
        a(f'- {r["name"]}: {r["abroad"]} {c["cols"][2]}: {r["needs"]}')
    a(c["note"])
    i = t["idme"]; head(i["h"])
    for s in i["steps"]:
        a(s["h"]); a(s["body"])
    a(""); a(i["nossn_h"]); a(i["nossn"])
    w = t["wrong"]; head(w["h"])
    for it in w["items"]:
        a("? " + it["q"]); a("  " + it["a"])
    d = t["death"]; head(d["h"]); a(d["intro"])
    for x in d["items"]:
        a(x["h"]); a(x["body"])
    p = t["paper"]; head(p["h"]); a(p["intro"]); Lb = p["labels"]
    for r in DATA["routes"]:
        tr = p["routes"][r["id"]]; a(""); a(tr["h"])
        if r.get("form"): a(f'{Lb["form"]}: {r["form"]} {r["form_url"]}')
        if r.get("mail"): a(f'{Lb["mail"]}: {r["mail"]}')
        if r.get("fax"): a(f'{Lb["fax"]}: {r["fax"]}' + (f' ({Lb["check"]})' if r.get("fax_check") else ""))
        if r.get("phone"): a(f'{Lb["phone"]}: {r["phone"]}')
        if r.get("email"): a(f'{Lb["email"]}: {r["email"]}')
        if tr.get("note"): a(tr["note"])
    ph = t["phone"]; head(ph["h"]); a(ph["intro"])
    for ln in DATA["lines"]:
        hrs = f' ({ph["days"]}, {ln["open"]}-{ln["close"]} ET)' if ln.get("tz") else (f' ({ph["anytime"]})' if ln.get("always") else "")
        a(f'- {ph["lines"][ln["id"]]}: {ln["show"]}{hrs}')
    head(t["help"]["h"]); [a("- " + x) for x in t["help"]["items"]]
    s = t["scammers"]; head(s["h"]); a(s["intro"]); a(""); a(s["signs_h"]); [a("- " + x) for x in s["signs"]]
    a(""); a(s["do_h"]); [a(f"{n+1}. {x}") for n, x in enumerate(s["do"])]
    head(t["thailand"]["h"]); [a("- " + x) for x in t["thailand"]["items"]]
    head(t["care"]["h"]); a(t["care"]["intro"]); [a("- " + x) for x in t["care"]["items"]]
    head(t["share"]["h"]); [a(x) for x in t["share"]["lines"]]; a(url_of(code))
    head(u["sources"]); [a(f"- {x[0]}: {x[1]}") for x in DATA["sources"]]
    a(""); a(t["foot"]["made"]); a(t["foot"]["not_gov"])
    return "\n".join(L) + "\n"


def qr_svg(url, dest):
    import qrcode, qrcode.image.svg
    img = qrcode.make(url, image_factory=qrcode.image.svg.SvgPathFillImage, box_size=10, border=2)
    img.save(str(dest))


def main():
    langs = {}
    for c in ORDER:
        f = SRC / "i18n" / f"{c}.json"
        if f.exists():
            langs[c] = json.loads(f.read_text())
    for c, t in langs.items():
        d = OUT / path_of(c)
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(build_page(c, t, langs))
        (d / "guide.txt").write_text(guide_txt(c, t))
        qr_svg(url_of(c), d / "qr.svg")
    # sitemap with hreflang alternates
    alts = "".join(f'<xhtml:link rel="alternate" hreflang="{langs[c]["meta"]["lang"]}" href="{url_of(c)}"/>' for c in langs)
    urls = "".join(f"<url><loc>{url_of(c)}</loc><lastmod>{CHECKED}</lastmod>{alts}</url>" for c in langs)
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">{urls}</urlset>\n')
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}sitemap.xml\n")
    en = langs["en"]
    llms = [f"# {en['meta']['title']}", "", f"> {en['meta']['description']}", "",
            f"Checked against VA, ID.me, Login.gov and Social Security pages on {CHECKED}. Free. Made by Hongdam for Chiang Mai Visa Desk.", "",
            "## Languages", ""]
    llms += [f"- [{t['meta']['native']}]({url_of(c)}): plain text at {url_of(c)}guide.txt" for c, t in langs.items()]
    llms += ["", "## Sections", ""] + [f"- {h}" for h in ["Before you start (documents, phone, email)", "Which sign-in works from abroad (ID.me, Login.gov, CLEAR)",
             "ID.me from abroad, step by step", "When it goes wrong (19 problems and the way through)", "When a veteran has died",
             "No login: post, fax and phone (addresses)", "Phone lines from abroad", "Free help (accredited VSOs)", "Scammers: signs and what to do",
             "In Thailand", "If it is too much (crisis lines)"]]
    llms += ["", "## Full text", "", f"- [English guide.txt]({SITE}guide.txt)"]
    (OUT / "llms.txt").write_text("\n".join(llms) + "\n")
    (OUT / "llms-full.txt").write_text(guide_txt("en", en))
    (OUT / ".nojekyll").write_text("")
    print("built:", " ".join(langs))
    if "--cards" in sys.argv:
        import subprocess
        subprocess.run([sys.executable, str(ROOT / "tools" / "cards.py")] + list(langs), check=True)


if __name__ == "__main__":
    main()
