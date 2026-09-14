# E0 setup — corrected 08b-derived wall-bottom reference

## Setup authority and lifecycle

| Field | Contract |
| --- | --- |
| Setup ID | `P7-E0-REF` |
| Lifecycle mode | `discovery` reference |
| Phase context | [`../CONTEXT.md`](../CONTEXT.md) |
| Approved candidate | `E0`, originating from the H2 fixed-mesh comparison |
| Decision gate | `G0` authorizes this server-neutral setup record; later treatment comparisons use `G1` |
| Human approval | E0 approved 2026-09-08; initial horizon of 2,000 iterations accepted |
| Design record | [`design.md`](design.md) |
| Lifecycle verification | [`../phase-state.yaml`](../phase-state.yaml): `DISCOVERY_DESIGN = PASS`, scope `G0_server_neutral_setup_creation_only` |
| Execution status | **Not authorized.** Treatment-series planning and later loop-entry verification must occur first. |

## Scientific question

> Can an 08b-derived carrier setup, reconciled onto the supplied Phase-07 mesh
> with a non-draining bottom wall and corrected steam-outlet scale, produce a
> valid and sufficiently repeatable 2,000-iteration reference history for
> later fixed-mesh liquid-removal comparisons?

E0 establishes the natural liquid-inventory buildup and imbalance scale. It
does not test a removal treatment and is not required to approach zero liquid-
inventory slope.

## Why this setup exists

Earlier setup 07 and 08b evidence showed that truncated Purnanto wall-bottom
cases can retain a large liquid/mixture imbalance, but the retained records do
not provide a matched, complete inventory and residual history on this new
mesh. E0 is therefore a `PARTIAL REPEAT`, not a claim of a wholly new model.
Its value is the controlled combination of:

- the exact supplied 342,609-cell mesh;
- the human-corrected `0.876 m` steam-outlet geometry;
- exact parent-case identification and live settings reconciliation;
- complete file-backed inventory, phase-routing, balance, and residual
  histories; and
- predeclared adjacent late-window comparisons.

The historical 08b 5,000-iteration endpoint is contextual only. It is not a
matched pass/fail target for E0.

## Exact server-neutral artifact identities

### Settings parent candidate

| Item | Required identity |
| --- | --- |
| Filename | `TwoPhaseInletV2(Purnanto).cas.h5` |
| Size | `243,137,956 bytes` |
| SHA-256 | `b75a69dcad7da29fa9576c15d478a187798029b51d45ac773a265ecdf146ae56` |
| Role | Source of the 08b-derived carrier physics, materials, boundaries, numerics, and initialization configuration |
| Qualification | Candidate identity is proven locally; its settings must be proven by Fluent readback before use |

### Geometry/mesh source

| Item | Required identity |
| --- | --- |
| Filename | `Separator-purnanto342k.msh.h5` |
| Size | `40,685,983 bytes` |
| SHA-256 | `59b7cf3bcf1cf0266587d4b98f8c6d67bbca007a4381ceb16a05fd8728b37801` |
| Units | `m` |
| Stored mesh count | `342,609` cells, `1,077,053` nodes, `1,647,633` faces |
| Fluid cell zone | `separator-purnanto` |
| Boundary zones | `liquidinlet`, `steaminlet`, `steamoutlet`, `bottom`, `wall`, `separator-purnanto:1` |
| Mesh evidence | [`../mesh-inspection.md`](../mesh-inspection.md) |

Machine-specific paths and server placement belong in `run-paths.yaml`, not in
this setup contract.

## Intentional change budget

Only the following changes from the parent carrier case are allowed:

1. replace the parent's discrete mesh with the exact Phase-07 mesh;
2. reconcile the parent cell-zone and boundary settings to the new named zones;
3. retain `bottom` as a stationary, no-slip, non-draining wall;
4. correct the `steamoutlet` turbulence/backflow hydraulic diameter from the
   historically configured `0.724 m` to **`0.875936 m`** (`≈0.876 m`);
5. create the required E0 report, residual, checkpoint, and manifest package;
6. initialize once using the proven parent-defined initialization method; and
7. run the prepared case for a total of 2,000 iterations when execution is
   separately authorized.

No bottom opening, outlet, porous jump, momentum loss, sink/source,
withdrawal law, feedback function, geometry edit, model-form change, or
unapproved numerical tuning is permitted in E0.

## Required parent readback before mutation

Load the exact parent case in a controlled session and export/read back at
least:

- Fluent version and dimensionality;
- pressure-based and steady solver state;
- Mixture model, phase count, primary/secondary phase identities, and phase
  material assignments;
- energy, species, viscous, and DPM model states;
- RNG `k-epsilon` options, including wall treatment, differential-viscosity,
  and swirl-dominated-flow settings;
