# Phase Context — Phase 7.2A Wall-Liquid Routing and Steam-Outflow Carryover

## Status

**Human-selected phase direction — 2026-09-22.** Phase 7.2A starts from the
completed Phase 7.1A R0 Coupled / Global-Time-Step control continuation. That
run is a strong numerical starting baseline: it completed its continuation,
tracked the absorber command to machine precision, retained low late scaled
residuals, and did not encounter AMG failure, floating-point exception,
nonfinite residuals, or a fatal solver event. It also leaves the central
mechanism question unresolved: liquid carryover through `steamoutlet` remains
large, while reverse flow and turbulent-viscosity limiting persist.

The first 7.2A screen therefore compares two separate wall-routing
mechanisms—wall roughness and Eulerian Wall Film (EWF)—from the same developed
full-loading state. The mechanisms are not combined in the first screen, so a
change in steam-outlet liquid carryover can be attributed to one wall treatment
at a time.

## Evidence anchors

### Observed simulation evidence

- The [declared R0 control window](../phase-07-1a-absorber-convergence/roughness-family/r0-smooth-control/control-window.md)
  identifies the terminal second continuation as the comparison control. Its
  checkpoint ledger ends at expected native coordinate `5580`, while the final
  report/transcript state reaches native coordinate `5586`. Phase 7.2A uses
  that final `5586` state as its parent; the `4580–5580` interval remains the
  historical R0 comparison window.
- The [R0 control result](../phase-07-1a-absorber-convergence/roughness-family/r0-smooth-control/results.md)
  records the terminal second-continuation state and its limitations.
- The authoritative [run4 completion receipt](../../../PyAnsys/output/phase71a_r0_control_run4/authoritative-completion-receipt.json)
  reports a verified final pair, `1000` reverse-flow messages, `1000`
  turbulent-viscosity-limit messages, and no AMG/FPE/nonfinite messages.
- At the terminal report point, total liquid mass was `295.8536 kg`, liquid
  volume was `0.3357353 m^3`, and lower-zone liquid mass was `0.0021686 kg`.
  The absorber command and applied removal were both `116.9200 kg/s`, with
  command error `4.26e-14 kg/s`.
- The terminal phase-resolved outlet reports were approximately
  `-80.2509 kg/s` for phase 1 and `-24.3344 kg/s` for phase 2 at
  `steamoutlet`, for a mixture flux of `-104.5823 kg/s`. The phase-2 value is
  the primary liquid-carryover baseline for 7.2A; its sign convention must be
  stated in each child record.
- Terminal continuity and phase-2 volume-fraction residuals were
  `2.7841e-3` and `5.4762e-4`, respectively. These are useful numerical-health
  observations, not a steady-state qualification.

### Inference and remaining uncertainty

- **Inference:** the control is numerically durable enough to support a
  mechanism screen, but its lower liquid inventory and outlet routing are still
  evolving. A wall treatment should be judged by matched-window routing and
  balance evidence, not by a single lower residual or a lower total inventory.
- **Open question:** can wall momentum exchange or explicit film attachment
  reduce phase-2 liquid reaching `steamoutlet` and/or move that liquid toward
  the lower region without damaging vapor routing, source accounting, or
  numerical health?
- **Assumption to verify at preflight:** the final pair can be loaded and
  reopened on each assigned live Fluent endpoint, and the wall/EWF control
  needed for a family delta is exposed cleanly in Fluent 2025 R2. A capability
  gap is recorded as such; it is not to be emulated by changing another model.

## Phase contract

### Question

> Starting from the verified smooth-wall R0 terminal control state, can wall
> roughness or EWF reduce liquid carryover through `steamoutlet` by changing
> wall-adjacent liquid transport, while preserving absorber command tracking,
> low source-inclusive mass imbalance, bounded or improving liquid inventory
> behaviour, and credible vapor routing?

### In scope

- A matched steady continuation from the verified R0 terminal pair.
- Family R: roughness with EWF off and the rest of the model frozen.
- Family E: EWF with zero roughness and the rest of the model frozen.
- Native iteration histories, paired checkpoints, wall/mechanism readback,
  phase-resolved fluxes, source-inclusive closure, liquid inventory, and
  residual/event evidence.
- A first discovery window of up to `1,000` additional native steady
  iterations per child, with checkpoints at `0`, `250`, `500`, `750`, and
  `1,000`. The exact child horizon remains bounded by the live preflight and
  must be reported explicitly; extending it is a new execution decision.
- Parallel execution on independent server-local Fluent sessions when the
  endpoint and parent gates pass.

### Frozen invariants

Unless the family record explicitly names the single wall-treatment delta,
preserve:

