# Phase 07 E5-CZ absorber-control family design

## Design authority

| Field | Contract |
| --- | --- |
| Lifecycle | `discovery` |
| Context | [`../CONTEXT.md`](../CONTEXT.md) |
| Candidate | `E5-CZ-ABSORB` / human-approved H6 absorber-control extension |
| Gate | `G3 — lower-inventory absorber-capacity screen` |
| Human approval | New family and recommended design approved by the human on 2026-09-10 |
| Parent | Exact verified `P7-E5-CZ-G100-CONT2500` active-2,500 case/data pair |
| Claim class | Comparative numerical absorber-mechanism discovery; not physical brine-pool validation or qualification |

## Discovery question

> Can the no-outlet lower-zone absorber pull accumulated liquid toward a bounded
> numerical pool target when its command is driven by lower-zone phase-2
> inventory and its source-capacity limit is varied independently?

The family addresses the specific uncertainty left by the G100 continuation:
the previous controller used total separator liquid inventory and reached the
`146.15 kg/s` command cap. The new family retains the intended numerical
brine-pool abstraction and changes the feedback basis to the liquid inventory
inside the lower absorbing region. It fixes `G=2.00` and varies only the
predeclared source cap, so the child comparison isolates available absorber
capacity rather than mixing gain and cap changes.

## Prior evidence and collision check

| Existing evidence | Classification | Why this family is nonredundant |
| --- | --- | --- |
| `P7-E5-CZ-G025/G050/G100` | `PARTIAL REPEAT` | Those children used the original total-separator-inventory law, `G≤1.00`, and the `146.15 kg/s` cap; they did not test lower-zone feedback or the new cap ladder. |
| `P7-E5-CZ-G100-CONT2500` | `NEW CONTROL DELTA` | The continuation reached active 2,500 but preserved the old total-inventory controller and cap. Its positive inventory drift identifies the saturation/control uncertainty rather than resolving it. |
| Fixed-mesh E4/E5 screens | `COMPARISON CONTEXT` | They show adaptive and phase-selective source limitations but do not provide an auditable native lower-zone absorber with this local feedback law. |
| Conventional outlet families | `DIFFERENT MECHANISM` | They remain historical comparisons only; this family deliberately does not introduce a bottom boundary outlet. |

## Common parent and topology

Each child must start from the exact final pair produced by:

`P7-E5-CZ-G100-CONT2500-student-20260910T070332Z`

The parent is active `2,500`, approximately native `3,000`, with the final
paired case/data paths recorded in the completed continuation
[run-paths.yaml](../cell-zone-treatment-family/p7-e5-cz-g100-cont2500/run-paths.yaml).
The continuation report package records a stale post-reopen runtime-counter
field (`current_iteration: 1556`) even though the final report/residual extent
reaches native `3,000`; this is a hard pre-run readback limitation. Each child
must reopen the parent, prove the topology/source state, and record the live
iteration/readback discrepancy before proceeding. If the parent cannot be
proven, the child is blocked and no substitute parent may be chosen silently.

The topology is frozen:

- fluid zones: `separator-purnanto` and `p7-e5-lower-y010`;
- lower-zone register: `0 ≤ y ≤ 0.10 m`;
- expected lower-zone cell count: `3,794`;
- expected parent-zone cell count: `338,815`;
- expected total cells/faces/solver nodes: `342,609` / `1,647,633` /
  `1,046,255`;
- lower-zone geometric volume must be read back rather than copied; and
- no re-split, remesh, reinitialize, zone enlargement, outlet change, or
  boundary-condition change is permitted.

## Controlled source and controller delta

The child source formulation remains a native lower-zone source:

- lower-zone phase-2 mass source: one negative uniform SI volumetric source;
- direct phase-1 mass source: disabled/`none`;
- lower-zone mixture x/y/z momentum sources: matched to the phase-2 removal
  command and the read-back lower-zone phase-2 velocity basis;
- no parent-zone source, direct vapor mass source, energy source, turbulence
  source, or UDF;
- integrated phase-2 source audit through Fluent `get_sum` is required; and
- source sign, units, active zone, and source tree are read back before the
  first solve and at every controller update.

The local feedback rule is defined from the child-parent readback:

```text
M_L0       = lower-zone phase-2 mass at the active-2,500 parent state
M_L,target = 0.50 × M_L0
e_L        = max(0, (M_L - M_L,target) / M_L,target)
Q_cmd      = clamp(2.00 × 116.92 kg/s × e_L, 0, Q_cap)
S_mass     = -Q_cmd / V_lower                         [kg m^-3 s^-1]
S_mom,k    = S_mass × U_phase2,k,lower                [N m^-3]
```

`M_L,target` is a numerical absorber target, not a real separator level or a
claim about the physical brine surface. The `0.50` factor is an explicit
planning assumption and must be recorded in the manifest and results report.
If the parent lower-zone mass is non-positive, unavailable, or not reproducible
after reopen, the child is blocked before solving. The target is not changed
post hoc after seeing the child result.

The command is updated every `50` controller-active iterations. The lower zone
is allowed to contain both phases; only the direct phase-2 mass source is
source-selective. The zero direct phase-1 source is required, but the
mixture-level momentum source may still influence the shared carrier solution,
so vapor response must be measured rather than assumed to be unchanged.

## Initial family matrix

| Setup ID | Gain `G` | Source cap `Q_cap` | Controlled child difference |
| --- | ---: | ---: | --- |
| `P7-E5-CZ-ABSORB-G200-CAP14615` | `2.00` | `146.15 kg/s` | cap level |
| `P7-E5-CZ-ABSORB-G200-CAP29230` | `2.00` | `292.30 kg/s` | cap level |
| `P7-E5-CZ-ABSORB-G200-CAP58460` | `2.00` | `584.60 kg/s` | cap level |