- all used fluid and particle materials and their property definitions;
- gravity, operating pressure, operating-density method, reference pressure
  location, and reference values;
- inlet types, phase mass-flow targets, phase fractions/purity, flow direction,
  temperature state where active, and turbulence specification;
- steam-outlet pressure, backflow pressure specification, backflow phase
  fractions, and turbulence specification;
- cell-zone state and all wall states;
- pressure–velocity coupling, spatial discretization, gradient method,
  relaxation/pseudo-time controls, and convergence/monitor settings;
- initialization method and any parent initialization options/patch flags; and
- DPM interaction state and exact inherited injection inventory.

The known historical parent interpretation is pressure-based steady Mixture,
two continuous phases, RNG `k-epsilon`, energy/species off, gravity active,
split mass-flow inlets targeting `116.92 kg/s` liquid and `80.69 kg/s` vapor,
and a `1,120,000 Pa` steam-outlet pressure with Total Pressure backflow
specification. These values guide the audit but do not replace live readback.

If the supplied artifact materially disagrees with that carrier definition,
stop and return to the human. Do not silently reconstruct a different parent.

## Required reconciled E0 state

### General and continuous models

| Setting | Required E0 state |
| --- | --- |
| Solver | Pressure-based, steady |
| Multiphase | Mixture, two continuous phases |
| Turbulence | RNG `k-epsilon`; preserve proven parent options |
| Energy | Off |
| Species | Off |
| Gravity and operating conditions | Preserve proven parent values exactly |
| Materials and phase mapping | Preserve proven parent definitions exactly |
| Numerics | Preserve proven parent pressure–velocity, discretization, gradient, relaxation/pseudo-time, and convergence settings |

### DPM isolation

The supplied parent has previously been reported as containing six active
one-way injections totaling `29.22 kg/s`, rather than the broader nine-bin
payload in the narrative 08b record. E0 does not use DPM evidence.

- Read back and record the exact injection state.
- Continuous-phase interaction/source updates must be **Off**.
- Do not execute `dpm-update`, tracking, sampling, or injection modification.
- Do not include DPM mass in E0's continuous-phase closure.
- If DPM coupling is active or cannot be proven inactive, setup validation
  fails before initialization.

### Boundary mapping

| New mesh zone | Required E0 role |
| --- | --- |
| `liquidinlet` | Parent-reconciled split mass-flow inlet delivering `116.92 kg/s` continuous liquid with the parent turbulence state |
| `steaminlet` | Parent-reconciled split mass-flow inlet delivering `80.69 kg/s` continuous vapor with the parent turbulence state |
| `steamoutlet` | Parent-reconciled pressure outlet at the proven parent pressure/backflow state, with hydraulic diameter corrected to `0.875936 m` |
| `bottom` | Stationary, no-slip wall; zero phase and mixture through-flow |
| `wall` | Preserve corresponding parent stationary-wall state |
| `separator-purnanto:1` | Preserve corresponding parent stationary-wall state; mapping must be demonstrated rather than inferred from the name |
| `separator-purnanto` | Fluid mixture cell zone with the parent material/phase state |

Boundary-flow signs and realized values must be read back during smoke. A zone
that is missing, duplicated, ambiguously mapped, or assigned to the wrong
boundary type invalidates the prepared case.

### Steam-outlet correction

The authoritative mesh face area is `0.602608 m²`, whose equivalent circular
diameter is `0.875936 m`. Set the outlet turbulence/backflow hydraulic
diameter to the full-precision value and prove it by:

1. immediate setting readback;
2. prepared-case save;
3. full case reopen; and
4. post-reopen readback.

The former `0.724 m` value belongs to the square-inlet side length and must not
be propagated to the Phase-07 steam outlet.

## Initialization contract

- Instrument every hard-required report before initialization.
- Use the initialization method and options proven from the exact parent.
- Do not introduce a liquid pool patch, phase-fraction patch, pressure patch,
  velocity patch, or reconstructed-interface patch unless it is proven as the
  exact parent-defined initialization state.
- Save the prepared uninitialized case, reopen it, and pass complete setup
  readback before initialization.
- Initialize once, then save the initialized case/data pair before iteration 1.
- If the parent-defined initialization method does not survive mesh
  reconciliation or cannot be proven, return upstream; do not choose a
  replacement silently.

## Hard pre-run instrumentation

Every report must write a durable file-backed sample at every solver iteration
using native iteration coordinates. Stable implementation names may add a run
prefix, but their scientific identity must remain clear.

### Inventory reports

