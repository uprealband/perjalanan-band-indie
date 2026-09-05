import json
import re
from pathlib import Path
from html import escape
from mutagen import File

ROOT = Path(__file__).resolve().parents[1]
AUDIO_ROOT = ROOT / "audio"
TRACK_ROOT = ROOT / "track"
OUTPUT = ROOT / "catalog.json"
RAW_BASE = "https://raw.githubusercontent.com/uprealband/perjalanan-band-indie/main/"
ARTWORK_ROOT = ROOT / "artwork"


def clean(value):
    if value is None:
        return ""
    if isinstance(value, list):
        return str(value[0]) if value else ""
    return str(value).strip()


def first(tags, *keys):
    for key in keys:
        if key in tags:
            return clean(tags[key])
    return ""


def txxx(tags, name):
    wanted = name.strip().lower()
    for key, value in tags.items():
        if str(key).upper().startswith("TXXX:"):
            desc = clean(getattr(value, "desc", ""))
            if desc.lower() == wanted:
                return clean(getattr(value, "text", value))
    return ""


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")


def year_from(text):
    m = re.search(r"(19|20)\d{2}", text or "")
    return m.group(0) if m else ""


def version_from_filename(path, title):
    stem = path.stem
    stem = re.sub(r"^Uprealband-", "", stem, flags=re.I)
    title_slug = slug(title)
    stem_slug = slug(stem)
    if title_slug and stem_slug.startswith(title_slug + "-"):
        rest = stem_slug[len(title_slug) + 1:]
        return rest.replace("-", " ").title()
    return stem.replace("-", " ").strip()


def release_date(tags):
    raw = first(tags, "TDRC", "TDOR", "TYER", "date", "year")
    if re.match(r"^\d{4}-\d{2}-\d{2}", raw):
        return raw[:10]
    if re.match(r"^\d{4}-\d{2}", raw):
        return raw[:7] + "-01"
    y = year_from(raw)
    return f"{y}-01-01" if y else ""


def duration_of(audio):
    if getattr(audio, "info", None) and getattr(audio.info, "length", None):
        seconds = int(round(audio.info.length))
        return f"{seconds // 60}:{seconds % 60:02d}"
    return ""


def cover_for(item_id, audio=None, explicit_cover=""):
    if explicit_cover:
        if re.match(r"^https?://", explicit_cover):
            return explicit_cover
        p = ROOT / explicit_cover.lstrip("/")
        if p.exists():
            return RAW_BASE + p.relative_to(ROOT).as_posix()

    for ext in ("jpg", "jpeg", "webp", "png"):
        p = ARTWORK_ROOT / f"{item_id}.{ext}"
        if p.exists():
            return RAW_BASE + p.relative_to(ROOT).as_posix()

    if audio is not None and getattr(audio, "tags", None):
        for key in audio.tags.keys():
            if str(key).upper().startswith("APIC:"):
                pic = audio.tags[key]
                mime = getattr(pic, "mime", "") or ""
                data = getattr(pic, "data", None)
                if not data:
                    continue
                ext = (
                    "jpg" if mime == "image/jpeg" else
                    "png" if mime == "image/png" else
                    "webp" if mime == "image/webp" else
                    "jpg"
                )
                ARTWORK_ROOT.mkdir(parents=True, exist_ok=True)
                out = ARTWORK_ROOT / f"{item_id}.{ext}"
                out.write_bytes(data)
                return RAW_BASE + out.relative_to(ROOT).as_posix()
    return ""


def path_type(path):
    rel_parts = path.relative_to(AUDIO_ROOT).parts
    if rel_parts and rel_parts[0].lower() == "podcast":
        return "podcast"
    return "music"


def read_common(path):
    audio = File(path, easy=False)
    tags = audio.tags or {}
    title = first(tags, "TIT2", "title") or re.sub(
        r"^Uprealband-", "", path.stem, flags=re.I
    ).replace("-", " ")
    artist = first(tags, "TPE1", "artist") or "Uprealband"
    album = first(tags, "TALB", "album")
    genre = first(tags, "TCON", "genre")
    year = year_from(first(tags, "TDRC", "TYER", "date", "year"))
    return audio, tags, title, artist, album, genre, year


