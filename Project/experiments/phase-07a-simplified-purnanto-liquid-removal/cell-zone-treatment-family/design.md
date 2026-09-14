# Phase 07 E5-CZ cell-zone recovery-family design

## Design authority

| Field | Contract |
| --- | --- |
| Lifecycle | `discovery` |
| Context | [`../CONTEXT.md`](../CONTEXT.md) |
| Candidate | `E5-CZ` / human-approved H4 follow-on direction |
| Gate | `G2 — E5-CZ cell-zone recovery screen` |
| Human approval | Cell-zone split and three-setting follow-on family approved 2026-09-10 |
| Reference | Exact valid E0 iteration-500 case/data pair after the split-by-mark operation |
| Claim class | Comparative numerical mechanism discovery; not physical outlet validation or qualification |

## Discovery question

> Can the blocked E5 liquid-removal concept become an auditable native Fluent
> source mechanism when the supplied single fluid zone is split into a lower
> cell zone, and what does the response to three source gains teach us about
> the usefulness and limits of that mechanism?

The family is deliberately narrower than the completed fixed-mesh campaign. It
holds the split boundary, parent state, source region, source formulation, and
update interval fixed while varying only the gain. The comparison therefore
tests whether the zone split recovers a controllable source route, rather than
confounding source strength with a new geometry or a new mesh.

## Prior evidence and collision check

| Existing evidence | Classification | Why this family is nonredundant |
| --- | --- | --- |
| `P7-E5-PSINK-G025/G050/G100` blocked before solve because the live tree had no register/region binding. | `PARTIAL REPEAT` | The new children bind the source to a genuine lower cell zone; no E5 performance result existed to repeat. |
| Fixed-mesh E0--E4 screens and the G=1.50 recovery screen show finite-horizon inventory and balance behaviour but do not test a native lower-zone source. | `NEW DELTA` | The source is moved from the unavailable region-binding route to a cell-zone-scoped phase source with explicit source accounting. |
| Student-server technical split probe on the inherited G150 recovery pair. | `IMPLEMENTATION EVIDENCE` | It proves the Fluent operation and mesh invariant, but it is not the scientific parent and is not treated as a treatment result. |

The G150 recovery pair is retained only as a technical capability artifact. All
scientific children must be rebuilt from the exact E0 iteration-500 checkpoint
after the split, with matched save/reopen proof.

## Controlled mesh/topology delta

Start from the supplied `Separator-purnanto342k.msh.h5` topology and the exact
E0 iteration-500 case/data checkpoint. Create the same register in every child:

```text
register: p7-e5-cz-lower-y010
min_point: [-2.067034, 0.0, -1.469893]
max_point: [ 1.066950, 0.10, 1.066889]
inside: true
```

Execute Fluent's native `mesh/modify-zones/sep-cell-zone-mark` operation with
`cell_zone_name=separator-purnanto`, `register=p7-e5-cz-lower-y010`, and
`move_faces=true`. Rename the marked child zone to
`p7-e5-lower-y010`; zone IDs remain session-specific and must be recorded from
the live readback. The expected technical result is a parent zone with
`338,815` cells and a lower zone with `3,794` cells, with generated adjacent
face-zone names recorded as part of the topology delta.

The student-server technical comparison already observed identical totals in
the unsplit and split case/data pairs: `342,609` cells, `1,647,633` faces,
`1,046,255` solver nodes, identical domain extents, identical volume and
face-area statistics, and a clean mesh check. Every scientific child must
repeat the relevant readback on its own placed parent. If any invariant fails,
the child is blocked before source setup.

## Native source formulation

The lower zone remains a fluid zone with the same material, phase mapping,
Mixture model, turbulence model, gravity, and numerical settings as the E0
parent. The source delta is restricted to that zone:

- phase-2 mass source: one negative constant SI volumetric source;
- phase-1 mass source: disabled/`none`;
- mixture x/y/z momentum sources: one constant source per component, updated
  with the phase-2 removal command and the lower-zone phase-2 velocity used for
  the momentum-accounting basis;
- no direct vapor mass source, no energy source, no turbulence source, and no
  source in the parent fluid zone; and
- source values, units, signs, active zone, and integrated user-source
  reports must be read back before and during the solve.

For each controller update, use the existing E0-derived inventory law:

```text
M*        = E0 total continuous-liquid mass at native iteration 500
ΔMref     = E0 total continuous-liquid mass at native iteration 1000 - M*
e         = max(0, (Mcurrent - M*) / ΔMref)
u         = clamp(G × 116.92 kg/s × e, 0, 146.15 kg/s)
S_mass    = -u / V_lower   [kg m^-3 s^-1]
S_mom,k   = S_mass × U_phase2,k,lower   [N m^-3]
```

`V_lower` is the geometric volume of `p7-e5-lower-y010`, and
`U_phase2,k,lower` is the explicitly reported lower-zone phase-2 velocity basis
used for the matched mixture-momentum source. If the lower-zone velocity or
integrated source cannot be obtained with enough provenance to audit the
coupling, the child is blocked; a zero-momentum or whole-domain source is not a
silent substitute.

