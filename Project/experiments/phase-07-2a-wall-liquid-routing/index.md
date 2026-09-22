# Phase 7.2A — Wall-Liquid Routing and Steam-Outflow Carryover

## Status

**Human-selected phase created on 2026-09-22.** The completed Phase 7.1A R0
Coupled / Global-Time-Step continuation is promoted as the starting numerical
baseline for this phase. Phase 7.2A asks whether wall roughness or Eulerian
Wall Film can reduce liquid reaching the steam outlet while preserving the
control's useful numerical behaviour and auditable phase/source balances.

The scientific authority is [CONTEXT.md](CONTEXT.md). The exact baseline pair,
hashes, and reuse rules are in the [baseline handoff](baseline-control-handoff.md).
The throughout-run evidence requirements are in the
[monitoring contract](monitoring-contract.md).

## Phase question

> Can a wall-treatment mechanism change wall-adjacent liquid routing enough to
> reduce phase-2 liquid carryover through `steamoutlet`, without sacrificing
> absorber command tracking, source-inclusive mass closure, liquid-inventory
> behaviour, or vapor routing relative to the R0 control?

## Starting baseline

The Phase 7.2A baseline is `P72A-R0-SMOOTH-CONTROL-COUPLED-GLOBAL-TIME`, a
read-only scientific designation for the terminal Phase 7.1A run4 pair at its
final native report/transcript state, iteration `5586`. It is
smooth wall, EWF off, full-loading, steady Coupled / Global Time Step, with the
v2 phase-2-only throughput-controlled absorber. It is not a freshly initialized
case and it is not the earlier prepared v2 pair.

At the terminal report point the control had:

- phase-2 `steamoutlet` flux: `-24.3344 kg/s`;
- phase-1 `steamoutlet` flux: `-80.2509 kg/s`;
- total liquid mass: `295.8536 kg`;
- absorber command and applied removal: `116.9200 kg/s` and `116.9200 kg/s`;
- command error: `4.26e-14 kg/s`;
- continuity / phase-2 volume-fraction residuals: `2.7841e-3` /
  `5.4762e-4`;
- no AMG, FPE, nonfinite, or fatal events in the 1,000-iteration window.

These values define the reference state and comparison metrics, not a claim
that the separator is physically validated or fully steady.

## Selected family structure

- [Family R — wall roughness](roughness-family/index.md), with EWF off and
  `C_s=0.5` for active roughness.
- [Family E — Eulerian Wall Film](ewf-family/index.md), with roughness zero.

The first screen keeps the two mechanisms separate. It does not create an
interaction family and does not repeat the old first-2,000-iteration inlet
ramp. Each child starts from an independently loaded copy of the exact 7.2A
baseline pair and must pass a hash/reopen/readback gate before mutation.

## Execution boundary

The phase is planning-ready, not an instruction to mutate Fluent immediately.
The initial bounded screen is up to `1,000` additional native steady iterations
per child, with paired checkpoints at `0/250/500/750/1000`, live reports at
least every `10` iterations, and plots refreshed throughout the run. A later
longer continuation, an R+E interaction, a solver change, or a physical-model
change requires a separate phase decision.

## Evidence boundary

The minimum conclusion set is phase-resolved outlet carryover, total and lower
liquid inventory, absorber/source tracking, source-inclusive closure/storage,
residual and event health, and mechanism-specific wall/film evidence. Lower
residuals or lower total inventory alone cannot establish a positive routing
mechanism.
