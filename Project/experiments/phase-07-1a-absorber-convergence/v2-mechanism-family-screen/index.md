# Phase 7.1A — v2 mechanism family screen

## Status

**Human-selected planning direction — 2026-09-22.** Two new experiment
families are derived from the verified Phase 7.1A v2 60k virtual-liquid-outlet
baseline:

- [Family R — wall roughness](../roughness-family/index.md) on **Server 1**;
- [Family E — Eulerian Wall Film](../ewf-family/index.md) on **Server 3**.

The two families are intended to run in parallel as independent server-local
discovery streams. This record creates the scientific envelope; it does not by
itself authorize a Fluent solve.

The server assignment follows the natural family order requested by the human:
R to Server 1 and E to Server 3. The live endpoint identity and reachability
must still be read back at execution preflight. No live session, checkpoint, or
working directory may be shared between the two streams.

## Shared question and control

The two families test distinct mechanisms while keeping the same control:

> Does stronger wall shear, or explicit wall-film formation and drainage,
> change the near-wall liquid trajectory and lower-region routing that the v2
> bulk Mixture field currently produces?

The canonical control is **C0**, equivalent to both `R0` and `E0`:

| Setting | C0 shared control |
| --- | --- |
| v2 absorber | active, phase-2-only, inlet-throughput controlled |
| EWF | off |
| wall roughness height `k_s` | `0 m` |
| roughness constant `C_s` | not active in the smooth-wall control |
| bottom boundaries | walls |
| direct phase-1 mass source | none |

If a server-local control copy is needed for a fair same-endpoint comparison,
label it `C0-S1` or `C0-S3`; these are repeated executions of the same C0
condition, not different scientific controls. They must be derived from the
same verified parent identity.

## Common parent and loading rule

Every C0 and family child must begin from an independently loaded copy of the
prepared v2 pair recorded in
`../baseline-v2-virtual-liquid-outlet/run-paths.yaml`. The child must hash,
reopen, and read back the parent before applying its one physical delta.

The first `2,000` native steady iterations are now an explicit common inlet
development ramp for the v2 baseline and both families:

- start multiplier: `0.25` of the final targets;
- linear ramp to multiplier `1.00` over active iterations `1–2,000`;
- update interval: every `10` iterations;
- liquid target: `116.92 kg/s`;
- steam target: `80.69 kg/s`.

The instantaneous inlet commands are therefore `116.92 f` and `80.69 f`,
where `f` increases from `0.25` to `1.00`. The existing
[v2 inlet-loading record](../v2-inlet-loading-ramp/deffered.md) is the source
of this schedule and its completed finite-horizon evidence. A later base-flow
hold or longer qualification horizon is not silently included in these family
packets; it requires a separate decision after the 2,000-iteration screen.

## Frozen comparison scaffold

Unless a family row explicitly names its single mechanism delta, preserve:

- the verified `Separator-purnanto-60k.msh.h5` mesh and v2 virtual-outlet zone;
- steady pressure-based Mixture/RNG k-epsilon physics;
- the phase-2-only v2 source, matching liquid momentum removal, and shared
  turbulence removal;
- zero direct phase-1 mass source and no vapor sink;
- fresh Hybrid Initialization with no patched liquid pool;
- the two mass-flow inlets and `steamoutlet` as the only pressure outlet;
- all bottom boundaries as walls;
- existing solution methods, discretization, under-relaxation, residual
  definitions, DPM trace objects, and energy/species-off state.

The family delta must not be mixed with turbulence, pressure-coupling,
discretization, outlet, mesh, absorber-zone, initialization, or transient
changes. No third EWF-plus-roughness interaction family is active yet.

## Common evidence contract

Each branch must preserve native-iteration histories and paired checkpoints,
and must report at minimum:

1. inlet commands and realized liquid/steam phase fluxes;
2. `P71V2Command`, native applied phase-2 source, and zero phase-1 source;
3. lower-zone available liquid and lower-zone inventory;
4. whole-separator liquid inventory and liquid volume;
5. mixture, vapor, and liquid fluxes at `steamoutlet`;
6. source-inclusive phase and mixture closure, including storage when the field
   is not stationary;
7. residuals, reverse flow, and turbulence-viscosity limiting; and
8. family-specific near-wall trajectory evidence.

The principal cross-family metrics are outer-wall mean liquid vertical
velocity, lower-vessel liquid inventory, desired liquid discharge, steam
leakage through the bottom region, and liquid carryover through `steamoutlet`.
For EWF, add film mass/inventory and film flow toward the bottom whenever the
Fluent model exposes those quantities.

## Throughout-run monitoring schedule

For the later R/E mechanism branches, use the same native monitoring cadence
as Family N so mechanism and solver results remain comparable:

- **Every 10 iterations:** inlet commands and realized phase fluxes;
  v2 command versus applied phase-2 source; direct phase-1 source audit;
  lower-zone availability/inventory; total liquid and vapor inventory;
  phase-resolved `steamoutlet` fluxes; source-inclusive closure; residuals;
  reverse-flow activity; warnings/limiting; and elapsed block time.
- **At active 0, 500, 1,000, 1,500, and 2,000:** paired case/data checkpoint,
  solver and mechanism readback, native monitor snapshot, and phase-fraction /
  velocity field evidence. For EWF, include film inventory and transfer fields
  wherever available; for roughness, include the outer-wall trajectory and
  wall-setting readback.
- **At any failure or discontinuity:** preserve the first event iteration, last
  valid monitor row, last valid paired checkpoint, transcript, and readback;
  never repair the branch by silently changing its declared single delta.

Interpret each branch over the same windows (`0–500`, `500–1,000`,
`1,000–1,500`, and `1,500–2,000`). The primary decision is based on the
late-window trend and variability of routing, inventory, source-inclusive
closure, and family-specific mechanism evidence—not on a final residual value
alone.

## Decision boundary

The result is informative only when the mechanism delta is verified and the
phase/source accounting remains auditable. A family may show a useful
mechanistic effect without being numerically qualified. No branch may be
called physically validated, plant-effective, or steady solely because its
residuals are lower or its liquid inventory is smaller.
