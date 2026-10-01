# Experiment 001 — Machine-Readable Archive vs Narrative Interpretation

**Date:** 2026-10-02

## Research question

Does machine-readable structure help AI distinguish:
- direct facts
- temporal relationships
- causal relationships
- inference / interpretation

The practical concern is that an AI may add narrative embellishment when summarizing historical archives. An interpretation may be compatible with the story while still not being an explicit fact in the source.

## Baseline source set

The experiment uses these three pages as the intended source set:

1. https://perjalanan.uprealband.com/2026/10/pengantar-perjalanan-uprealband-2004.html
2. https://perjalanan.uprealband.com/2026/10/bab-01-operasi-merayu-gerry.html
3. https://perjalanan.uprealband.com/2026/10/bab-02-misi-mangga-dua-dan-kedatangan.html

For a controlled comparison, the same source set and the same question set should be reused after machine-readable data is introduced.

## Baseline question set

Q01. Siapa yang membantu proses rekaman EP Uprealband?
Q02. Siapa yang menjadi bassist setelah Ismanu keluar?
Q03. Mengapa posisi bassist kembali kosong setelah Eka?
Q04. Mengapa Gerry kemudian dipertimbangkan menjadi bassist?
Q05. Siapa yang menjadi drummer setelah Gerry pindah ke bass?
Q06. Bagaimana Apoy ditemukan?
Q07. Di mana rehearsal pertama dengan Apoy dilakukan?
Q08. Apakah audio video klip 2004 direkam bersamaan dengan visual videonya?
Q09. Siapa yang memainkan bass pada audio video tersebut?
Q10. Apakah Eka memainkan bass pada audio video tersebut?
Q11. Apakah hubungan Ismanu keluar → Eka bergabung merupakan hubungan temporal atau kausal?
Q12. Apakah semua hubungan antarperistiwa dalam cerita dapat dianggap sebagai hubungan sebab-akibat?

## Required answer discipline

Every answer should distinguish:

- **FACT** — explicitly stated by the source.
- **TEMPORAL** — the source establishes that one event occurs before/after another.
- **CAUSAL** — the source explicitly supports a cause-and-effect relationship.
- **INFERRED** — a conclusion derived from the source but not explicitly stated.
- **UNKNOWN** — the source set does not provide enough evidence.

Temporal sequence must not automatically be converted into causality.

If the source does not support an answer, the correct output is UNKNOWN, not a plausible completion.

## Baseline observation

A useful failure mode to test is narrative embellishment.

An AI may transform a sequence of documented events into evaluative language such as describing the band as particularly "hebat", "tahan banting", or "pantang menyerah". Such language may be an interpretation of the overall story, but it should not be treated as a historical fact unless the source explicitly supports that characterization.

Another failure mode is:

A happened → B happened

being rewritten as:

A caused B

without explicit causal evidence.

## Hypothesis

**H1:** Explicit machine-readable event and relation structures will reduce unsupported causal inference and narrative embellishment compared with narrative-only presentation.

This is a hypothesis, not a conclusion.

## Next experiment

Run the identical Q01–Q12 test against:

### Condition A
Narrative pages only.

### Condition B
Narrative pages + machine-readable event data.

### Condition C
Machine-readable event data with explicit relation types and evidence references.

Then compare:

1. unsupported factual claims
2. temporal-to-causal conversions
3. unsupported interpretations
4. unsupported filling of UNKNOWN
5. evaluative embellishment

## Evaluation principle

The goal is not to make the AI sound more enthusiastic or more impressive.

The goal is to make the AI more precise about what the archive actually establishes.

> The archive owns the facts. The reader may form the interpretation.

## Current status

**Baseline established.**

No conclusion about the effectiveness of machine-readable structure should be recorded until the same questions have been tested under the later conditions.