The caps are respectively one, two, and four times the prior G100 cap. They
are a bounded numerical stress ladder, not real plant capacities. Each child
receives `500` controller-active discovery iterations, including a
`50`-iteration smoke segment, with updates every `50` iterations. The children
are matched continuations from the same active-2,500 parent.

## Required evidence

### Hard pre-run evidence

- exact parent case/data identity and remote existence;
- parent reopen, topology, mesh counts, lower-zone name, geometric volume,
  source tree, and current-iteration readback;
- explicit record of the stale/inconsistent parent runtime-counter field and
  the authoritative history/iteration basis selected for the child;
- parent lower-zone phase-2 mass `M_L0`, target mass, target rule, and liquid
  density provenance;
- nested monitoring registers or report locations for the lower absorber,
  immediately adjacent band, and any broader lower-half diagnostic band;
- phase-2 mass source, phase-1 source-off, mixture-momentum source, signs,
  units, `G`, `Q_cap`, and `50`-iteration update cadence;
- report histories for total liquid mass, lower-zone phase-2 mass and volume,
  nested lower bands, vapor inventory/flux, phase/mixture balances, and
  residuals; and
- save/reopen plus a `50`-iteration smoke check before accepting the child.

### Run evidence

- controller events with active/native iteration, `M_L`, `M_L0`, target,
  normalized local error, requested/clamped command, cap, saturation,
  phase-2 source density, mixture-momentum sources, and `get_sum` audit;
- total liquid inventory and all nested lower-region inventories;
- direct phase-1 source state and vapor inventory/flux histories;
- phase-resolved inlet, steam-outlet, treated-bottom, and user-source balances;
- mixture boundary balance and continuity/phase residual histories;
- reversed-flow, turbulent-viscosity limiting, divergence, and other solver
  warnings;
- paired checkpoints at active `0`, `100`, `250`, and `500` after child start;
  and
- final child case/data save, reopen, source/topology readback, and manifest.

## Core figure plan

| Figure | Question | Plot and comparison basis | Interpretation use |
| --- | --- | --- | --- |
| F1 | Does local absorber control reduce liquid buildup? | Total liquid mass plus lower-zone and nested-band phase-2 inventories versus child active iteration for all three caps; show target band and parent anchor. | Distinguishes global drift from local pull-down and bounded lower-region response. |
| F2 | Does higher capacity change the command/realization relationship? | Local inventory error, requested/clamped command, cap/saturation state, integrated phase-2 source, and direct phase-1 source on the controller-update coordinate. | Distinguishes cap limitation from source non-realization or controller failure. |
| F3 | Does the apparent absorber response preserve phase and numerical credibility? | Phase/mix/user-source balances, vapor inventory/flux, bottom vapor-loss ratio, and residual/warning summary over the same child window. | Separates liquid-selective numerical disappearance from vapor disturbance, open closure, or solver pathology. |

## Decision gate G3

Classify all three children before any continuation. A child is useful for
comparison only if its parent/topology/source/smoke/evidence gates pass.

**Continue to a separate human decision** if one cap produces a materially
lower late total-inventory slope, lower-region inventory remains bounded near
the declared numerical target band, the command is not saturated for most of
the window, direct phase-1 mass source remains zero, vapor response is
acceptable, and the source/momentum audit is complete.

**Return to the human without continuation** if all caps retain positive global
and local drift, if the lower-region inventory rebounds without bound, if the
cap ladder only changes source stiffness, if vapor is materially disturbed, or
if the balance remains source-dominated/open without a clear ranking.

No result from this family may establish physical brine-pool level control,
physical outlet fidelity, steady convergence, mesh independence, or plant
drainage performance. A successful discovery child would authorize only a
named human decision about a bounded continuation or a revised absorber
control direction; it cannot originate an outlet, patch/reset, UDF, remesh, or
qualification run.

## Adversarial design review

| Criterion | Score | Assessment |
| --- | ---: | --- |
| Scientific value | `4/4` | Directly tests the unresolved cap/control explanation identified by G100 while preserving the user's no-outlet abstraction. |
| Evidence and interpretability | `3/4` | The fixed gain/cap contrast is interpretable, but the parent runtime-counter limitation, open closure, and mixture-level momentum coupling remain material claim limits. |
| Cost-effectiveness | `3/4` | Three 500-iteration continuations reuse one parent and one topology, but the highest cap may cause stiffness or early blocking. |

Surviving issues and disposition:

- **Important:** `M_L,target = 0.50 M_L0` is a numerical assumption, not a
  measured pool level. It is fixed before each child and must remain visible in
  the claim boundary.
- **Important:** a high cap may destabilize Fluent before it teaches capacity.
  The `50`-iteration smoke, warning capture, and paired recovery checkpoints
  are hard requirements; a blocked high-cap child remains a bounded numerical
  result, not evidence that the absorber concept is physically impossible.
- **Important:** the parent runtime counter is stale in the completed package.
  Fresh reopen/readback is mandatory, and histories—not the stale snapshot—must
  be identified as the authoritative continuation coordinate.
- **Important:** zero direct phase-1 source does not make vapor dynamically
  transparent because the matched momentum source is mixture-level. Vapor and
  balance evidence remain required.
- **Non-issue:** zero bottom phase-2 boundary flux is not a rejection signal
  for this volumetric absorber abstraction.

Disposition: viable for discovery setup creation and a later Phase Loop launch
decision. No Fluent run is authorized by this design record alone.
