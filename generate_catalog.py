import json
import re
import html
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


def txxx(tags, name):
    """Read an ID3 TXXX custom text frame by description, case-insensitively."""
    wanted = name.strip().lower()
    for key, value in tags.items():
        if str(key).upper().startswith('TXXX:'):
            desc = clean(getattr(value, 'desc', ''))
            if desc.lower() == wanted:
                return clean(getattr(value, 'text', value))
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
        rest = stem_slug[len(title_slug) + 1:]
        return rest.replace('-', ' ').title()
    return stem.replace('-', ' ').strip()


def release_date(tags):
    # Prefer a full date if present, otherwise fall back to the tagged year.
    raw = first(tags, 'TDRC', 'TDOR', 'TYER', 'date', 'year')
    if re.match(r'^\d{4}-\d{2}-\d{2}', raw):
        return raw[:10]
    if re.match(r'^\d{4}-\d{2}', raw):
        return raw[:7] + '-01'
    y = year_from(raw)
    return f'{y}-01-01' if y else ''


def duration_of(audio):
    if getattr(audio, 'info', None) and getattr(audio.info, 'length', None):
        seconds = int(round(audio.info.length))
        return f'{seconds // 60}:{seconds % 60:02d}'
    return ''


def cover_for(item_id, audio):
    # Prefer a manually supplied artwork file.
    for ext in ('jpg', 'jpeg', 'webp', 'png'):
        p = ARTWORK_ROOT / f'{item_id}.{ext}'
        if p.exists():
            return RAW_BASE + p.relative_to(ROOT).as_posix()

    # Otherwise extract the first embedded ID3 APIC/Picture.
    if audio is not None and getattr(audio, 'tags', None):
        for key in audio.tags.keys():
            if str(key).upper().startswith('APIC:'):
                pic = audio.tags[key]
                mime = getattr(pic, 'mime', '') or ''
                data = getattr(pic, 'data', None)
                if not data:
                    continue
                ext = (
                    'jpg' if mime == 'image/jpeg' else
                    'png' if mime == 'image/png' else
                    'webp' if mime == 'image/webp' else
                    'jpg'
                )
                ARTWORK_ROOT.mkdir(parents=True, exist_ok=True)
                out = ARTWORK_ROOT / f'{item_id}.{ext}'
                out.write_bytes(data)
                return RAW_BASE + out.relative_to(ROOT).as_posix()
    return ''


def path_type(path):
    """Return content type based on the folder immediately below audio/."""
    rel_parts = path.relative_to(AUDIO_ROOT).parts
    if rel_parts and rel_parts[0].lower() == 'podcast':
        return 'podcast'
    return 'music'


def read_common(path):
    audio = File(path, easy=False)
    tags = audio.tags or {}
    title = first(tags, 'TIT2', 'title') or re.sub(
        r'^Uprealband-', '', path.stem, flags=re.I
    ).replace('-', ' ')
    artist = first(tags, 'TPE1', 'artist') or 'Uprealband'
    album = first(tags, 'TALB', 'album')
    genre = first(tags, 'TCON', 'genre')
    year = year_from(first(tags, 'TDRC', 'TYER', 'date', 'year'))
    return audio, tags, title, artist, album, genre, year


def make_track(path):
    rel = path.relative_to(ROOT).as_posix()
    audio, tags, title, artist, album, genre, year = read_common(path)
    version = version_from_filename(path, title)
    rel_audio = path.relative_to(AUDIO_ROOT)
    universe = rel_audio.parts[0].upper() if len(rel_audio.parts) > 1 else ''
    track_id = slug(f'{title}-{version}') or slug(path.stem)
    return {
        'id': track_id,
        'type': 'music',
        'title': title,
        'artist': artist,
        'album': album,
        'year': year,
        'genre': genre,
        'version': version,
        'universe': universe,
        'cover': cover_for(track_id, audio),
        'audio': RAW_BASE + rel,
        'duration': duration_of(audio),
        'releaseDate': release_date(tags),
        'featured': False,
    }


def make_podcast(path):
    rel = path.relative_to(ROOT).as_posix()
    audio, tags, title, artist, album, genre, year = read_common(path)

    comment = ''
    for key, value in tags.items():
        if str(key).upper().startswith('COMM:'):
            comment = clean(getattr(value, 'text', value))
            if comment:
                break
    description = (
        txxx(tags, 'DESCRIPTION') or
        txxx(tags, 'SUMMARY') or
        comment or
        ''
    )
    podcast_id = slug(f'podcast-{title}') or slug(path.stem)

    return {
        'id': podcast_id,
        'type': 'podcast',
        'title': title,
        'description': description,
        'artist': artist,
        'album': album,
        'year': year,
        'genre': genre,
        'cover': cover_for(podcast_id, audio),
        'audio': RAW_BASE + rel,
        'duration': duration_of(audio),
        'releaseDate': release_date(tags),
    }



TRACK_ROOT = ROOT / 'track'
STORIES_OUTPUT = ROOT / 'stories.json'


def parse_frontmatter(text):
    meta = {}
    if text.startswith('---'):
        parts = text.split('---', 2)
        if len(parts) == 3:
            for line in parts[1].splitlines():
                if ':' not in line:
                    continue
                k, v = line.split(':', 1)
                meta[k.strip().lower()] = v.strip().strip('"\'')
            return meta, parts[2].lstrip('\n')
    return meta, text


