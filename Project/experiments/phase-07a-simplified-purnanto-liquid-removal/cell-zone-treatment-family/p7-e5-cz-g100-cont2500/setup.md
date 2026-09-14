# P7-E5-CZ-G100-CONT2500 — unchanged lower-cell-zone continuation

## Contract

| Field | Value |
| --- | --- |
| Lifecycle | `discovery` bounded continuation |
| Context | [`../../CONTEXT.md`](../../CONTEXT.md) |
| Candidate/origin | `H5`; human-approved continuation direction on 2026-09-10 |
| Gate/design | `G2` E5-CZ cell-zone recovery screen; continuation selected after the three-gain screen |
| Parent | Exact verified G100 active-500 case/data pair from `P7-E5-CZ-G100-student-20260910T045745Z` |
| Controlled delta | Horizon only: continue the existing G100 state for `2,000` additional active iterations, from active `500` to active `2,500` |
| Frozen mesh/topology | Existing G100 split; lower zone `p7-e5-lower-y010`; no remesh, re-split, zone enlargement, or boundary change |
| Frozen source law | Existing G100 `G=1.00` adaptive lower-zone phase-2 source and matched mixture-momentum source |
| Frozen numerical context | G100 parent physics, materials, phases, gravity, inlets, steam outlet, numerics, monitors, and source audit |
| Update cadence | Every `50` active iterations, unchanged from G100 |
| Claim class | Bounded continuation evidence for a computational zone-scoped mechanism; not physical outlet validation or qualification |

## Approved question

> Does the positive liquid-inventory trend observed during the first 500 active
> iterations of G100 persist when the unchanged lower-cell-zone source
> mechanism is continued for 2,000 additional active iterations?

The continuation distinguishes two explanations that the first screen could
not separate:

1. the 500-iteration response is an evolving transient and the lower liquid
   may eventually feed the bottom region and approach a bounded removal state;
2. the source command can increase without producing a meaningful bottom
   liquid transport path, so global inventory drift and open closure persist.

## Prior evidence and nonredundancy

The original G100 screen is complete and provides the verified continuation
parent. It reached active 500/native 1,000 with a late liquid-inventory slope
of approximately `+0.3521 kg/native iteration`, final commanded source near
`95.89 kg/s`, no source saturation, phase-2 liquid boundary outflow near
`0.264 kg/s`, and open boundary-only mixture closure near `0.589`.

This is a `PARTIAL REPEAT` with a single controlled delta: the continuation
horizon. It is nonredundant because the existing 500-iteration screen cannot
show whether the observed drift is persistent over the longer declared window.
No mesh, source, phase model, outlet, or numerical setting is changed here.

## Parent and continuation identity

Load the paired final G100 artifacts from the exact run recorded in
`p7-e5-cz-g100/run-paths.yaml`:

```text
P7-E5-CZ-G100-active500.cas.h5
P7-E5-CZ-G100-active500.dat.h5
```

The continuation must:

- read and verify the paired parent before mutation;
- preserve the already-created `separator-purnanto` and
  `p7-e5-lower-y010` fluid zones;
- not repeat the split operation;
- not reinitialize the field;
- not reset or patch any phase field;
- not change the lower-zone geometric volume or register extent;
- not change the G100 gain, source law, momentum basis, source bounds, or
  update cadence; and
- preserve the existing G100 source/readback and report conventions.

The existing lower zone is a multiphase fluid zone. Both phases may occupy it;
only the phase-2 mass branch is directly source-selective. This continuation
must therefore retain phase-resolved lower-zone inventory and bottom-flux
evidence rather than treating the zone as liquid-only.

## Run intent and horizon

| Segment | Active iterations | Approximate native coordinate | Purpose |
| --- | ---: | ---: | --- |
| Existing parent | `1--500` | `501--1,000` | Retained G100 discovery history and continuation anchor |
| New continuation | `501--2,500` | `1,001--3,000` | Test persistence or relaxation of the inventory/routing trend |
| Final analysis window | `2,001--2,500` | `2,501--3,000` | Primary late-window slope, balance, routing, and residual assessment |

Save durable paired case/data checkpoints at active `750`, `1,000`, `1,250`,
`1,500`, `1,750`, `2,000`, `2,250`, and `2,500`, or at an equivalent cadence
that preserves a recovery pair at least every 250 active iterations. Save and
reopen the final active-2,500 pair before terminal classification.

This is an iteration-based steady-solver continuation, not a claim of 2,000
physical seconds or of a physical transient residence time. The intended
interpretation is bounded numerical evolution under the unchanged G100 setup.

## Adversarial strategy check