- the 60k-mesh v2 virtual-outlet geometry and `p71a-v2-virtual-outlet` zone;
- steady pressure-based Mixture/RNG k-epsilon physics;
- the phase-2-only throughput-controlled absorber, matching liquid momentum
  removal, and shared `k`/`epsilon` removal;
- no direct phase-1 mass source and no direct vapor sink;
- full-loading liquid and steam inlet targets (`116.92` and `80.69 kg/s`);
- `steamoutlet` as the pressure outlet and all bottom boundaries as walls;
- materials, gravity, discretization, solution controls, and steady
  formulation from the verified control endpoint;
- no physical transient formulation, mesh change, outlet change, absorber
  change, inlet ramp, whole-domain reinitialization, or patched liquid pool.

The run4 endpoint is already a developed full-loading state. The old v2
`0.25 -> 1.00` first-2,000-iteration loading rule remains historical context
for Phase 7.1A and is not replayed in 7.2A children.

### Out of scope and claim limits

- No roughness-plus-EWF interaction in the initial single-mechanism E0–E2/R0–R3
  screen. The human-selected E3 follow-on combines E1 basic EWF with the
  already tested R3 wall roughness (`k_s=5e-4 m`, `C_s=0.5`), from the same
  verified parent; phase accretion stays off in E3.
- No claim that lower carryover proves physical wall-scale validity, plant
  separation efficiency, or hardware drainage performance.
- No claim of steady convergence solely from the control's low residuals or a
  child completing its iteration budget.
- No inference of film drainage from a global liquid-inventory decrease unless
  film mass and transfer/flow evidence are also available.
- No promotion of a family solely because it reduces total liquid mass; the
  result must also show an interpretable change in phase-resolved routing and
  preserved mass/source accounting.

## Candidate experiment families

| Family | Controlled delta | Screening question | Positive signal | Reject / defer signal |
| --- | --- | --- | --- | --- |
| R — roughness | Wall roughness only; EWF off; `C_s=0.5` when active | Does increased wall shear change near-wall liquid direction and reduce phase-2 carryover? | Monotonic or otherwise interpretable change in outer-wall liquid velocity, lower-region delivery, and lower `steamoutlet` liquid flux with preserved closure | Wall scope/readback is not clean, another setting changes, or the response is unresolvable against numerical deterioration |
| E — Eulerian Wall Film | EWF only; roughness `k_s=0` | Does explicit wall-film formation and drainage capture liquid that remains in the bulk near-wall path? | Film mass/transfer evidence shows bulk-to-film capture and downward film flow, accompanied by reduced bulk liquid carryover and preserved vapor audit | Film variables/transfer cannot be exposed, film behaviour is unaccounted for, or apparent benefit is only a global inventory change |

The initial queue is `R0/E0` smooth no-EWF control reference, then R1–R3 and
E1–E2. R4 remains an evidence-gated roughness extension. By direct human
reframe on 2026-09-23, E3 is a selected interaction follow-on: E1 basic EWF
plus R3 roughness, with no phase accretion or additional film-physics option.
Its clean two-factor contrast is E0/E1/R3/E3, judged by the same matched-window
carryover, film, closure, inventory, and solver-health evidence.

The human also selected E2.1 on 2026-09-23 after reviewing the EWF result:
repeat E2's phase-accretion setup from the same verified 5586 parent, changing
only the Fluent maximum film-thickness limit from `0.01 m` to `0.3 m`. Treat
this as an exploratory numerical-limit sensitivity, not a physical film
thickness target. Record maximum and area-weighted film thickness and film
mass every native iteration, with the EWF transfer, outlet, closure, and
solver-health evidence already required for Family E. Its setup and claim
limits are in [E2.1 setup](ewf-family/e2.1/setup.md).

## Decision conditions

The screen is useful only if each child passes parent identity, wall/EWF
readback, paired save/reopen, and instrumentation gates. For a usable
mechanism conclusion, compare the same native windows against the R0 baseline
using:

1. phase-2 liquid flux through `steamoutlet` and its window mean/slope;
2. phase-1 steam flux through `steamoutlet` and mixture outlet flux;
3. total liquid inventory and lower-region liquid inventory/availability;
4. absorber command, native applied phase-2 removal, and command error;
5. source-inclusive phase and mixture closure, including storage when the
   field is moving;
6. residuals, reverse-flow activity, viscosity limiting, AMG/FPE/nonfinite
   events, and checkpoint survival; and
7. family-specific wall trajectory evidence, or EWF film mass and transfer
   evidence where applicable.

A branch can be selected for a longer follow-up when it gives a repeatable,
mechanistically supported reduction in liquid carryover without an
unaccounted source/outlet path and without unacceptable numerical degradation.
If both families fail that test, the result is still a useful negative screen:
the missing mechanism is not established as a roughness/EWF effect inside this
model. Neither outcome authorizes Phase 08 or a plant-performance claim.