def markdown_html(text):
    lines = text.replace('\r\n', '\n').splitlines()
    out = []
    para = []
    def flush():
        if para:
            joined = ' '.join(x.strip() for x in para).strip()
            if joined:
                joined = html.escape(joined)
                joined = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', joined)
                joined = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', joined)
                out.append(f'<p>{joined}</p>')
            para.clear()
    for line in lines:
        if not line.strip():
            flush(); continue
        m = re.match(r'^#{1,6}\s+(.+)$', line.strip())
        if m:
            flush(); out.append(f'<h3>{html.escape(m.group(1).strip())}</h3>'); continue
        if re.match(r'^[-*]\s+', line.strip()):
            flush(); out.append(f'<p>• {html.escape(re.sub(r"^[-*]\s+", "", line.strip()))}</p>'); continue
        para.append(line)
    flush()
    return '\n'.join(out)


def first_paragraph(text):
    clean_text = re.sub(r'^#{1,6}\s+', '', text.strip(), flags=re.M)
    blocks = [b.strip() for b in re.split(r'\n\s*\n', clean_text) if b.strip()]
    return re.sub(r'[*_`#]', '', blocks[0])[:360] if blocks else ''


def chapter_sort_key(item):
    m = re.search(r'(?:track|bab|chapter)?\s*0*(\d+)', item.get('chapter', ''), re.I)
    return (int(m.group(1)) if m else 999999, item.get('title', '').lower())


def make_story(path):
    raw = path.read_text(encoding='utf-8', errors='replace')
    meta, body = parse_frontmatter(raw)
    # Strip a leading title heading from body because the UI supplies the title.
    heading = re.match(r'^\s*#\s+(.+?)\s*\n+', body)
    title = meta.get('title', '')
    if heading:
        if not title:
            title = heading.group(1).strip()
        body = body[heading.end():]
    if not title:
        title = path.stem.replace('_', ' ').replace('-', ' ').strip()
    chapter = meta.get('chapter', '')
    if not chapter:
        m = re.search(r'(?:track|bab|chapter)[ _-]*0*(\d+)', path.stem, re.I)
        chapter = f'TRACK {int(m.group(1)):02d}' if m else 'TRACK'
    year = meta.get('year', '') or year_from(meta.get('date', '')) or year_from(path.stem)
    release = meta.get('date', '')
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', release):
        release = f'{year}-01-01' if year else ''
    story_id = slug(f'{chapter}-{title}') or slug(path.stem)
    excerpt = meta.get('excerpt', '') or first_paragraph(body)
    cover = meta.get('cover', '')
    if cover and not re.match(r'^https?://', cover):
        cover = RAW_BASE + cover.lstrip('./')
    tts_audio = meta.get('ttsaudio', meta.get('audio', ''))
    if tts_audio and not re.match(r'^https?://', tts_audio):
        tts_audio = RAW_BASE + tts_audio.lstrip('./')
    return {
        'id': story_id,
        'type': 'story',
        'chapter': chapter,
        'title': title,
        'year': year,
        'cover': cover,
        'excerpt': excerpt,
        'body': markdown_html(body.strip()),
        'ttsAudio': tts_audio,
        'ttsVoice': meta.get('ttsvoice', meta.get('voice', 'Gerry')),
        'soundtrackId': meta.get('soundtrack', meta.get('soundtrackid', 'tetap-menyala')),
        'releaseDate': release,
        'duration': meta.get('duration', ''),
        'source': path.relative_to(ROOT).as_posix(),
    }


def load_stories():
    stories = []
    if not TRACK_ROOT.exists():
        return stories
    allowed = {'.md', '.markdown', '.txt'}
    for path in sorted(TRACK_ROOT.rglob('*')):
        if not path.is_file() or path.suffix.lower() not in allowed:
            continue
        if path.name.lower() in {'readme.md', 'readme.markdown'}:
            continue
        try:
            stories.append(make_story(path))
        except Exception as exc:
            print(f'[WARN] Skip story {path}: {exc}')
    stories.sort(key=chapter_sort_key)
    return stories


def main():
    tracks = []
    podcasts = []
    stories = load_stories()

    if AUDIO_ROOT.exists():
        for path in sorted(AUDIO_ROOT.rglob('*')):
            if not path.is_file() or path.suffix.lower() != '.mp3':
                continue
            try:
                if path_type(path) == 'podcast':
                    podcasts.append(make_podcast(path))
                else:
                    tracks.append(make_track(path))
            except Exception as exc:
                print(f'[WARN] Skip {path}: {exc}')

    tracks.sort(
        key=lambda x: (x['releaseDate'] or '0000-00-00', x['title'].lower()),
        reverse=True,
    )
    podcasts.sort(
        key=lambda x: (x['releaseDate'] or '0000-00-00', x['title'].lower())
    )

    if tracks:
        tracks[0]['featured'] = True

    catalog = {
        'tracks': tracks,
        'stories': stories,
        'podcasts': podcasts,
    }
    OUTPUT.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
    )
    print(
        f'[OK] Wrote {OUTPUT} | '
        f'{len(tracks)} music track(s), {len(stories)} story track(s), {len(podcasts)} podcast episode(s)'
    )


if __name__ == '__main__':
    main()