| Criterion | Score | Assessment |
| --- | ---: | --- |
| Scientific value | `4/4` | It directly tests the unresolved slow-evolution versus persistent-drift explanation using the strongest clean full-history E5-CZ parent. |
| Evidence and interpretability | `3/4` | The unchanged setup isolates horizon, but the native source is still a uniform zone source and the calculation remains a steady-iteration continuation rather than a physical-time drainage test. |
| Cost-effectiveness | `3/4` | One continuation reuses the verified parent and instrumentation, but 2,000 additional iterations are justified only if the lower-zone, bottom-flux, and balance histories are retained in full. |

Important surviving criticisms are recorded as claim limits rather than hidden
assumptions: a favourable late trend could still be path-dependent, an internal
source is not a physical outlet, and a positive source command does not prove
bottom liquid transport. The strategy is viable as a bounded discovery
continuation and is ready for prerequisite verification after the Phase Loop
launch choice; it is not a qualification strategy.

## Required evidence

### Hard pre-run evidence

- exact G100 active-500 case/data identity and successful readback;
- final fluid-zone names and lower-zone identity;
- unchanged G100 source tree, gain, controller bounds, and update cadence;
- unchanged lower-zone geometric volume and phase-2 inventory basis;
- existing report/residual instrumentation redirected to a continuation-safe
  output location before the first new iteration; and
- continuation checkpoint/autosave paths proven writable and unambiguous.

### Run and terminal evidence

- native residual histories for the full continuation and the new window;
- full solver transcript, warnings, reversed-flow/limiting messages, and last
  valid state;
- controller updates at every 50 active iterations, including active/native
  coordinate, liquid inventory, normalized error, requested/clamped command,
  saturation, source values, lower-zone phase-2 basis, and integrated
  `get_sum` source;
- total liquid inventory and lower-zone liquid inventory/volume histories;
- phase-resolved inlet, steam-outlet, bottom, and user-source balances;
- bottom phase-2 liquid outflow and bottom vapor outflow;
- mixture imbalance and source-accounting diagnostics;
- proof that direct phase-1 mass source remains zero;
- checkpoint identities and final paired case/data identity; and
- final save/reopen readback of the unchanged two-zone topology.

Required evidence must cover the continuation itself and must not be inferred
solely from the original 500-iteration package.

## Core figure plan

| Figure | Question | Plot and basis | Interpretation use |
| --- | --- | --- | --- |
| F1 | Does the G100 inventory trend persist over the longer horizon? | Total continuous-liquid mass versus active iteration `1--2,500`, with original G100 and E0 reference windows clearly separated from the new continuation; fit the final `2,001--2,500` window | Distinguishes persistent positive drift from late flattening or reversal |
| F2 | Does upper liquid feed the lower region and leave through the bottom? | Lower-zone liquid inventory/volume, bottom phase-2 liquid outflow, and bottom vapor outflow over the continuation coordinate | Tests the bottom-only mechanism and separates delayed lower transport from direct domain-wide removal |
| F3 | Is the commanded source still realized and audited? | Requested/clamped command, integrated `get_sum` phase-2 user source, realized phase-2 removal, direct phase-1 source, and saturation state | Distinguishes controller request from realized phase-selective action |
| F4 | Does any apparent improvement survive balance and numerical checks? | Phase/mixture/user-source balance, normalized mixture imbalance, and residual histories with final-window summaries | Rejects source-dominated, vapor-dominated, or numerically deteriorated interpretations |

All figures must preserve raw histories, units, sign conventions, phase/zone
scope, and the distinction between the existing parent window and the new
continuation window.

## Decision gate

### Continue/reconsider signal

The continuation is informative if the late-window evidence shows a clear
change in the lower-region behaviour: lower-zone liquid inventory approaches a
bounded trend, bottom phase-2 liquid outflow becomes materially larger than the
current screen value, total inventory slope moves toward zero or negative, and
vapor loss and source imbalance remain acceptable.

### Weaken/reject signal

The unchanged mechanism is weakened if the final window retains positive total
inventory drift, lower-zone liquid does not establish a meaningful bottom
outflow, the mixture closure remains open, or the source command grows toward
its cap without corresponding liquid transport. That would support moving the
planning discussion toward a distinct bottom collector/outlet or localized
phase-gated mechanism; it would not support patching/resetting or a physical
drainage claim.

### Claim boundary

Even a favourable continuation can establish only that the unchanged native
cell-zone source shows a bounded or unbounded numerical trend over active
iterations `501--2,500` under the declared model. It cannot establish physical
outlet fidelity, plant drainage, mesh independence, steady convergence, or
removal of all upper liquid.

## Completion route

After terminal analysis, return the evidence to the human for the next
mechanism decision. No automatic new geometry, zone enlargement, outlet
change, source law, UDF, patch/reset, qualification run, or additional
continuation is authorized by this setup.
