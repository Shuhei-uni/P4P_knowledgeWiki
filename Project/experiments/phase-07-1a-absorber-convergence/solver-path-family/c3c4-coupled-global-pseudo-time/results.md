# P71A-C3C4-COUPLED-GLOBAL-PSEUDO-TIME results

## Status

**NOT RUN — setup prepared; live preflight and Student endpoint unavailable.**

No solver result or convergence claim exists. The setup is a bounded discovery
screen for the combined Coupled + Global Time Step solver package; it is not a
claim about pseudo-time alone or absorber validity.

## Execution record

- Exact parent: active-1000 paired absorber case/data, as specified in
  `deffered.md` and `turbulence-family/parent-reference.md`.
- Live endpoint: Student endpoint was unreachable during preparation on
  2026-09-15.
- Read-only API probe: Fluent 2025 R2 server 3 exposed
  `solution.methods.pseudo_time_method`, but server 3 is not the absorber
  parent and was not used for mutation or calculation.
- Required next action: reconnect to Student, inspect the live Mixture
  parent, resolve the exact Global Time Step controls, then perform the
  prepared save/reopen and smoke gates before any discovery iterations.

## Evidence placeholders

Populate only after a verified run:

- parent/child readback:
- smoke result:
- pseudo-time and coupling controls:
- residual histories:
- source and phase balances:
- liquid and vapor inventories:
- limiter/reverse-flow/warning diagnostics:
- checkpoints and figures:
