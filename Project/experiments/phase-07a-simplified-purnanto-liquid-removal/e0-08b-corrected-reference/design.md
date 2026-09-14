# E0 experiment design — corrected 08b-derived reference

## Design identity

| Field | Value |
| --- | --- |
| Phase | Phase 07 — simplified Purnanto liquid-removal mechanisms |
| Lifecycle mode | `discovery` |
| Approved candidate | `E0` |
| Origin | H2 reference implied by the human-selected fixed-mesh comparison |
| Human approval | Approved 2026-09-08 |
| Context authority | [`../CONTEXT.md`](../CONTEXT.md), setup-preparation gate `G0`; later comparison gate `G1` |
| Design purpose | Establish the corrected, instrumented wall-bottom reference against which later human-approved removal treatments can be compared |

## Uncertainty being reduced

The supplied Phase-07 mesh has the intended truncated Purnanto geometry, but
its discrete mesh differs substantially from the historical 08b mesh and its
steam-outlet diameter corrects the former Project value from `0.724 m` to
`0.876 m`. The project does not yet know the new case's natural liquid-
inventory buildup, phase-mass imbalance, or numerical-history scale.

E0 asks:

> Can an 08b-derived carrier setup, reconciled onto the supplied mesh with a
> non-draining bottom wall and corrected steam-outlet scale, produce a valid
> and sufficiently repeatable `2,000`-iteration reference history for later
> fixed-mesh liquid-removal comparisons?

E0 does not ask whether the wall-bottom model reaches liquid mass closure.
Continued liquid accumulation may be the reference result.

## Prior-experiment collision check

| Prior work | Collision class | Existing result | Why E0 remains informative |
| --- | --- | --- | --- |
| Setup 07 professional-mesh baseline | `PARTIAL REPEAT` | Cutoff bottom accepted as a wall; endpoint steam-carryover flux was reported, but lower liquid closure was intentionally out of scope. | E0 uses the new mesh, corrected outlet scale, and predeclared inventory/balance histories. |
| Setup 08b 5,000-iteration saved field | `PARTIAL REPEAT` | Historical endpoint reported `116.063719 kg/s` mixture imbalance and `0.587337` imbalance ratio, with only small steam-line liquid carryover. | The old report lacks a matched complete inventory and residual history on this mesh and cannot establish the new reference slope. |
| Phase-05 outlet-characterization work | `PARTIAL REPEAT` by diagnostic theme | Full-geometry outlet cases measured inventory and phase routing; stable anchors over-drained an initialized pool. | Different geometry and initial-condition question; useful for instrumentation lessons, not a substitute for E0. |
| Phase-06 pool-control work | `PARTIAL REPEAT` by inventory question | Full-geometry steady surrogates did not establish a controlled pool state. | Phase 07 deliberately changes to the simpler truncated geometry and first needs its own fixed-mesh reference. |

Novelty classification: **`PARTIAL REPEAT`**, scientifically nonredundant
because the new mesh, corrected outlet length scale, exact parent readback,
and complete trend evidence form the controlled delta.

## Question-experiment challenge

### Three-criterion assessment

| Criterion | Score | Assessment |
| --- | ---: | --- |
| Scientific value | `4/4` | Later outlet-treatment effects cannot be interpreted without the matched wall-bottom buildup and imbalance scale. |
| Evidence and interpretability | `3/4` | Strong if all histories are instrumented before initialization; limited because historical 08b evidence is chiefly an endpoint rather than a matched history. |
| Cost-effectiveness | `4/4` | One `2,000`-iteration run on a 342,609-cell mesh is a proportionate discovery reference with a conditional extension instead of an automatic long run. |

### Strongest criticisms and dispositions

- **Important — parent ambiguity:** the supplied case has previously been
  reported as carrying six one-way DPM injections rather than the broader
  nine-bin payload described in the 08b narrative. E0 concerns the continuous
  Mixture carrier field. The exact DPM state must be read back, interaction
  with the continuous phase must remain off, and no DPM update or DPM result
  may count as E0 evidence. If DPM coupling is active, setup validity fails.
- **Important — mesh replacement may lose or mis-map settings:** every model,
  material, phase, boundary, solver, initialization, and report dependency
  must be reconciled and read back. Filename similarity is insufficient.
- **Important — initialization can control early inventory behavior:** use the
  parent-defined initialization method when it survives authoritative
  readback. If it cannot be proven after mesh reconciliation, return upstream
  rather than silently select a different method.
- **Important — 2,000 iterations may not establish a stable slope:** compare
  adjacent late windows. A stable positive buildup slope is usable; an
  evolving or noise-dominated slope is inconclusive and may justify only a
  human-reviewed continuation of unchanged E0.
- **Minor — historical 08b is not a matched comparator:** use its reported
  endpoint fluxes only as contextual reasonableness checks, not pass/fail
  tolerances or proof of parity.

Disposition: **viable for E0 setup preparation under G0**, subject to the hard
pre-run instrumentation and readback requirements below. This design does not
by itself satisfy the later G1 contrastive-screen gate or authorize loop entry.

