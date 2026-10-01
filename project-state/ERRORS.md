# Error and Anti-Regression Log

## ERR-001
Status: resolved

Problem: project direction can be reduced to SEO/content publishing.

Why this is an error: SEO is a distribution/discoverability concern. The primary research objective is machine-readable historical reconstruction.

Replacement: DEC-001.

## ERR-002
Status: active risk

Problem: AI can lose the state of previous decisions and repeat a previously rejected approach.

Mitigation: maintain CURRENT-STATE.md, DECISIONS.md, EXPERIMENTS.md, SCENARIOS.md, and this error log.

## ERR-003
Status: observed in Track 01

Problem: Track 01 contains duplicated Tokoh, Tempat, and Tahun sections.

Impact: duplicate metadata creates unnecessary ambiguity for parsers and downstream AI extraction.

Mitigation: normalize metadata generation/source structure later. Do not remove historical narrative merely because it is repetitive.

## ERR-004
Status: observed in Track 02

Problem: Track 02 does not use exactly the same heading/front-matter structure as Track 01.

Impact: extraction of title, chapter, year, entities, and topics becomes less deterministic.

Mitigation: establish one canonical story metadata schema before publishing additional chapters.

## ERR-005
Status: active risk

Problem: repository contains many future track source files while only a subset is intended to be publicly published.

Impact: a machine may confuse draft material with published narrative.

Mitigation: add explicit publication status to story metadata/catalog entries.
