#!/usr/bin/env python3
"""Placeholder share cards, 1200x630, one per language: name, line, call to action, address.
Drawn as HTML and photographed by headless Chrome, so Thai, Lao, Khmer and CJK shape properly.
Marcus makes the designed ones (ticket); his files replace docs/<lang>/card.png.

  python3 tools/cards.py en th ...
"""
import html, json, os, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
FONT = {"th": "'Thonburi', 'Sukhumvit Set'", "lo": "'Lao Sangam MN', 'Lao MN'", "km": "'Khmer Sangam MN', 'Khmer MN'",
        "ko": "'Apple SD Gothic Neo'", "ja": "'Hiragino Sans', 'Hiragino Kaku Gothic ProN'", "zh": "'PingFang SC', 'Hiragino Sans GB'"}
KEY = ('<svg viewBox="0 0 512 512" width="150" height="150"><circle cx="256" cy="190" r="88" fill="none" stroke="#C79A3A" stroke-width="40"/>'
       '<rect x="236" y="266" width="40" height="190" rx="12" fill="#C79A3A"/><rect x="276" y="350" width="64" height="32" rx="8" fill="#C79A3A"/>'
       '<rect x="276" y="404" width="44" height="30" rx="8" fill="#C79A3A"/></svg>')


def page(code):
    t = json.loads((ROOT / "src/i18n" / f"{code}.json").read_text())
    m, e = t["meta"], html.escape
    head = FONT.get(code, "Georgia, 'Times New Roman', serif")
    body = FONT.get(code, "'Helvetica Neue', Helvetica, Arial, sans-serif")
    path = "nanobotco.github.io/getting-in/" + ("" if code == "en" else code + "/")
    return f"""<!doctype html><html lang="{m['lang']}"><meta charset="utf-8"><style>
*{{margin:0;box-sizing:border-box}} html,body{{width:1200px;height:630px;overflow:hidden}}
body{{background:#24406E;color:#F7F4EC;position:relative}}
.bar{{position:absolute;left:72px;top:96px;width:12px;height:380px;background:#C79A3A}}
.txt{{position:absolute;left:120px;top:86px;width:860px}}
h1{{font-family:{head};font-size:104px;line-height:1.15;font-weight:700;word-break:keep-all;overflow-wrap:normal}}
.line{{font-family:{body};font-size:42px;color:#F4E7CE;margin-top:26px;line-height:1.35}}
.cta{{font-family:{body};font-size:36px;color:#E2B860;margin-top:26px;font-weight:600;line-height:1.35}}
.key{{position:absolute;right:70px;top:90px}}
.foot{{position:absolute;left:0;right:0;bottom:0;height:70px;background:#1B3157;font:30px 'Helvetica Neue',Arial,sans-serif;padding:18px 72px}}
</style><body><div class="bar"></div><div class="key">{KEY}</div>
<div class="txt"><h1 id="h">{e(m['card_title'])}</h1><div class="line">{e(m['card_line'])}</div><div class="cta">{e(t['ui']['cta'])}</div></div>
<div class="foot">{path}</div>
<script>var h=document.getElementById('h'),x=document.querySelector('.txt'),s=104;while((h.scrollWidth>860||x.offsetHeight>440)&&s>40){{s-=4;h.style.fontSize=s+'px';}}</script>
</body></html>"""


def card(code, tmp):
    src = pathlib.Path(tmp) / f"{code}.html"
    src.write_text(page(code))
    out = ROOT / "docs" / ("" if code == "en" else code) / "card.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                    "--window-size=1200,630", f"--screenshot={out}", src.as_uri()],
                   check=True, capture_output=True, timeout=60)


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        for c in sys.argv[1:]:
            card(c, tmp)
    print("cards:", " ".join(sys.argv[1:]))