## Exact artifacts and controlled delta

### Parent candidate

| Item | Identity |
| --- | --- |
| Fluent case | `TwoPhaseInletV2(Purnanto).cas.h5` |
| Size | `243,137,956 bytes` |
| SHA-256 | `b75a69dcad7da29fa9576c15d478a187798029b51d45ac773a265ecdf146ae56` |
| Status | Exact candidate identified; 08b carrier settings require live Fluent proof |

### Replacement mesh

| Item | Identity |
| --- | --- |
| Fluent mesh | `Separator-purnanto342k.msh.h5` |
| Size | `40,685,983 bytes` |
| SHA-256 | `59b7cf3bcf1cf0266587d4b98f8c6d67bbca007a4381ceb16a05fd8728b37801` |
| Structural state | 342,609 cells; one fluid zone; `liquidinlet`, `steaminlet`, `steamoutlet`, and planar `bottom` zones verified locally |

The only declared changes from the carrier parent are:

1. replace the old discrete mesh with the exact supplied Phase-07 mesh;
2. map the split inlets, steam outlet, walls, and cell zone onto the new zones;
3. retain `bottom` as a stationary, no-slip, non-draining wall;
4. set and verify the steam-outlet turbulence/backflow hydraulic diameter as
   `0.875936 m` (`≈0.876 m`) instead of historical `0.724 m`;
5. add E0's file-backed evidence package; and
6. initialize and run exactly `2,000` iterations from the prepared E0 state.

No bottom opening, outlet, sink, source, withdrawal function, controller,
geometry edit, model-form change, or unapproved numerical tuning is permitted.

## Frozen comparison context

Subject to authoritative live readback of the parent, E0 preserves:

- pressure-based steady solver;
- Mixture model with two continuous phases;
- RNG `k-epsilon`, standard wall treatment, differential viscosity, and
  swirl-dominated-flow setting;
- energy and species off;
- parent phase materials and properties;
- gravity, operating pressure/density method, and reference values;
- split-inlet target phase flows of `116.92 kg/s` liquid and `80.69 kg/s`
  vapor, with phase purity and turbulence conditions reconciled to the new
  inlet zones;
- steam-outlet pressure and total-pressure backflow specification, except for
  the declared corrected hydraulic diameter;
- parent pressure–velocity coupling, discretization schemes, relaxation/
  pseudo-time controls, and convergence controls;
- parent-defined initialization method; and
- one-way/inactive-for-carrier DPM state, with no DPM update included in E0.

Any unplanned mismatch that cannot be repaired without changing this contract
returns to the human; it is not absorbed as an implementation convenience.

## Run intent and horizon

- Run mode: attached discovery execution under `scientific-phase-loop` after
  the required lifecycle and implementation gates pass.
- Initialization: initialize once from the save/reopen-proven prepared E0 case
  using the proven parent-defined initialization method.
- Total horizon: exactly `2,000` solver iterations after initialization. A
  50-iteration smoke is included in this total, not added on top.
- Smoke gate: iterations `1–50`; reports and native residual rows must appear,
  inlet directions must be correct, and no solver divergence or invalid field
  may occur before continuation.
- Development interval: iterations `51–999`.
- Comparison windows: `1,000–1,500` and `1,500–2,000`.
- Primary late window: final `500` iterations.
- Checkpoints: prepared case before initialization; initialized case/data;
  smoke case/data at iteration 50; paired case/data at iterations 500, 1,000,
  1,500, and 2,000; preserve the final pair and all file-backed histories.
- Continuation: no automatic extension. If adjacent late-window slopes are
  materially inconsistent or noise-dominated, report E0 as inconclusive and
  return for approval of an unchanged continuation, normally 1,000 iterations.

## Derived quantities and sign convention

Preserve Fluent's raw reported signs. For comparison plots and tables also
derive a declared engineering convention:

- inlet magnitude is positive into the domain;
- outlet magnitude is positive out of the domain;
- liquid net accumulation rate is liquid inflow minus liquid discharge through
  `steamoutlet` and `bottom`;
- vapor net accumulation rate is vapor inflow minus vapor discharge through
  `steamoutlet` and `bottom`;
- mixture net accumulation rate is total inflow minus total discharge;
- normalized mixture imbalance divides the absolute mixture net rate by
  `197.61 kg/s` nominal mixture inflow;
- normalized bottom vapor loss divides bottom vapor discharge by `80.69 kg/s`.

For E0, `bottom` is a wall and its phase fluxes should be zero. They are still
included in the report contract to establish a structurally matched baseline
for later bottom-boundary candidates.

Inventory is the domain integral of continuous liquid mass. Also retain the
continuous-liquid volume integral when Fluent exposes it reliably. Linear
least-squares slopes over both declared 500-iteration windows are derived
after the run; raw histories remain primary evidence.

## Required pre-run instrumentation

The following are hard requirements and may not be reconstructed from a final
endpoint alone:

- native-coordinate scaled residual histories for every active solved
  equation, captured durably from the Fluent transcript or a separately
  verified file-backed path;
