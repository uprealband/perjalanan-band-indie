# UprealBand Music Hub: automatic catalog

This package adds a GitHub Action that rebuilds `catalog.json` whenever MP3 files under `audio/` change.

## Repository layout expected

```text
audio/
  hybrid/
    Uprealband-Biarkan-Cintamu-Funk-Soul-Hybrid.mp3
  evolution/
    ...
artwork/                 # optional, e.g. artwork/biarkan-cintamu-funk-soul-hybrid.jpg
scripts/
  generate_catalog.py
.github/workflows/
  catalog.yml
catalog.json             # generated automatically
```

## What the Action does

1. Reads MP3 ID3 metadata with Mutagen.
2. Gets Universe from the first folder under `audio/`.
3. Derives Version from the filename after the ID3 Title.
4. Calculates duration.
5. Builds raw GitHub audio URLs.
6. Writes `catalog.json`.
7. Commits the updated catalog back to `main`.

The Blogger frontend can then read:

`https://raw.githubusercontent.com/uprealband/perjalanan-band-indie/main/catalog.json`

## Important

The MP3 itself remains in GitHub. Blogger only reads the catalog and streams the MP3 URL.

If a release date is not present in ID3, the generated `releaseDate` falls back to January 1 of the tagged year. If no year is available, it stays blank.

Artwork is optional. If `artwork/<track-id>.jpg` (or `.jpeg`, `.webp`, `.png`) exists, the generated catalog points to it automatically.
