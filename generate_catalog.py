#!/usr/bin/env python3
import json
import re
from pathlib import Path
from mutagen import File
from mutagen.id3 import ID3

ROOT = Path(__file__).resolve().parent
AUDIO_ROOT = ROOT / "audio"
ARTWORK_ROOT = ROOT / "artwork"
OUTPUT = ROOT / "catalog.json"


def clean(value):
    if value is None:
        return ""
    if isinstance(value, list):
        return str(value[0]) if value else ""
    return str(value).strip()


def safe_id(text):
    text = clean(text).lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text[:180] or "audio"


def first_tag(tags, *names):
    if not tags:
        return ""
    for name in names:
        value = tags.get(name)
        if value:
            return clean(value)
    return ""


def extract_cover(path, track_id):
    for ext in (".jpg", ".jpeg", ".webp", ".png"):
        candidate = ARTWORK_ROOT / f"{track_id}{ext}"
        if candidate.exists():
            return f"https://raw.githubusercontent.com/uprealband/perjalanan-band-indie/main/artwork/{candidate.name}"
    try:
        tags = ID3(path)
        for apic in tags.getall("APIC"):
            mime = apic.mime or "image/jpeg"
            ext = ".png" if mime == "image/png" else ".jpg"
            target = ARTWORK_ROOT / f"{track_id}{ext}"
            ARTWORK_ROOT.mkdir(parents=True, exist_ok=True)
            target.write_bytes(apic.data)
            return f"https://raw.githubusercontent.com/uprealband/perjalanan-band-indie/main/artwork/{target.name}"
    except Exception:
        pass
    return ""


def main():
    tracks = []
    podcasts = []
    stories = []

    if AUDIO_ROOT.exists():
        for path in sorted(AUDIO_ROOT.rglob("*.mp3"), key=lambda p: str(p).lower()):
            rel = path.relative_to(AUDIO_ROOT)
            folder = rel.parts[0].lower() if rel.parts else ""
            # Encode every URL path segment so spaces, parentheses, @, etc. remain playable in browsers.
            from urllib.parse import quote
            audio_url = "https://raw.githubusercontent.com/uprealband/perjalanan-band-indie/main/" + "/".join(quote(part, safe="") for part in rel.parts)

            try:
                audio = File(path, easy=False)
                tags = audio.tags or {}
            except Exception:
                continue

            title = first_tag(tags, "TIT2", "title") or path.stem
            artist = first_tag(tags, "TPE1", "artist") or "Uprealband"
            album = first_tag(tags, "TALB", "album")
            genre = first_tag(tags, "TCON", "genre")
            year = first_tag(tags, "TDRC", "date", "year")
            duration = ""
            try:
                duration_seconds = float(audio.info.length)
                minutes = int(duration_seconds // 60)
                seconds = int(round(duration_seconds % 60))
                if seconds == 60:
                    minutes += 1
                    seconds = 0
                duration = f"{minutes}:{seconds:02d}"
            except Exception:
                pass

            is_cover = folder == "cover" or album.upper() == "COVER" or genre.lower() == "cover"
            track_id = safe_id(rel.with_suffix("").as_posix())
            cover = extract_cover(path, track_id)
            version = first_tag(tags, "TXXX:VERSION", "version")
            universe = "COVER" if is_cover else folder.upper()
            release_date = f"{year}-01-01" if year and re.fullmatch(r"\d{4}", year) else ""

            item = {
                "id": track_id,
                "type": "cover" if is_cover else ("podcast" if folder == "podcast" else "music"),
                "title": title,
                "artist": artist,
                "album": album,
                "year": year,
                "genre": genre,
                "version": version,
                "universe": universe,
                "cover": cover,
                "audio": audio_url,
                "duration": duration,
                "releaseDate": release_date,
                "featured": False,
            }

            if folder == "podcast":
                description = first_tag(tags, "TXXX:DESCRIPTION", "TXXX:SUMMARY", "COMM::eng", "COMM")
                item["description"] = description
                item.pop("universe", None)
                item["type"] = "podcast"
                podcasts.append(item)
            else:
                tracks.append(item)

    catalog = {"tracks": tracks, "stories": stories, "podcasts": podcasts}
    OUTPUT.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Generated {len(tracks)} tracks and {len(podcasts)} podcasts")


if __name__ == "__main__":
    main()
