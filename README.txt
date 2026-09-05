UPREALBAND AUTO-CATALOG FIXED

Replace the existing repository file:
  scripts/generate_catalog.py

This version reads:
  audio/**/*.mp3      -> catalog.tracks[]
  audio/podcast/*.mp3 -> catalog.podcasts[]
  track/**/*.(md|markdown|txt) -> catalog.stories[]

The GitHub Actions workflow runs:
  python scripts/generate_catalog.py

After replacing the script, commit/push it. The Build Music Hub Catalog workflow should run automatically because scripts/generate_catalog.py is in its push path.

Expected log format:
[OK] Wrote .../catalog.json | 13 music track(s), 16 story track(s), 2 podcast episode(s)

README.md files inside track/ are skipped.
