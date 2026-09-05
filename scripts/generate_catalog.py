import json, re
import base64
from pathlib import Path
from mutagen import File

ROOT = Path(__file__).resolve().parents[1]
AUDIO_ROOT = ROOT / 'audio'
OUTPUT = ROOT / 'catalog.json'
RAW_BASE = 'https://raw.githubusercontent.com/uprealband/perjalanan-band-indie/main/'
ARTWORK_ROOT = ROOT / 'artwork'


def clean(value):
    if value is None:
        return ''
    if isinstance(value, list):
        return str(value[0]) if value else ''
    return str(value).strip()

def first(tags, *keys):
    for key in keys:
        if key in tags:
            return clean(tags[key])
    return ''

def slug(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

def year_from(text):
    m = re.search(r'(19|20)\d{2}', text or '')
    return m.group(0) if m else ''

def version_from_filename(path, title):
    stem = path.stem
    stem = re.sub(r'^Uprealband-', '', stem, flags=re.I)
    title_slug = slug(title)
    stem_slug = slug(stem)
    if title_slug and stem_slug.startswith(title_slug + '-'):
        rest = stem_slug[len(title_slug)+1:]
        return rest.replace('-', ' ').title()
    # Fallback: preserve filename remainder as a readable version.
    return stem.replace('-', ' ').strip()

def release_date(tags):
    raw = first(tags, 'TDRC', 'TYER', 'date', 'year')
    y = year_from(raw)
    return f'{y}-01-01' if y else ''

def cover_for(track_id, audio):
    # Prefer an artwork file if one already exists, otherwise extract the
    # embedded ID3 APIC/Picture and save it as a lightweight web image.
    for ext in ('jpg', 'jpeg', 'webp', 'png'):
        p = ARTWORK_ROOT / f'{track_id}.{ext}'
        if p.exists():
            return RAW_BASE + p.relative_to(ROOT).as_posix()

    if audio is not None and getattr(audio, 'tags', None):
        for key in audio.tags.keys():
            if str(key).startswith('APIC:'):
                pic = audio.tags[key]
                mime = getattr(pic, 'mime', '') or ''
                data = getattr(pic, 'data', None)
                if not data:
                    continue
                ext = 'jpg' if mime == 'image/jpeg' else 'png' if mime == 'image/png' else 'webp' if mime == 'image/webp' else 'jpg'
                ARTWORK_ROOT.mkdir(parents=True, exist_ok=True)
                out = ARTWORK_ROOT / f'{track_id}.{ext}'
                out.write_bytes(data)
                return RAW_BASE + out.relative_to(ROOT).as_posix()
    return ''

def make_track(path):
    rel = path.relative_to(ROOT).as_posix()
    audio = File(path, easy=False)
    tags = audio.tags or {}
    title = first(tags, 'TIT2', 'title') or re.sub(r'^Uprealband-', '', path.stem, flags=re.I).replace('-', ' ')
    artist = first(tags, 'TPE1', 'artist') or 'Uprealband'
    album = first(tags, 'TALB', 'album')
    genre = first(tags, 'TCON', 'genre')
    year = year_from(first(tags, 'TDRC', 'TYER', 'date', 'year'))
    version = version_from_filename(path, title)
    universe = path.relative_to(AUDIO_ROOT).parts[0].upper() if len(path.relative_to(AUDIO_ROOT).parts) > 1 else ''
    track_id = slug(f'{title}-{version}') or slug(path.stem)
    duration = ''
    if getattr(audio, 'info', None) and getattr(audio.info, 'length', None):
        seconds = int(round(audio.info.length))
        duration = f'{seconds // 60}:{seconds % 60:02d}'
    return {
        'id': track_id,
        'title': title,
        'artist': artist,
        'album': album,
        'year': year,
        'genre': genre,
        'version': version,
        'universe': universe,
        'cover': cover_for(track_id, audio),
        'audio': RAW_BASE + rel,
        'duration': duration,
        'releaseDate': release_date(tags),
        'featured': False,
    }

def main():
    tracks = []
    if AUDIO_ROOT.exists():
        for path in sorted(AUDIO_ROOT.rglob('*')):
            if path.is_file() and path.suffix.lower() == '.mp3':
                try:
                    tracks.append(make_track(path))
                except Exception as exc:
                    print(f'[WARN] Skip {path}: {exc}')
    tracks.sort(key=lambda x: (x['releaseDate'] or '0000-00-00', x['title'].lower()), reverse=True)
    if tracks:
        tracks[0]['featured'] = True
    catalog = {'tracks': tracks, 'stories': [], 'podcasts': []}
    OUTPUT.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'[OK] Wrote {OUTPUT} with {len(tracks)} track(s)')

if __name__ == '__main__':
    main()
