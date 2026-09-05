# UprealBand Music Hub: Auto-Catalog V3

This package rebuilds `catalog.json` whenever MP3 files under `audio/` change.

## Content routing

The first folder below `audio/` determines the content type:

```text
audio/
  hybrid/        -> catalog.tracks[] + Universe HYBRID
  evolution/     -> catalog.tracks[] + Universe EVOLUTION
  soundtrack/   -> catalog.tracks[] + Universe SOUNDTRACK
  podcast/       -> catalog.podcasts[]  (NOT Music, NOT a Universe)
```

This separation is intentional. Podcast is a content type, not a Music Universe.

## Podcast metadata

The generator reads normal ID3 metadata for title, artist, album, genre, year, duration and cover.

Optional Mp3tag custom TXXX fields are supported:

- `SEASON` -> e.g. `S01`
- `EPISODE` -> e.g. `EP 01`
- `DESCRIPTION` -> podcast description
- `SUMMARY` -> fallback description

If `EPISODE` is empty, the ID3 Track number is used. If that is also empty, the generator assigns episode numbers after sorting podcasts by release date/title.

The title is never modified to add `S01` or `EP 01`.

## Artwork

The generator first checks `artwork/<id>.(jpg|jpeg|webp|png)`. If no external artwork exists, it extracts the first embedded ID3 APIC image from the MP3 and saves it under `artwork/`.

## GitHub Action

The workflow:

1. Installs Mutagen.
2. Reads MP3 metadata.
3. Separates Music and Podcast by folder.
4. Extracts embedded artwork when needed.
5. Generates `catalog.json` with `tracks`, `stories`, and `podcasts`.
6. Commits `catalog.json` and `artwork/` back to `main`.

The Blogger frontend reads:

`https://raw.githubusercontent.com/uprealband/perjalanan-band-indie/main/catalog.json`
