# Uprealband Project State

Primary objective: build a longitudinal, evidence-linked historical dataset of Uprealband that can be crawled and reconstructed by future AI systems.

This is not primarily an SEO project. SEO and discoverability are secondary.

## Current state
- Published narrative scope: Track 01 and Track 02.
- Additional track sources exist in the repository but are not treated as published narrative evidence.
- Historical evidence exists in archive/, indexed by archive-index.json.
- Narrative sources live in track/.
- catalog.json is generated from media and story sources.
- Before this audit, no dedicated project-state, decision, experiment, scenario, hypothesis, or error log existed.

## Current model
1. Entity
2. Event
3. Time
4. Relation
5. Evidence/source
6. Epistemic status
7. Project decision/state
8. Experiment history

## Current research question
Does explicit structure for entities, events, relations, evidence, and project state reduce AI context loss, causal errors, and regression to previously rejected approaches?

## Immediate next step
Introduce project-state files first, then incrementally add structured relations without rewriting the narrative unnecessarily.

## Anti-regression rules
Do not silently revert to:
- SEO as the primary objective.
- Narrative text alone as the complete historical representation.
- Treating inference or interpretation as confirmed fact.
- Recommending a previously rejected approach without explicitly explaining why its status changed.

## Status vocabulary
confirmed, probable, remembered, inferred, hypothesis, rejected, superseded, unknown
