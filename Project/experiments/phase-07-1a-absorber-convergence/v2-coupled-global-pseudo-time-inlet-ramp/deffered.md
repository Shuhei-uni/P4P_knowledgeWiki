# Phase 7.1A — v2 Coupled global pseudo-time inlet ramp

> **Status — DEFFERED (2026-09-22):** Deferred after the Server-3 approach
> was paused; retain this setup as planning provenance only.

## Question

Does the v2 virtual liquid outlet show a cleaner numerical response when the
pressure and velocity equations are solved with Fluent's Coupled scheme and
steady global pseudo-time marching, while every other v2 baseline setting is
held fixed?

This is a solver-treatment comparison against the completed v2 steady
inlet-loading ramp. Pseudo-time is numerical marching only; no physical flow
time is introduced.

## Exact parent and controlled delta

- Parent: the verified `P71A-BASELINE-V2-VIRTUAL-OUTLET-prepared` case/data
  pair from the v2 baseline build.
- Runtime: Fluent 2025 R2 on server 1.
- Solver formulation: pressure-based, steady.
- Controlled delta 1: pressure–velocity coupling `SIMPLE` → `Coupled`.
- Controlled delta 2: steady pseudo-time method → `Global Time Step` with
  `Automatic` pseudo-timestep selection initially.
- Unchanged: v2 mesh, cell zones, models, volume-fraction/slip treatment,
  spatial discretization, boundary roles, absorber named expressions and
  source terms, inlet ramp, report definitions, and convergence-monitor
  settings.
- Absorber: leave `P71V2Sink` authoritative. Its requested removal follows the
  instantaneous phase-2 liquid-inlet command; no source retuning is allowed.
- Physical time: must remain steady; the run must use native solver iterations,
  not `dual-time-iterate` or any physical transient command.

## Horizon and checkpoints

Run `2,000` native steady solver iterations in `10`-iteration inlet-control
blocks. Start the liquid and steam inlets at `0.25` of the recorded base
targets and ramp linearly to `116.92 kg/s` liquid and `80.69 kg/s` steam by
active iteration `2,000`. Preserve paired case/data checkpoints at active
`0`, `500`, `1,000`, `1,500`, and `2,000` on server 1 local disk; copy only
the terminal pair to the recorded OneDrive final root.

## Required evidence

Record on Fluent's native iteration coordinate:

1. mixture, phase-1, and phase-2 steam outlet fluxes;
2. liquid and steam inlet fluxes;
3. `P71V2Command`, named-expression removal, and native applied phase-2 source;
4. lower-zone liquid availability and lower-zone liquid inventory; and
5. total liquid mass and liquid volume over both fluid zones.

Also preserve the Coupled/pseudo-time readback, residual history, transcript,
event schedule readbacks, checkpoint identities, and terminal paired-artifact
hashes. The pseudo-time controls must be explicitly identified as numerical;
no pseudo-time value may be interpreted as physical time.

## Decision use and claim limit

Use the comparison to assess solver robustness and the response of the v2
absorber during the same inlet-development history. Do not call the case
physically transient, and do not treat lower residuals alone as proof of a
credible absorber or bounded inventory. Any convergence or performance claim
still requires finite residuals, bounded late-window behaviour, credible
phase-resolved/source-inclusive balances, and explained outlet reverse flow.