- total-domain continuous-liquid mass history and, when available, volume;
- phase-resolved mass-flow histories for liquid and vapor on `liquidinlet`,
  `steaminlet`, `steamoutlet`, and `bottom`;
- mixture mass-flow histories on the same four boundaries;
- derived liquid, vapor, and mixture net-rate/imbalance histories;
- steam-outlet liquid carryover and vapor recovery histories;
- bottom liquid discharge and normalized bottom vapor-loss histories, even
  though both should be zero for the E0 wall;
- report-file native iteration coordinates spanning the full 2,000-iteration
  run, including smoke;
- solver transcript, setup/readback manifest, checkpoint manifest, and exact
  final artifact identities.

Missing any inventory, phase-flux, mixture-balance, or residual history makes
E0 invalid for the discovery gate.

## Supporting evidence

- Fluent mesh check and solver-side mesh quality, including cell count, zone
  map, minimum orthogonal quality, maximum skewness/aspect ratio when exposed,
  and cell-volume range;
- pressure and velocity reasonableness at the inlets and steam outlet;
- final liquid-volume-fraction contour on a declared central plane and/or
  exterior boundary rendering to show where retained liquid resides;
- comparison of final flux magnitudes against historical 08b endpoint values,
  labelled unmatched and contextual only; and
- readback of DPM interaction/injection state to prove that it does not affect
  the continuous carrier solve.

## Core figure plan

### F1 — E0 liquid-inventory reference

| Field | Contract |
| --- | --- |
| Question | Does the wall-bottom E0 case provide a measurable and sufficiently repeatable liquid-buildup reference? |
| Plot | Raw total-domain continuous-liquid mass history with separate fitted lines over iterations `1,000–1,500` and `1,500–2,000` |
| X-axis | Native solver iteration, `1–2,000` |
| Y-axis | Continuous-liquid mass `[kg]`; optional companion liquid volume `[m³]` |
| Series | Raw E0 history and the two explicitly labelled window fits |
| Comparison basis | Adjacent 500-iteration windows within E0 |
| Reduction | Raw history plus least-squares slope `[kg/iteration]` for each window |
| Data source | Pre-run total-domain liquid inventory report file |
| Instrumentation | Hard requirement before initialization |
| Interpretation use | Similar late-window slopes support use as a reference even when positive; changing/noise-dominated slopes make the reference inconclusive. |

### F2 — Phase routing and closure

| Field | Contract |
| --- | --- |
| Question | Is the inventory trend consistent with the measured phase-resolved boundary fluxes and mixture imbalance? |
| Plot | Aligned histories of normalized liquid inflow/outflow/net rate, vapor inflow/outflow/net rate, and mixture imbalance |
| X-axis | Native solver iteration, `1–2,000` |
| Y-axis | Mass rate `[kg/s]`; normalized mixture imbalance `[-]` in a separate aligned panel |
| Series | Both inlets, steam outlet, bottom, and derived net histories with phase labels |
| Comparison basis | Nominal `116.92 kg/s` liquid, `80.69 kg/s` vapor, and `197.61 kg/s` mixture inflows |
| Reduction | Raw histories plus final-500 mean, range, and slope where meaningful |
| Data source | Pre-run phase and mixture boundary report files |
| Instrumentation | Hard requirement before initialization |
| Interpretation use | Tests whether apparent inventory buildup agrees with conservation evidence and exposes routing or sign errors. |

### F3 — Numerical adequacy

| Field | Contract |
| --- | --- |
| Question | Are E0's inventory and balance trends numerically credible enough for later matched comparisons? |
| Plot | Log-scale native scaled-residual histories aligned with a mixture-imbalance history panel |
| X-axis | Native solver iteration, `1–2,000` |
| Y-axis | Scaled residual `[-]`; mixture net rate `[kg/s]` or normalized imbalance `[-]` |
| Series | Every active solved equation plus E0 mixture imbalance |
| Comparison basis | Full history and final 500 iterations |
| Reduction | Raw histories; final-window mean/range and qualitative trend classification |
| Data source | Verified transcript/file-backed residual capture and mixture reports |
| Instrumentation | Hard requirement before initialization; endpoint residuals are insufficient |
| Interpretation use | Distinguishes a physically informative accumulation reference from solver deterioration or incomplete numerical development. |

## Decision outcome after E0

E0 is a usable reference when its setup and execution are valid and its late
histories define a repeatable enough scale for comparing an approved removal
treatment. It may have a large positive liquid buildup or mixture imbalance.

E0 is inconclusive when the late inventory/balance histories remain strongly
evolving or too noisy to define a reference slope. The only permitted
continuation is a human-reviewed extension of unchanged E0.

E0 is invalid when artifact identity, zone mapping, setup readback,
save/reopen, smoke, residual capture, inventory capture, or phase-flux capture
fails. An invalid E0 produces no scientific baseline and permits repair of the
same approved experiment only.

## Claim limit

E0 can establish only the numerical reference behavior of the declared
corrected simplified model. It cannot establish steady mass convergence,
physical brine drainage, validated outlet behavior, mesh independence,
plant-level control, or exact parity with the historical 08b case.
