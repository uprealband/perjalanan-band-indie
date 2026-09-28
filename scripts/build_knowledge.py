from pathlib import Path
import html
import re

ROOT = Path(__file__).resolve().parents[1]
TRACK_DIR = ROOT / "track"
OUT_DIR = ROOT / "book-site"
BASE_URL = "https://bab.perjalanan.uprealband.com"


def relpath(num, slug):
    return f"{num:02d}-{slug}/"


def slug_for(path):
    return re.sub(r"^track-\d+-", "", path.stem, flags=re.I).lower()


def extract_list(text, names):
    lines = text.splitlines()
    wanted = {n.lower() for n in names}
    values = []
    active = False
    for line in lines:
        m = re.match(r"^#{2,4}\s+(.+?)\s*$", line)
        if m:
            active = m.group(1).strip().lower() in wanted
            continue
        if active:
            m = re.match(r"^\s*[-*+]\s+(.+?)\s*$", line)
            if m:
                values.append(re.sub(r"\s+", " ", m.group(1)).strip())
    return values


def first_paragraph(text):
    lines = text.splitlines()
    started = False
    out = []
    for line in lines:
        s = line.strip()
        if not s:
            if started:
                break
            continue
        if re.match(r"^#{1,4}\s+", s):
            if started:
                break
            continue
        if s.startswith(("- ", "* ", "+ ")):
            if started:
                break
            continue
        started = True
        out.append(s)
    value = " ".join(out)
    value = re.sub(r"\[[^\]]+\]\([^)]*\)", "", value)
    value = re.sub(r"[*_>#~-]", "", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value[:360].rstrip() + ("…" if len(value) > 360 else "")


def facts(text):
    return {
        "tahun": extract_list(text, ["Tahun"]),
        "lokasi": extract_list(text, ["Tempat", "Lokasi"]),
        "tokoh": extract_list(text, ["Tokoh", "Personel"]),
        "topik": extract_list(text, ["Topik"]),
        "ringkasan": first_paragraph(text),
    }


def factbox(data):
    rows = []
    for key, label in [
        ("tahun", "Periode"),
        ("lokasi", "Lokasi"),
        ("tokoh", "Tokoh"),
        ("topik", "Topik"),
    ]:
        if data[key]:
            rows.append(
                f'<div class="fact-row"><dt>{label}</dt><dd>{html.escape(", ".join(data[key]))}</dd></div>'
            )
    summary = ""
    if data["ringkasan"]:
        summary = (
            '<div class="fact-summary"><strong>Ringkasan naratif</strong>'
            f'<p>{html.escape(data["ringkasan"])}</p></div>'
        )
    return '<section class="factbox" aria-label="Ringkasan fakta">' + summary + f'<dl>{"".join(rows)}</dl></section>'


def human_title(path):
    stem = re.sub(r"^track-\d+-", "", path.stem, flags=re.I)
    return re.sub(r"[-_]+", " ", stem).strip().title()


def replace_internal_links(text):
    pattern = r'href="(?:https://raw\.githubusercontent\.com/uprealband/perjalanan-band-indie/main/)?track/track-(\d+)-([^"]+)\.md(?:#([^"]+))?"'

    def repl(m):
        num = int(m.group(1))
        slug = m.group(2).lower()
        anchor = f"#{m.group(3)}" if m.group(3) else ""
        return f'href="/{relpath(num, slug)}{anchor}"'

    return re.sub(pattern, repl, text, flags=re.I)


def add_css(html_text):
    css = """
.factbox{font-family:Arial,sans-serif;background:#f7f4ee;border-left:5px solid #f47b20;padding:20px 22px;margin:0 0 38px}
.fact-summary strong{font-size:12px;letter-spacing:.1em;text-transform:uppercase}
.fact-summary p{font-family:Georgia,serif;font-size:16px;line-height:1.6;margin:8px 0 18px}
.factbox dl{margin:0}.fact-row{display:grid;grid-template-columns:100px 1fr;gap:12px;border-top:1px solid #ccc;padding:9px 0}
.fact-row dt{font-size:11px;font-weight:800;letter-spacing:.08em;text-transform:uppercase}.fact-row dd{margin:0;font-size:13px;line-height:1.55}
.knowledge-nav{font-family:Arial,sans-serif;font-size:12px;display:flex;flex-wrap:wrap;gap:10px;margin:0 0 24px}
.knowledge-nav a{color:#d95f00;text-decoration:none}
.timeline{width:100%;border-collapse:collapse;font-family:Arial,sans-serif;font-size:14px}.timeline th,.timeline td{border-bottom:1px solid #bbb;text-align:left;vertical-align:top;padding:12px 8px}.timeline th{font-size:10px;letter-spacing:.1em;text-transform:uppercase}
"""
    return html_text.replace("</style>", css + "</style>", 1)


def wrap_page(title, description, body):
    canonical = f"{BASE_URL}/{title.lower().replace(' ', '-')}/"
    return f'''<!doctype html>
<html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} | Perjalanan UprealBand</title>
<meta name="description" content="{html.escape(description, quote=True)}">
<link rel="canonical" href="{canonical}"><meta name="robots" content="index,follow,max-image-preview:large">
<style>body{{margin:0;background:#f5f2ec;color:#171717;font-family:Arial,sans-serif}}header{{padding:20px 5vw;background:#fff;border-bottom:1px solid #171717}}header a{{color:#171717;text-decoration:none;font-weight:800}}main{{max-width:1000px;margin:auto;padding:30px 24px 70px}}h1{{font-size:clamp(34px,6vw,64px);line-height:1.05}}h2{{margin-top:42px}}table{{background:#fff}}footer{{padding:25px;text-align:center;background:#fff;border-top:1px solid #171717;font-size:12px}}a{{color:#d95f00}}</style></head>
<body><header><a href="/">PERJALANAN UPREALBAND</a></header><main><div class="knowledge-nav"><a href="/tentang-uprealband/">Profil</a><a href="/kronologi/">Kronologi</a><a href="/personel/">Personel</a><a href="/artefak/">Artefak</a><a href="/sumber-arsip/">Sumber Arsip</a><a href="/corpus/">Corpus</a></div>
<h1>{html.escape(title)}</h1><p>{html.escape(description)}</p>{body}</main><footer>Perjalanan UprealBand · Dokumentasi perjalanan band indie asal Depok sejak 2004.</footer></body></html>'''


def main():
    paths = sorted(TRACK_DIR.glob("track-*.md"))
    if len(paths) != 31:
        raise SystemExit(f"Expected 31 track files, found {len(paths)}")

    records = []
    for num, path in enumerate(paths, 1):
        text = path.read_text(encoding="utf-8")
        records.append((num, path, human_title(path), slug_for(path), facts(text)))

    for num, path, title, slug, data in records:
        target = OUT_DIR / relpath(num, slug) / "index.html"
        if not target.exists():
            continue
        page = target.read_text(encoding="utf-8")
        page = replace_internal_links(page)
        if 'class="factbox"' not in page:
            page = page.replace('<div class="content">', factbox(data) + '<div class="content">', 1)
        page = add_css(page)
        target.write_text(page, encoding="utf-8")

    chapter_links = "".join(
        f'<li><a href="/{relpath(n, slug)}">Bab {n:02d}: {html.escape(title)}</a></li>'
        for n, _, title, slug, _ in records
    )
    profile_body = f'''
<h2>UprealBand</h2>
<p><strong>UprealBand adalah band indie asal Depok, Indonesia, yang memulai perjalanan sejak 2004.</strong></p>
<p>Halaman ini menjadi pintu masuk ke arsip perjalanan. Detail sejarah tetap berada pada 31 bab sumber dan tidak digantikan oleh ringkasan otomatis.</p>
<h2>Peta arsip</h2>
<ul><li><a href="/kronologi/">Kronologi</a></li><li><a href="/personel/">Tokoh & Personel</a></li><li><a href="/artefak/">Artefak & Topik</a></li><li><a href="/sumber-arsip/">Sumber Arsip</a></li><li><a href="/corpus/">Corpus Teks Lengkap</a></li></ul>
<h2>31 Bab Perjalanan</h2><ol>{chapter_links}</ol>
<h2>Situs resmi</h2><p><a href="https://www.uprealband.com/">uprealband.com</a></p>
'''
    (OUT_DIR / "tentang-uprealband").mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "tentang-uprealband/index.html").write_text(
        wrap_page("Tentang UprealBand", "Profil resmi dan pintu masuk arsip Perjalanan UprealBand.", profile_body),
        encoding="utf-8",
    )

    rows = []
    for n, _, title, slug, data in records:
        years = ", ".join(data["tahun"]) or "Tidak dicatat"
        places = ", ".join(data["lokasi"]) or "Tidak dicatat"
        rows.append(f'<tr><td>Bab {n:02d}</td><td>{html.escape(years)}</td><td><a href="/{relpath(n, slug)}">{html.escape(title)}</a></td><td>{html.escape(places)}</td></tr>')
    chronology_body = '<h2>Kronologi berdasarkan metadata bab</h2><p>Tahun dan lokasi di bawah hanya diambil dari metadata sumber. Tidak ada peristiwa baru yang ditambahkan oleh generator.</p><table class="timeline"><thead><tr><th>Bab</th><th>Tahun</th><th>Bab / Peristiwa</th><th>Lokasi</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table>"
    (OUT_DIR / "kronologi").mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "kronologi/index.html").write_text(
        wrap_page("Kronologi", "Kronologi Perjalanan UprealBand berdasarkan 31 bab arsip.", chronology_body),
        encoding="utf-8",
    )

    people = {}
    for n, _, title, slug, data in records:
        for person in data["tokoh"]:
            people.setdefault(person, []).append((n, slug))
    rows = []
    for person in sorted(people, key=str.lower):
        sources = " · ".join(f'<a href="/{relpath(n, s)}">Bab {n:02d}</a>' for n, s in people[person])
        rows.append(f"<tr><td>{html.escape(person)}</td><td>{sources}</td></tr>")
    people_body = '<h2>Tokoh yang tercatat</h2><p>Peran atau periode keterlibatan tidak ditambahkan jika sumber bab tidak mencatatnya.</p><table class="timeline"><thead><tr><th>Nama</th><th>Sumber</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table>"
    (OUT_DIR / "personel").mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "personel/index.html").write_text(
        wrap_page("Personel", "Indeks tokoh dan personel yang tercatat dalam arsip.", people_body),
        encoding="utf-8",
    )

    rows = []
    for n, _, title, slug, data in records:
        topics = ", ".join(data["topik"]) or "Tidak dicatat"
        rows.append(f'<tr><td>Bab {n:02d}</td><td><a href="/{relpath(n, slug)}">{html.escape(title)}</a></td><td>{html.escape(topics)}</td></tr>')
    artifacts_body = '<h2>Topik dan artefak yang tercatat</h2><p>Indeks ini memakai metadata Topik dari sumber. Artefak spesifik tetap dibaca dari narasi bab.</p><table class="timeline"><thead><tr><th>Bab</th><th>Bab</th><th>Topik</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table>"
    (OUT_DIR / "artefak").mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "artefak/index.html").write_text(
        wrap_page("Artefak", "Indeks artefak dan topik dokumentasi Perjalanan UprealBand.", artifacts_body),
        encoding="utf-8",
    )

    sources_body = '''
<h2>Sumber utama</h2>
<p>Folder <code>track/</code> pada repository menjadi sumber Markdown utama. Website dibangun otomatis dari sumber tersebut.</p>
<p>Ringkasan fakta pada setiap bab diekstrak dari bagian metadata yang memang tercatat dan dari paragraf pembuka. Generator tidak menambahkan fakta sejarah baru.</p>
<ul><li><a href="https://github.com/uprealband/perjalanan-band-indie">Repository Perjalanan UprealBand</a></li><li><a href="/">Daftar 31 bab</a></li><li><a href="/corpus/">Corpus teks lengkap</a></li></ul>
'''
    (OUT_DIR / "sumber-arsip").mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "sumber-arsip/index.html").write_text(
        wrap_page("Sumber Arsip", "Metodologi dan sumber utama arsip Perjalanan UprealBand.", sources_body),
        encoding="utf-8",
    )

    sitemap = OUT_DIR / "sitemap.xml"
    if sitemap.exists():
        xml = sitemap.read_text(encoding="utf-8")
        extra = "".join(
            f"<url><loc>{BASE_URL}/{x}/</loc></url>"
            for x in ["tentang-uprealband", "kronologi", "personel", "artefak", "sumber-arsip"]
        )
        sitemap.write_text(xml.replace("</urlset>", extra + "</urlset>"), encoding="utf-8")


if __name__ == "__main__":
    main()
