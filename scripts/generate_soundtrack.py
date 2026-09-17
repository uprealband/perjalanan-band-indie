import json
import re
from pathlib import Path
from urllib.parse import quote

from mutagen import File

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_ROOT = ROOT / "archive"
OUTPUT = ROOT / "audio" / "soundtrack" / "soundtrack.json"


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


def year_from(value):
    match = re.search(r"(19|20)\d{2}", value or "")
    return int(match.group(0)) if match else None


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")


def track_number(tags, path):
    raw = first(tags, "TRCK", "tracknumber")
    match = re.search(r"\d+", raw)
    if match:
        return int(match.group(0))

    match = re.search(r"(?:^|-)track[-_ ]?(\d+)(?:-|$)", path.stem, re.I)
    if match:
        return int(match.group(1))

    return None


def relative_audio(path):
    rel = path.relative_to(ROOT).as_posix()
    return "/".join(quote(part, safe="") for part in rel.split("/"))


def existing_entries():
    if not OUTPUT.exists():
        return {}
    try:
        data = json.loads(OUTPUT.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return {
        str(item.get("id")): item
        for item in data.get("soundtracks", [])
        if isinstance(item, dict) and item.get("id")
    }


def artwork_for(item_id, existing):
    preserved = clean(existing.get("cover"))
    if preserved:
        return preserved

    artwork_root = ROOT / "artwork"
    for ext in ("jpg", "jpeg", "webp", "png"):
        candidate = artwork_root / f"{item_id}.{ext}"
        if candidate.exists():
            return candidate.as_posix()
    return None


def discover():
    found = []
    if not ARCHIVE_ROOT.exists():
        return found

    for year_dir in sorted(ARCHIVE_ROOT.iterdir(), key=lambda p: p.name.lower()):
        if not year_dir.is_dir() or not re.fullmatch(r"(?:19|20)\d{2}", year_dir.name):
            continue

        audio_dir = year_dir / "audio"
        if not audio_dir.exists():
            continue

        for path in sorted(audio_dir.rglob("*.mp3"), key=lambda p: p.as_posix().lower()):
            try:
                audio = File(path, easy=False)
                if audio is None or not getattr(audio, "tags", None):
                    continue
                tags = audio.tags
                genre = first(tags, "TCON", "genre")
                if "soundtrack" not in genre.lower():
                    continue

                title = first(tags, "TIT2", "title") or path.stem
                artist = first(tags, "TPE1", "artist") or "Uprealband"
                year = year_from(first(tags, "TDRC", "TYER", "date", "year"))
                item_id = slug(title) or slug(path.stem)
                number = track_number(tags, path)

                found.append({
                    "id": item_id,
                    "type": "soundtrack",
                    "context": "moment",
                    "title": title,
                    "artist": artist,
                    "year": year,
                    "description": f"Soundtrack yang ditetapkan untuk momen {title} dalam dokumentasi perjalanan UprealBand.",
                    "audio": relative_audio(path),
                    "cover": None,
                    "relatedStory": None,
                    "featured": False,
                    "_track": number,
                    "_path": path.as_posix().lower(),
                })
            except Exception as exc:
                print(f"[SKIP] {path}: {exc}")

    return found


def sort_key(item):
    number = item.get("_track")
    return (0, number, item["_path"]) if number is not None else (1, item["title"].lower(), item["_path"])


def main():
    previous = existing_entries()
    entries = discover()
    entries.sort(key=sort_key)

    output = []
    for item in entries:
        old = previous.get(item["id"], {})
        item["description"] = clean(old.get("description")) or item["description"]
        item["cover"] = artwork_for(item["id"], old)
        item["relatedStory"] = old.get("relatedStory", None)
        item["featured"] = bool(old.get("featured", False))

        item.pop("_track", None)
        item.pop("_path", None)
        output.append(item)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps({"version": 1, "soundtracks": output}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"[OK] Generated soundtrack.json from Genre=Soundtrack | {len(output)} soundtrack(s)")
    for item in output:
        print(f"[OK] {item['title']} -> {item['audio']}")


if __name__ == "__main__":
    main()