This formulation is intentionally not the old local-cell mass-weighted sink.
Native Fluent cell-zone sources are uniform volumetric values over the selected
zone. The family tests that native, zone-scoped approximation and reports its
momentum limitation explicitly.

## Initial family matrix

| Setup ID | Gain `G` | Command at `e=1` before cap | Only changed family value |
| --- | ---: | ---: | --- |
| `P7-E5-CZ-G025` | `0.25` | `29.23 kg/s` | source gain |
| `P7-E5-CZ-G050` | `0.50` | `58.46 kg/s` | source gain |
| `P7-E5-CZ-G100` | `1.00` | `116.92 kg/s` | source gain |

Each child receives `500` controller-active steady iterations, including a
`50`-iteration smoke segment, with updates every `50` active iterations.
Children begin from the same split, source-off E0 iteration-500 checkpoint.
The run is a discovery screen, not a steady-state or qualification test.

## Required evidence

Hard pre-run evidence:

- exact E0 checkpoint identity and parent readback;
- register readback and marked-cell count;
- split command/readback, source and lower-zone names/IDs, generated face
  zones, and unsplit/split mesh-invariant comparison;
- lower-zone geometric volume and phase-2 activation inventory;
- source-tree readback showing phase-2 mass only in the lower zone and mixture
  momentum sources only in that zone;
- source sign, SI units, source values, update interval, gain, bounds, and
  `M*`/`ΔMref` provenance;
- phase-1 mass, direct phase-1/phase-2 energy, turbulence, and parent-zone
  sources read back as disabled or `none`; and
- save/reopen and 50-iteration smoke proof before accepting the child.

Run evidence:

- native residual histories and full transcript;
- controller updates: native/active iteration, `Mcurrent`, `M*`, `ΔMref`,
  normalized error, requested/clamped command, saturation, lower-zone phase-2
  mass source, mixture momentum source, integrated user sources, and realized
  phase removal;
- total liquid inventory and lower-zone inventory;
- phase-resolved inlet, steam-outlet, bottom, and user-source mass balances;
- bottom vapor discharge normalized by the `80.69 kg/s` reference vapor inlet;
- mesh/source warnings, reversed flow, limiting, divergence, and last-valid
  state; and
- checkpoint/final case-data identity with save/reopen verification.

## Core figure plan

| Figure | Question | Plot and basis | Interpretation use |
| --- | --- | --- | --- |
| F1 | Does the zone-source family change liquid inventory behaviour? | Total continuous-liquid mass vs controller-active iteration for the three gains, with matched E0 500--1,000 window and final 401--500 window summaries. | Distinguishes persistent inventory response from an endpoint effect. |
| F2 | Is the commanded source actually realized in the intended phase? | Requested/clamped command, integrated phase-2 user source, realized phase-2 removal, saturation, and direct phase-1 source on the controller-update coordinate. | Distinguishes actuator response from merely requested removal and exposes vapor contamination. |
| F3 | Does apparent improvement survive conservation and numerical checks? | Liquid, vapor, mixture, and user-source net balances with bottom vapor-loss history and native residuals as supporting panels. | Separates useful liquid removal from source-dominated closure, vapor loss, or numerical failure. |

## Adversarial review

| Criterion | Score | Assessment |
| --- | ---: | --- |
| Scientific value | `4/4` | It directly removes the old E5 capability blocker and isolates gain sensitivity while keeping the split region fixed. |
| Evidence and interpretability | `3/4` | Zone-level mass is auditable, but native momentum is mixture-level and uniform; the limitation is material and is included in the claim boundary. |
| Cost-effectiveness | `4/4` | Three short children reuse one split parent and the existing adaptive evidence package; the family is substantially cheaper than another geometry campaign. |

Strongest criticisms and disposition:

- **Important:** splitting creates new adjacent face zones and can change cell
  type/storage bookkeeping even when total mesh metrics are unchanged. Record
  the topology delta and repeat the unsplit/split checks for the scientific
  parent.
- **Important:** native zone sources are uniform volumetric terms, so this is
  not equivalent to a local-cell mass-weighted UDF. Report the mismatch and do
  not make the stronger claim.
- **Important:** Fluent exposes phase-specific mass but mixture-level momentum
  in this Mixture setup. The lower-zone phase-2 velocity basis and integrated
  mixture momentum source are hard evidence requirements; missing coupling
  blocks the child.
- **Minor:** steady iteration is not physical time. Inventory slopes are
  numerical progression metrics and must not be called physical accumulation
  rates.

Disposition: viable for the `G2` discovery-design gate and the phase-planner
launch decision. No long run, qualification path, UDF, remesh, or patch/reset
route is authorized by this design.

## G2 decision rule

Classify all three gains before any continuation. A gain is valid only if the
split/source/readback/smoke/evidence gates pass. A continuation to at most one
member and `2,000` controller-active iterations is allowed only when one valid
member is clearly preferable by persistent liquid-inventory/balance response,
lower vapor loss, predominantly liquid removal, and no source inconsistency,
saturation, oscillation, or numerical failure. If the gains trade liquid
improvement against vapor loss without a clear dominant setting, return the
comparison as unresolved. No result from this discovery family establishes
steady convergence, physical outlet fidelity, mesh independence, or plant
drainage performance.