def make_track(path):
    rel = path.relative_to(ROOT).as_posix()
    audio, tags, title, artist, album, genre, year = read_common(path)
    version = version_from_filename(path, title)
    rel_audio = path.relative_to(AUDIO_ROOT)
    universe = rel_audio.parts[0].upper() if len(rel_audio.parts) > 1 else ""
    track_id = slug(f"{title}-{version}") or slug(path.stem)
    return {
        "id": track_id,
        "type": "music",
        "title": title,
        "artist": artist,
        "album": album,
        "year": year,
        "genre": genre,
        "version": version,
        "universe": universe,
        "cover": cover_for(track_id, audio),
        "audio": RAW_BASE + rel,
        "duration": duration_of(audio),
        "releaseDate": release_date(tags),
        "featured": False,
    }


def make_podcast(path):
    rel = path.relative_to(ROOT).as_posix()
    audio, tags, title, artist, album, genre, year = read_common(path)

    comment = ""
    for key, value in tags.items():
        if str(key).upper().startswith("COMM:"):
            comment = clean(getattr(value, "text", value))
            if comment:
                break

    description = (
        txxx(tags, "DESCRIPTION") or
        txxx(tags, "SUMMARY") or
        comment or
        ""
    )
    podcast_id = slug(f"podcast-{title}") or slug(path.stem)

    # No S01 / EP01 generation. Podcast identity comes from its metadata.
    return {
        "id": podcast_id,
        "type": "podcast",
        "title": title,
        "description": description,
        "artist": artist,
        "album": album,
        "year": year,
        "genre": genre,
        "cover": cover_for(podcast_id, audio),
        "audio": RAW_BASE + rel,
        "duration": duration_of(audio),
        "releaseDate": release_date(tags),
    }


FRONT_RE = re.compile(r"^\s*---\s*\n(.*?)\n---\s*\n?", re.S)


def parse_front_matter(text):
    match = FRONT_RE.match(text)
    if not match:
        return {}, text

    data = {}
    for line in match.group(1).splitlines():
        m = re.match(r"^\s*([A-Za-z][A-Za-z0-9_-]*)\s*:\s*(.*?)\s*$", line)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        value = value.strip("\"'")
        data[key] = value
    return data, text[match.end():]


def markdown_to_html(text):
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out = []
    paragraph = []

    def flush():
        if paragraph:
            joined = " ".join(x.strip() for x in paragraph).strip()
            if joined:
                # Minimal inline markdown, safely escaped first.
                s = escape(joined)
                s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
                s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
                out.append(f"<p>{s}</p>")
            paragraph.clear()

    for line in lines:
        stripped = line.strip()

        if not stripped:
            flush()
            continue

        m = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if m:
            flush()
            level = len(m.group(1))
            out.append(f"<h{level}>{escape(m.group(2).strip())}</h{level}>")
            continue

        if re.match(r"^[-*]\s+", stripped):
            flush()
            item = re.sub(r"^[-*]\s+", "", stripped)
            if not out or not out[-1].startswith("<ul>"):
                out.append("<ul>")
            out.append(f"<li>{escape(item)}</li>")
            continue

        if stripped.startswith("```"):
            flush()
            # Keep code blocks simple and safe.
            if stripped == "```":
                out.append("<pre><code>")
            else:
                out.append("</code></pre>")
            continue

        paragraph.append(stripped)

    flush()

    # Close a trailing list.
    if out and out[-1].startswith("<li>"):
        out.append("</ul>")

    return "\n".join(out)


