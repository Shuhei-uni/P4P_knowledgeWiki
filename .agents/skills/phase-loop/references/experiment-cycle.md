# Experiment cycle

## Design

Write only what another capable agent needs to execute and judge the experiment:

- question / hypothesis;
- exact parent;
- controlled delta and invariants;
- run horizon/mode;
- required evidence and 1–5 core figures;
- decision rule and claim limit.

Prefer one controlled comparison over a broad matrix unless screening needs
breadth.

## Build and run

Use `pyansys-workflow`. Do not spend long compute on an unverified child.
Readback + save/reopen + smoke/instrumentation proof should establish that the
intended experiment actually exists.

Discovery stays short enough for quick evidence-driven iteration. Qualification
gets the horizon needed for the intended statement and deterministic completion
proof.

## Analyse and interpret

Use `cfd-numerical-analysis` for evidence. Then write `results.md` around the
experiment question:

1. answer at a glance;
2. core figures/tables;
3. numerical adequacy;
4. observations;
5. interpretation and claim limits;
6. next action.

Do not change the evidence standard after seeing the result.
