# Experiment 001 — Q01 Entity Conflation Failure

**Date:** 2026-10-02

## Test case

**Q01. Siapa yang membantu proses rekaman EP Uprealband?**

## Observed AI answer

AI answered that **Glen and Ismanu** helped the EP recording process.

## Correction

The supported attribution is:

- **Glen** — helped with the EP recording process.
- **Ismanu** — was previously involved in the EP process, but this does **not** establish that Ismanu participated in the recording.

Therefore, the correct answer to Q01 is **Glen**.

## Failure mode

**Entity / role conflation.**

The AI combined two nearby pieces of information:

1. Glen is explicitly connected to helping with the EP recording.
2. Ismanu is explicitly connected to the EP process.

It then incorrectly promoted both people into the same action: helping with the recording.

This is a distinct failure from inventing a completely unsupported person or event. The entities and general context are present in the source, but the **action-to-person attribution is wrong**.

## Required structural fix

Machine-readable data should represent the relationship between a person and a specific action/event explicitly.

The archive should distinguish:

- person
- event
- action/role
- evidence supporting that exact relationship

A person mentioned in the same context must not automatically inherit another person's action.

Conceptually:

`Glen → helped_recording → EP`

does not imply:

`Ismanu → helped_recording → EP`

If the source only establishes that Ismanu was involved in the EP process, the recording-specific participation should remain **UNKNOWN** unless explicitly supported.

## Research significance

This becomes a dedicated test case for **entity-role attribution**.

The experiment should test whether explicit person → action → event → evidence links reduce this type of conflation.

This correction does not by itself prove that machine-readable structure solves the problem. It records the observed failure and the structural requirement for the next test.

**Status:** Failure recorded; structural fix to be tested.