| Report ID | Quantity | Units/scope |
| --- | --- | --- |
| `e0-liquid-mass-total` | Integral continuous-liquid mass | `[kg]`, entire `separator-purnanto` fluid zone |
| `e0-liquid-volume-total` | Integral continuous-liquid volume | `[m³]`, entire fluid zone; required when Fluent exposes a verified formulation |

The liquid-mass report is mandatory. The exact field/expression must be proven
against phase density and volume fraction so that it measures continuous
liquid inventory rather than mixture mass or an area average.

### Phase-resolved boundary-flow reports

For each phase (`liquid`, `vapor`) record mass flow `[kg/s]` independently on:

- `liquidinlet`;
- `steaminlet`;
- `steamoutlet`; and
- `bottom`.

Also record mixture mass flow `[kg/s]` independently on the same four zones.
Do not combine surfaces into one report because phase routing must remain
auditable.

### Derived histories

Preserve Fluent's raw sign convention, then derive a second declared
engineering convention with inlet magnitude positive into the domain and
outlet magnitude positive out:

```text
liquid net rate  = liquid inflow - liquid steamoutlet discharge - liquid bottom discharge
vapor net rate   = vapor inflow  - vapor steamoutlet discharge  - vapor bottom discharge
mixture net rate = total inflow  - total steamoutlet discharge  - total bottom discharge
mixture imbalance ratio = abs(mixture net rate) / 197.61 kg/s
bottom vapor-loss ratio  = bottom vapor discharge / 80.69 kg/s
```

For E0 the bottom fluxes should remain zero. Their reports are nevertheless
mandatory because all later fixed-mesh treatment comparisons require the same
surface-level evidence layout.

### Numerical histories

- Configure scaled residual printing/history for every active solved equation
  before initialization.
- Capture residual rows with native iteration coordinates through a durable
  transcript or another independently proven file-backed route.
- Store the complete solver transcript.
- Endpoint residual values or a post-run screenshot cannot replace the native
  history.

### Setup and artifact manifests

Record:

- parent and mesh hashes;
- Fluent version and host-independent run ID;
- pre-mutation parent readback;
- intended mutation list;
- immediate and post-reopen E0 readback;
- report names, output identities, sample counts, and coordinate extents;
- mesh-check and mesh-quality output;
- every checkpoint case/data identity and checksum where practical; and
- terminal status, final iteration, and final artifact identity.

Missing liquid-inventory, phase-flux, mixture-balance, or residual history is
non-waivable and makes E0 invalid for scientific comparison.

## Build, verification, and smoke sequence

No step after a failed gate is permitted.

1. Resolve server paths in `run-paths.yaml`; verify exact parent and mesh hashes.
2. Load and export/read back the exact parent setup.
3. Reconcile the exact Phase-07 mesh and named zones without initialization.
4. Apply only the declared boundary mapping and outlet-diameter correction.
5. Create and redirect the complete report/residual package.
6. Run Fluent's mesh check and capture solver-side mesh-quality evidence.
7. Save the prepared uninitialized case to a new output identity.
8. Reopen that prepared case by full resolved path and repeat all critical
   setup, boundary, outlet-diameter, numerics, DPM-isolation, and report
   readbacks.
9. Initialize once using the proven parent-defined method and save the initial
   case/data pair.
10. Run iterations `1–50` as the smoke segment, included in the 2,000 total.
11. Require 50 native report coordinates and residual evidence, correct inlet/
    outlet signs, finite inventory, zero bottom flux, and no solver divergence.
12. Save the iteration-50 smoke case/data pair before continuing.

## Run horizon and checkpoints

| Segment/checkpoint | Native iteration | Purpose |
| --- | ---: | --- |
| Prepared case | before initialization | Save/reopen-proven setup state |
| Initialized pair | `0` | Reproducible E0 initial condition |
| Smoke pair | `50` | Instrumentation and survivability gate |
| Checkpoint | `500` | Early development recovery state |
| Checkpoint | `1,000` | Start of first declared late comparison interval |
| Checkpoint | `1,500` | Shared boundary between adjacent analysis windows |
| Final pair | `2,000` | End of approved discovery horizon |

The total authorized design horizon is 2,000 iterations from initialization;
the smoke iterations are not extra.

Primary analysis uses the final 500 iterations. Compare least-squares liquid-
inventory and applicable balance slopes over `1,000–1,500` and
`1,500–2,000`. Preserve all raw histories and report final-window mean, range,
and slope without deleting early samples.

Reaching iteration 2,000 completes the planned discovery horizon, not a
convergence claim. An evolving or noise-dominated late slope permits only an
explicitly human-reviewed continuation of unchanged E0, normally another
1,000 iterations. It does not authorize tuning or a bottom treatment.

## Required evidence

E0 counts only when all of the following exist and pass:

