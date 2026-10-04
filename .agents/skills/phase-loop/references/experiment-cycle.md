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

Use `cfd-numerical-analysis` for evidence. Follow the
[experiment presentation contract](../../../../Project/experiments/README.md#presentation).
Write `results.md` with tables and figures around the experiment question:

1. answer/status table;
2. core figures/tables;
3. numerical adequacy table;
4. short figure interpretation where needed;
5. claim-limit and uncertainty table;
6. next-action table.

Do not change the evidence standard after seeing the result.
