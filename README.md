# Getting In

A free guide for US veterans, widows and widowers outside the US: signing in to VA.gov with ID.me, what goes wrong and the way through, claims on paper with no login, scammers, and who to call. Twelve languages, each translated by hand; browser translation is off.

Live: https://nanobotco.github.io/getting-in/

- `src/i18n/<lang>.json` — every word on the page, one file per language. `en.json` is the source.
- `src/data.json` — addresses, phone numbers, hours and sources (not translated).
- `tools/build.py` — writes `docs/`: a page per language, its `guide.txt`, a QR code, `sitemap.xml`, `llms.txt`, `robots.txt`. `--cards` redraws the share cards.
- `tools/cards.py` — placeholder share cards through headless Chrome.
- `docs/sw.js` — keeps opened pages readable offline.

Made by Hongdam for Chiang Mai Visa Desk. Facts checked against VA, ID.me, Login.gov and Social Security pages on 2026-10-20; the research and barrier list live in `~/Developer/claude code projects/idme-abroad/`.
