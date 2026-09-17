from pathlib import Path
import html
import json
import re
import shutil

import markdown

ROOT = Path(__file__).resolve().parents[1]
TRACK_DIR = ROOT / "track"
OUT_DIR = ROOT / "book-site"
BASE_URL = "https://perjalanan.uprealband.com"


def title_from_md(text, fallback):
    headings = re.findall(r"^#\s+(.+?)\s*$", text, flags=re.M)
    for heading in headings:
        if not re.match(r"TRACK\s+\d+", heading.strip(), flags=re.I):
            return heading.strip()
    return fallback


def remove_leading_book_headings(text):
    lines = text.splitlines()
    removed = 0
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and removed < 2 and lines[0].lstrip().startswith("#"):
        lines.pop(0)
        removed += 1
        while lines and not lines[0].strip():
            lines.pop(0)
    return "\n".join(lines)


def strip_markdown_for_description(text):
    text = remove_leading_book_headings(text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"[*_>`#~-]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:180].rstrip() + ("…" if len(text) > 180 else "")


def page_slug(filename):
    stem = filename.removesuffix(".md")
    stem = re.sub(r"^track-\d+-", "", stem, flags=re.I)
    return stem.lower()


def relpath_for(num, slug):
    return f"bab/{num:02d}-{slug}/"


def render_page(item, prev_item, next_item):
    num, filename, title, slug, body_html = item
    canonical = f"{BASE_URL}/{relpath_for(num, slug)}"
    desc = strip_markdown_for_description(Path(TRACK_DIR / filename).read_text(encoding="utf-8"))

    nav_prev = (
        f'<a class="nav-link prev" href="/{relpath_for(prev_item[0], prev_item[3])}">'
        f'<span>←</span><small>PREVIOUS</small><strong>Bab {prev_item[0]:02d}</strong></a>'
        if prev_item else '<span class="nav-link disabled"><span>←</span><small>PREVIOUS</small></span>'
    )
    nav_next = (
        f'<a class="nav-link next" href="/{relpath_for(next_item[0], next_item[3])}">'
        f'<small>NEXT</small><strong>Bab {next_item[0]:02d}</strong><span>→</span></a>'
        if next_item else '<span class="nav-link disabled"><small>NEXT</small><strong>END</strong><span>→</span></span>'
    )

    return f'''<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Bab {num:02d}: {html.escape(title)} | Perjalanan UprealBand</title>
<meta name="description" content="{html.escape(desc, quote=True)}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta property="og:type" content="article">
<meta property="og:title" content="Bab {num:02d}: {html.escape(title)} | Perjalanan UprealBand">
<meta property="og:description" content="{html.escape(desc, quote=True)}">
<meta property="og:url" content="{canonical}">
<style>{CSS}</style>
<script type="application/ld+json">{json.dumps({
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": f"Bab {num:02d}: {title}",
    "url": canonical,
    "isPartOf": {"@type": "Book", "name": "Perjalanan UprealBand", "url": BASE_URL + "/"},
    "about": "UprealBand",
}, ensure_ascii=False)}</script>
</head>
<body>
<header class="top"><a href="/">PERJALANAN UPREALBAND</a><span>DOCUMENTATION · DEPOK · SINCE 2004</span></header>
<main>
<div class="book-meta"><span>BAB {num:02d} / 31</span><span>PERJALANAN UPREALBAND</span></div>
<article class="book-page">
<div class="chapter-label">TRACK {num:02d}</div>
<h1>{html.escape(title)}</h1>
<div class="rule"></div>
<div class="content">{body_html}</div>
</article>
<nav class="book-nav" aria-label="Navigasi bab">
{nav_prev}
<a class="toc" href="/"><span>☰</span><small>DAFTAR ISI</small></a>
{nav_next}
</nav>
</main>
<footer>Perjalanan UprealBand · Dokumentasi perjalanan band indie asal Depok sejak 2004.</footer>
</body>
</html>'''


def build():
    files = sorted(TRACK_DIR.glob("track-*.md"))
    if len(files) != 31:
        raise SystemExit(f"Expected 31 track files, found {len(files)}")

    items = []
    for idx, path in enumerate(files, start=1):
        text = path.read_text(encoding="utf-8")
        title = title_from_md(text, path.stem)
        slug = page_slug(path.name)
        source_body = remove_leading_book_headings(text)
        body = markdown.markdown(source_body, extensions=["extra", "sane_lists"])
        items.append((idx, path.name, title, slug, body))

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)

    for i, item in enumerate(items):
        prev_item = items[i - 1] if i > 0 else None
        next_item = items[i + 1] if i + 1 < len(items) else None
        target = OUT_DIR / relpath_for(item[0], item[3])
        target.mkdir(parents=True, exist_ok=True)
        (target / "index.html").write_text(
            render_page(item, prev_item, next_item), encoding="utf-8"
        )

    links = "\n".join(
        f'<li><a href="/{relpath_for(i, slug)}"><span>Bab {i:02d}</span><strong>{html.escape(title)}</strong></a></li>'
        for i, _, title, slug, _ in items
    )
    index_jsonld = json.dumps({
        "@context": "https://schema.org",
        "@type": "Book",
        "name": "Perjalanan UprealBand",
        "url": BASE_URL + "/",
        "about": "UprealBand, band indie asal Depok sejak 2004",
    }, ensure_ascii=False)
    index = f'''<!doctype html>
<html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Perjalanan UprealBand | 31 Bab Perjalanan Band Indie Depok Sejak 2004</title>
<meta name="description" content="Dokumentasi perjalanan UprealBand, band indie asal Depok sejak 2004, disusun dalam 31 bab.">
<link rel="canonical" href="{BASE_URL}/"><meta name="robots" content="index,follow">
<style>{CSS}</style><script type="application/ld+json">{index_jsonld}</script></head>
<body><header class="top"><a href="/">PERJALANAN UPREALBAND</a><span>DOCUMENTATION · DEPOK · SINCE 2004</span></header>
<main><section class="intro"><div class="chapter-label">BUKU PERJALANAN</div><h1>Perjalanan UprealBand</h1><p>Dokumentasi perjalanan band indie asal Depok sejak 2004, disusun dalam 31 bab.</p></section>
<section class="toc-wrap"><div class="book-meta"><span>DAFTAR ISI</span><span>31 BAB</span></div><ol class="toc-list">{links}</ol></section></main>
<footer>Perjalanan UprealBand · Dokumentasi perjalanan band indie asal Depok sejak 2004.</footer></body></html>'''
    (OUT_DIR / "index.html").write_text(index, encoding="utf-8")
    (OUT_DIR / "CNAME").write_text("perjalanan.uprealband.com\n", encoding="utf-8")

    urls = [BASE_URL + "/"] + [BASE_URL + "/" + relpath_for(i, slug) for i, _, _, slug, _ in items]
    sitemap = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n" + "".join(f"  <url><loc>{html.escape(u)}</loc></url>\n" for u in urls) + "</urlset>\n"
    (OUT_DIR / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (OUT_DIR / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: " + BASE_URL + "/sitemap.xml\n", encoding="utf-8")


CSS = r'''
@font-face{font-family:Space;src:url("https://raw.githubusercontent.com/uprealband/perjalanan-band-indie/main/SpaceGrotesk%5Bwght%5D.woff2") format("woff2");font-weight:100 900;font-display:swap}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#f5f2ec;color:#171717;font-family:Space,Arial,sans-serif}.top{height:64px;padding:0 5vw;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #171717;background:#fff}.top a{font-weight:800;letter-spacing:.08em;text-decoration:none;color:#171717}.top span{font-size:11px;letter-spacing:.1em}.book-meta{display:flex;justify-content:space-between;gap:20px;font-size:11px;letter-spacing:.12em;font-weight:700;padding:28px 0 14px;border-bottom:1px solid #bbb}main{max-width:920px;margin:auto;padding:0 24px}.book-page{background:#fff;min-height:72vh;margin:28px 0 20px;padding:clamp(28px,6vw,70px);box-shadow:0 8px 30px rgba(0,0,0,.07)}.chapter-label{font-size:12px;letter-spacing:.16em;font-weight:800}.book-page h1,.intro h1{font-size:clamp(34px,6vw,64px);line-height:1.02;margin:18px 0 24px;letter-spacing:-.045em}.rule{width:64px;height:5px;background:#f47b20;margin-bottom:40px}.content{font-family:Georgia,serif;font-size:18px;line-height:1.82}.content h1{font-family:Space,Arial,sans-serif;font-size:30px;margin-top:42px}.content h2{font-family:Space,Arial,sans-serif;font-size:25px;margin-top:42px}.content h3{font-family:Space,Arial,sans-serif}.content p{margin:0 0 1.15em}.content blockquote{margin:28px 0;padding:8px 24px;border-left:4px solid #f47b20;color:#444}.content img{max-width:100%;height:auto}.content a{color:#d95f00}.book-nav{display:grid;grid-template-columns:1fr auto 1fr;gap:12px;align-items:stretch;margin:0 0 70px}.nav-link,.toc{background:#171717;color:#fff;text-decoration:none;padding:15px 18px;display:flex;align-items:center;gap:10px}.nav-link{justify-content:space-between}.nav-link small,.toc small{font-size:10px;letter-spacing:.12em}.nav-link strong{font-size:13px}.toc{background:#f47b20;color:#171717;flex-direction:column;justify-content:center;min-width:110px}.disabled{opacity:.25}.intro{padding:70px 0 45px}.intro p{font-size:20px;max-width:650px;line-height:1.6}.toc-wrap{padding-bottom:70px}.toc-list{list-style:none;padding:0;margin:0}.toc-list li{border-bottom:1px solid #bbb}.toc-list a{display:grid;grid-template-columns:80px 1fr;gap:15px;padding:18px 0;text-decoration:none;color:#171717}.toc-list span{font-size:12px;letter-spacing:.1em;font-weight:700}.toc-list strong{font-size:17px}footer{text-align:center;padding:28px 20px;border-top:1px solid #171717;background:#fff;font-size:11px;letter-spacing:.05em}@media(max-width:650px){.top{height:auto;min-height:60px;padding:15px 20px;display:block}.top span{display:block;margin-top:5px;font-size:9px}.book-meta{font-size:9px}.book-page{padding:28px 22px;margin-top:18px}.content{font-size:17px;line-height:1.75}.book-nav{grid-template-columns:1fr 1fr}.toc{grid-column:1/-1;grid-row:1;min-height:45px}.nav-link{grid-row:2}.intro{padding:50px 0 30px}.toc-list a{grid-template-columns:62px 1fr}.toc-list strong{font-size:15px}}
'''

if __name__ == "__main__":
    build()
