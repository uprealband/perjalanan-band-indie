# Historical Data Layer

This directory is the machine-readable layer for the published historical narrative.

It does not replace the story text.

- entities.json = stable entities
- events.json = dated historical events
- relations.json = typed relationships
- sources.json = source/evidence references

## Epistemic rule

Temporal relation is not automatically causal relation.

Use explicit relation status such as:
- temporal
- explicit
- narrative_causal
- hypothesis

When a causal interpretation is not explicitly supported by the source, do not encode it as confirmed fact.

## Current scope

Track 01 and Track 02 only.

This is an experiment, not yet the final schema.
