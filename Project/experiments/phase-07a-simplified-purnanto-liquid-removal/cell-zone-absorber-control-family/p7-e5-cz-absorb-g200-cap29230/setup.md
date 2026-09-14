# P7-E5-CZ-ABSORB-G200-CAP29230 setup

## Status and authority

| Field | Contract |
| --- | --- |
| Status | BLOCKED_VERIFIED — solver divergence/floating-point exception during the block ending at active 450; valid evidence through active 400 is recorded in [results.md](results.md) |
| Phase | Phase 07 simplified Purnanto liquid-removal mechanisms |
| Lifecycle | discovery |
| Candidate | E5-CZ-ABSORB / H6 lower-inventory absorber-control extension |
| Origin | Human-approved direction and family design on 2026-09-10 |
| Authority | Human-approved-context-only; explicit Phase Loop launch entered in this chat on 2026-09-10 |
| Gate | G3 — lower-inventory absorber-capacity screen |
| Family | [E5-CZ absorber-control design](../design.md) |

## Question and hypothesis

**Question:** Can the no-outlet lower-zone absorber reduce accumulated liquid
when its command is driven by lower-zone phase-2 inventory and bounded by a
source cap of 292.30 kg/s?

**Hypothesis:** Under the unchanged split topology and source formulation, a
lower-inventory feedback law with G=2.00 and this cap may pull the lower
absorber inventory toward a declared numerical target without directly
absorbing phase-1 vapor. This is a hypothesis for a bounded discovery screen,
not a predicted result or a physical brine-pool claim.

## Parent and comparison basis

Use only the exact final paired case/data state from
P7-E5-CZ-G100-CONT2500-student-20260910T070332Z, active 2,500,
approximately native 3,000, as recorded in the completed continuation
run-paths.yaml. The parent continuation has an explicit stale post-reopen
runtime-counter field. Before any solve, reopen the parent and record
topology, source tree, active/native iteration readback, report-history extent,
lower-zone inventory, and the discrepancy. If the pair or evidence basis
cannot be proven, block this child rather than selecting a different parent.

The child is a matched continuation from the same accumulated parent as the
other two family members. It must not be compared as if it were a cold-start
E0 screen.

## Controlled delta

Only the source-capacity limit differs between family members. This child uses:

- fixed adaptive gain: G=2.00;
- source cap: 292.30 kg/s;
- lower-zone primary feedback: phase-2 liquid mass in p7-e5-lower-y010;
- parent-relative numerical target: M_L,target = 0.50 × M_L0;
- local error: e_L = max(0, (M_L - M_L,target) / M_L,target);
- requested command: Q = clamp(2.00 × 116.92 kg/s × e_L, 0, 292.30 kg/s);
- controller update interval: every 50 active iterations; and
- lower-zone phase-2 volumetric source: S_mass = -Q/V_lower.

The 0.50 × M_L0 target is an explicit numerical planning assumption, where
M_L0 is read from the active-2,500 parent. It is not a real pool height,
plant setpoint, or physical validation target. It must be recorded before
solving and must not be changed after seeing the result.

The mixture x/y/z momentum source is updated from the lower-zone phase-2
velocity basis and audited with the phase-2 mass source. This is the native
zone-scoped approximation, not the unavailable local-cell mass-weighted UDF
law.

## Frozen invariants

- no bottom outlet, bottom-boundary change, or explicit drainage path;
- same split topology: separator-purnanto plus p7-e5-lower-y010;
- lower register: 0 ≤ y ≤ 0.10 m; expected marked cells 3,794;
- expected total mesh counts: 342,609 cells, 1,647,633 faces, and 1,046,255
  solver nodes;
- same material, phase mapping, Mixture model, turbulence, gravity,
  initialization state, numerics, outlets, and monitors as the parent;
- direct phase-1 mass source disabled/none everywhere;
- phase-2 mass source and matched mixture momentum source only in the lower
  zone;
- no energy, turbulence, parent-zone, UDF, patch/reset, remesh, re-split, or
  zone-enlargement change; and
- no qualification interpretation or automatic continuation.

## Run intent

- Mode: steady discovery continuation.
- Horizon: 500 controller-active iterations after parent readback.
- Smoke: first 50 active iterations with source/readback and warning checks.
- Update cadence: every 50 active iterations.
- Checkpoints: paired case/data at child-start, active 100, 250, and 500, plus
  the nearest valid recovery state if blocked.
- Finalization: save final case/data, reopen, read back topology/source state,
  and preserve the terminal manifest and histories.
- Durability: retain the exact parent identity, child output root, source
  audit, nested inventory histories, residual transcript, warnings, and final
  paired state.

## Required evidence

### Hard pre-run evidence

- exact parent pair exists and reopens;
- topology, mesh metrics, lower-zone identity/volume, and source tree read back;
- stale runtime-counter limitation and authoritative history coordinate recorded;
- M_L0, target mass, liquid density, and target formula recorded;
- nested lower-region monitors exist for the absorber band, adjacent band, and
  broader lower-half diagnostic band;
- phase-2 source, phase-1 source-off, mixture momentum source, G, cap, signs,
  units, and 50-iteration cadence read back;
- total liquid, lower-zone liquid mass/volume, nested bands, vapor inventory and
  flux, phase/mixture balances, source get_sum, residuals, and warnings are
  file-backed; and
- save/reopen plus smoke verification passes before counting discovery data.

### Run-time evidence

Record every controller update with active/native iteration, M_L, M_L0,
target, local error, requested/clamped command, cap/saturation, phase-2 source,
mixture momentum source, direct phase-1 source state, integrated user source,
and lower-zone phase-2 velocity basis.

Retain total and nested lower inventories; phase-resolved inlet, steam-outlet,
treated-bottom, and user-source balances; vapor loss; mixture closure;
residuals; reversed-flow/limiting/divergence warnings; and all checkpoints.
Zero bottom phase-2 boundary flux is compatible with this absorber abstraction
and is a supporting diagnostic, not the primary removal metric.

## Core figure plan

| Figure | Question | Evidence and use |
| --- | --- | --- |
| F1 — inventories | Does local absorber control reduce buildup? | Total liquid plus lower-zone/nested-band phase-2 inventories versus child active iteration, with target band and parent anchor. |
| F2 — command/audit | Is cap capacity the limiting factor and is the phase-2 source realized? | Local error, command, cap/saturation, integrated phase-2 source, source density, and direct phase-1 source on the 50-iteration controller coordinate. |
| F3 — phase/numerical credibility | Does apparent liquid disappearance preserve the intended phase routing and numerical evidence? | Phase/mixture/user-source balances, vapor inventory/flux, bottom vapor loss, residuals, and warning summary. |

## Decision gate

This child is useful only if all pre-run, source, smoke, and evidence gates pass.
The family may justify a later human decision only if one cap materially lowers
the late total-inventory slope, keeps lower-zone inventory bounded near the
predeclared target, avoids persistent saturation, leaves direct phase-1 mass
source zero, and does not materially worsen vapor response or numerical
credibility.

Persistent lower/total inventory drift, cap saturation without local response,
source/momentum mismatch, direct vapor removal, severe vapor disturbance, open
source-dominated balance, or solver failure are bounded negative/ambiguous
results. They do not authorize a new mechanism.

## Claim limits

This child can support only a bounded numerical statement about this parent,
mesh, source formulation, target rule, cap, and 500-iteration window. It cannot
establish physical brine-pool level control, physical outlet fidelity, physical
time drainage, mesh independence, steady convergence, plant performance, or
qualification.
