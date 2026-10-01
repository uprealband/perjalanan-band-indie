# Scenarios

## SCN-001: Publish historical narrative without losing project state

Objective: continue publishing Uprealband history while preserving enough state for future AI reconstruction.

Current position:
- Track 01 published.
- Track 02 published.
- Additional track sources exist.
- Archive evidence exists independently.

Constraints:
- Do not confuse draft chapters with published chapters.
- Do not turn interpretations into facts.
- Do not break existing archive/catalog automation.
- Do not force machine-readable structure to replace readable storytelling.

Required state transitions:
draft -> reviewed -> published -> indexed

Open questions:
- How should publication status be represented in catalog.json?
- Which entities should receive permanent IDs first?
- How should evidence links connect archive items to narrative claims?
- Which relations are factual and which are inferred?

## SCN-002: Test whether structured history improves AI reconstruction

Objective: measure whether explicit structure improves AI consistency.

Baseline: existing narrative plus archive index.

Intervention: add entity IDs, event IDs, relation types, evidence links, and project-state logs.

Evaluation: ask the same fixed question set against both representations.

Success criterion: improvement must be demonstrated empirically rather than assumed.