- exact parent and mesh identities;
- parent settings readback and bounded reconciliation;
- valid zone map and Fluent mesh check;
- immediate plus save/reopen-proven prepared E0 readback;
- proven `0.875936 m` outlet hydraulic diameter after reopen;
- proven one-way/no-carrier-source DPM state;
- initialized, smoke, checkpoint, and final paired artifacts;
- complete 2,000-iteration liquid inventory history;
- all phase and mixture boundary-flow histories;
- derived liquid/vapor/mixture net-rate and imbalance histories;
- complete native scaled-residual histories;
- solver transcript, report manifest, and terminal execution manifest; and
- analysis of both declared 500-iteration windows and all three core figures.

## Supporting evidence

- solver-side minimum orthogonal quality, maximum skewness/aspect ratio where
  exposed, cell-volume range, and zone-area readback;
- final liquid-volume-fraction contour on a declared central plane and/or
  exterior rendering that locates retained liquid;
- inlet/outlet pressure and velocity reasonableness; and
- contextual comparison with the historical 08b endpoint flux report,
  explicitly labelled as unmatched.

## Core figure plan

### F1 — Liquid-inventory reference

| Field | Contract |
| --- | --- |
| Question | Does wall-bottom E0 provide a measurable and sufficiently repeatable buildup reference? |
| Plot | Raw total-domain continuous-liquid mass history plus separately fitted lines over `1,000–1,500` and `1,500–2,000` |
| X-axis | Native solver iteration, `1–2,000` |
| Y-axis | Continuous-liquid mass `[kg]`; companion volume `[m³]` when valid |
| Series/cases | E0 raw history and two labelled window fits |
| Comparison basis | Adjacent 500-iteration windows within E0 |
| Reduction | Raw history and least-squares slope `[kg/iteration]` per window |
| Data source | `e0-liquid-mass-total` file-backed report |
| Instrumentation | Mandatory before initialization |
| Interpretation use | Similar slopes support a usable reference even when positive; changing or noise-dominated slopes make E0 inconclusive. |

### F2 — Phase routing and closure

| Field | Contract |
| --- | --- |
| Question | Is the inventory trend consistent with measured phase routing and mixture imbalance? |
| Plot | Aligned phase inflow/outflow/net-rate histories and normalized mixture-imbalance panel |
| X-axis | Native solver iteration, `1–2,000` |
| Y-axis | Phase mass rate `[kg/s]`; normalized imbalance `[-]` |
| Series/cases | Both inlets, steam outlet, bottom, and derived net histories for liquid, vapor, and mixture |
| Comparison basis | `116.92 kg/s` liquid, `80.69 kg/s` vapor, `197.61 kg/s` mixture nominal inflows |
| Reduction | Raw histories plus final-500 mean, range, and slope where meaningful |
| Data source | Pre-run phase and mixture boundary reports |
| Instrumentation | Mandatory before initialization |
| Interpretation use | Tests conservation consistency and exposes phase-routing, surface-selection, or sign errors. |

### F3 — Numerical adequacy

| Field | Contract |
| --- | --- |
| Question | Are E0's inventory and balance trends numerically credible enough for matched treatment comparisons? |
| Plot | Log-scale native scaled-residual histories aligned with mixture-imbalance history |
| X-axis | Native solver iteration, `1–2,000` |
| Y-axis | Scaled residual `[-]`; mixture net rate `[kg/s]` or normalized imbalance `[-]` |
| Series/cases | Every active solved equation plus E0 mixture imbalance |
| Comparison basis | Full history and final 500 iterations |
| Reduction | Raw histories; final-window mean/range and qualitative trend classification |
| Data source | Verified residual transcript/file and mixture reports |
| Instrumentation | Mandatory before initialization |
| Interpretation use | Distinguishes an informative accumulation baseline from solver deterioration or incomplete numerical development. |

## Decision rules

### Usable E0 reference

The setup and execution are valid, and the adjacent late histories establish a
sufficiently repeatable scale for comparing a later approved treatment. A
large positive liquid buildup or mixture imbalance does not by itself fail E0.

### Inconclusive E0 reference

The valid late histories remain too strongly evolving or too noisy to define a
reference slope. Return for a decision on an unchanged continuation; do not
tune the case or activate the bottom.

### Invalid E0

Artifact identity, zone mapping, setup readback, save/reopen, initialization,
smoke, residual capture, inventory capture, phase-flux capture, or final
artifact verification fails. Repair only the same approved setup or return to
the human; produce no scientific comparison from the invalid run.

## Claim boundary

E0 can establish only the numerical reference behavior of the corrected
simplified model under the declared setup. It cannot establish steady mass
convergence, physical brine drainage, validated outlet behavior, mesh
independence, plant control performance, or exact parity with historical 08b.