def make_story(path):
    raw = path.read_text(encoding="utf-8-sig")
    meta, body = parse_front_matter(raw)

    # Remove a leading title heading from the body if it is used as the title.
    heading = re.search(r"^\s*#\s+(.+?)\s*$", body, re.M)

    title = (
        clean(meta.get("title")) or
        (heading.group(1).strip() if heading else "") or
        re.sub(r"^track-\d+-", "", path.stem, flags=re.I).replace("-", " ").strip()
    )

    chapter_raw = (
        clean(meta.get("chapter")) or
        (re.search(r"track-(\d+)", path.stem, re.I).group(1)
         if re.search(r"track-(\d+)", path.stem, re.I) else "")
    )
    chapter_num = int(chapter_raw) if chapter_raw.isdigit() else None

    date_value = clean(meta.get("date"))
    year_value = year_from(clean(meta.get("year")) or date_value)
    if not year_value:
        year_value = year_from(path.stem)

    excerpt = clean(meta.get("excerpt"))
    if not excerpt:
        plain = re.sub(r"^#+\s+", "", body, flags=re.M)
        plain = re.sub(r"[*_`>]", "", plain)
        plain = re.sub(r"\s+", " ", plain).strip()
        excerpt = plain[:220] + ("…" if len(plain) > 220 else "")

    story_id = slug(f"story-{chapter_num or ''}-{title}") or slug(path.stem)

    # Optional TTS audio can be supplied in front matter.
    tts_audio = clean(meta.get("ttsAudio"))
    if tts_audio and not re.match(r"^https?://", tts_audio):
        p = ROOT / tts_audio.lstrip("/")
        if p.exists():
            tts_audio = RAW_BASE + p.relative_to(ROOT).as_posix()

    cover = cover_for(story_id, None, clean(meta.get("cover")))

    # Preserve the full Markdown-derived content for the Blogger Stories renderer.
    content_html = markdown_to_html(body)

    story = {
        "id": story_id,
        "type": "story",
        "title": title,
        "chapter": chapter_num if chapter_num is not None else "",
        "year": year_value,
        "date": date_value,
        "excerpt": excerpt,
        "content": content_html,
        "source": path.relative_to(ROOT).as_posix(),
    }

    if cover:
        story["cover"] = cover
    if tts_audio:
        story["ttsAudio"] = tts_audio
    if clean(meta.get("ttsVoice")):
        story["ttsVoice"] = clean(meta.get("ttsVoice"))
    if clean(meta.get("soundtrackId")):
        story["soundtrackId"] = clean(meta.get("soundtrackId"))
    if clean(meta.get("duration")):
        story["duration"] = clean(meta.get("duration"))

    return story


def load_stories():
    stories = []
    if not TRACK_ROOT.exists():
        print(f"[WARN] Track directory not found: {TRACK_ROOT}")
        return stories

    for path in sorted(TRACK_ROOT.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in (".md", ".markdown", ".txt"):
            continue
        if path.name.lower() in ("readme.md", "readme.markdown", "readme.txt"):
            continue

        try:
            stories.append(make_story(path))
        except Exception as exc:
            print(f"[WARN] Skip story {path}: {exc}")

    stories.sort(
        key=lambda x: (
            x["chapter"] if isinstance(x.get("chapter"), int) else 999999,
            x["title"].lower(),
        )
    )
    return stories


def main():
    tracks = []
    podcasts = []
    stories = load_stories()

    if AUDIO_ROOT.exists():
        for path in sorted(AUDIO_ROOT.rglob("*")):
            if not path.is_file() or path.suffix.lower() != ".mp3":
                continue
            try:
                if path_type(path) == "podcast":
                    podcasts.append(make_podcast(path))
                else:
                    tracks.append(make_track(path))
            except Exception as exc:
                print(f"[WARN] Skip {path}: {exc}")

    tracks.sort(
        key=lambda x: (x["releaseDate"] or "0000-00-00", x["title"].lower()),
        reverse=True,
    )
    podcasts.sort(
        key=lambda x: (x["releaseDate"] or "0000-00-00", x["title"].lower())
    )

    if tracks:
        tracks[0]["featured"] = True

    catalog = {
        "tracks": tracks,
        "stories": stories,
        "podcasts": podcasts,
    }

    OUTPUT.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(
        f"[OK] Wrote {OUTPUT} | "
        f"{len(tracks)} music track(s), "
        f"{len(stories)} story track(s), "
        f"{len(podcasts)} podcast episode(s)"
    )


if __name__ == "__main__":
    main()
