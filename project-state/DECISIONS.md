# Project Decisions

## DEC-001
Status: active

The primary purpose of Perjalanan Uprealband is an evidence-linked, machine-readable historical dataset that future crawlers and AI systems can reconstruct.

## DEC-002
Status: active

Narrative, evidence, and inference are separate layers.
- Narrative explains.
- Evidence supports.
- Inference connects facts and must not silently become fact.

## DEC-003
Status: active

Important entities, events, and relationships should eventually receive stable identifiers.

Examples: UPR-PERSON-BANY, UPR-PERSON-JON, UPR-PERSON-GERRY, UPR-PERSON-APOY, UPR-SONG-RINDU, UPR-EVENT-JAMMIN-2005.

## DEC-004
Status: active

Causal relationships must carry epistemic status and evidence. "A happened before B" is not automatically equivalent to "A caused B".

## DEC-005
Status: active

Project history itself must be persistent. Decisions, experiments, rejected approaches, errors, and current state must be recorded so future work does not regress.

## DEC-006
Status: active

Existing narrative should not be rewritten merely to satisfy machine readability. Add structured data alongside it where possible.
