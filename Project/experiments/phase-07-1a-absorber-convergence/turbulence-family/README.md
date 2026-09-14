# Phase 7.1A turbulence family

## Status

**Human-selected family; the first closure screen is complete and the staged
T2-T4 extension queue is active.**

This family was created after the live Fluent baseline audit on 2026-09-11.
It expands the turbulence investigation while preserving the accepted
bottom-only, phase-2-only cell-zone absorber.

The first tier compared turbulence closures. The active extension queue now
isolates RNG options, wall treatment, turbulence-equation numerics, and
multiphase turbulence coupling. SST and RSM remain deferred escalation
branches and do not yet have child setup packets.

T0 RNG reference, T1 standard k-epsilon, and T1 realizable k-epsilon were
executed in order on the `student` server from the exact active-1000 parent.
All three completed their 500-active-iteration attached discovery horizon with
paired save/reopen and evidence artifacts. The first realizable preflight was
blocked before solving when the validator had not yet encoded Fluent's
branch-specific absent Kato-Launder option; that attempt is preserved and the
fresh-parent retry completed successfully. The direct human phase-loop
invocation has now declared the remaining T2-T4 packets as queue orders 4–11,
in the order listed under Planned staging.

The first-screen execution gate is complete. The discovery evidence is
intentionally not promoted to a hypothesis route: the three closure branches
retain finite-horizon nonstationarity, reverse flow, and broad
turbulent-viscosity limiting, and no branch has a qualification claim. The
first campaign comparison is recorded in
[`family-analysis-summary.json`](family-analysis-summary.json) with the two
family-level comparison figures under `figures/`. The T2-T4 extension uses the
same exact parent and evidence contract and remains discovery-only.

## Family question

> Which turbulence closure or turbulence-specific treatment can reduce
> turbulence residual growth and turbulent-viscosity limiting while preserving
> the lower phase-2 absorber, phase-resolved accounting, and vapor-only outlet
> routing?

## Baseline reference

The live active settings are recorded in
[baseline-setup-record.md](../baseline-setup-record.md). That record is the
reference fingerprint, not a proven case/data identity.

The future parent must be a complete paired case/data artifact that is reopened
and read back against the baseline fingerprint before mutation. A live session
or iteration count alone is not sufficient parent identity.

The selected parent for the turbulence-family queue is the saved active-1000
absorber pair documented in [parent-reference.md](parent-reference.md). Its
prior manifest proves the absorber topology, source tree, bottom wall, and
save/reopen state. A read-only Fluent file-existence probe on 2026-09-11
confirmed both remote files are present on student. The child implementation
must load that pair without reinitialization and perform its own full parent
readback before mutation.

The live closure path and the no-mutation implementation rule are recorded in
[closure-path-readback.md](closure-path-readback.md).

## Frozen comparison context

Unless a child packet explicitly states its single turbulence delta, preserve:

- pressure-based steady solver;
- Mixture model with two continuous phases;
- implicit dispersed phase treatment;
- phase 1 water vapor and phase 2 water liquid;
- gravity and operating conditions;
- minimum-phase-averaged operating density;
- lower p7-e5-lower-y010 phase-2-only absorber;
- absorber integrated command of 116.92 kg/s;
- zero direct phase-1 source and no parent-zone source;
- bottom as a stationary no-slip wall;
- liquid and steam inlet mass-flow targets;
- steam pressure outlet and vapor-only phase-2 backflow volume fraction;
- SIMPLE pressure-velocity coupling;
- Green-Gauss node-based gradients;
- PRESTO! pressure;
- second-order momentum;
- first-order k unless the child explicitly tests k order;
- second-order epsilon;
- QUICK phase fraction;
- current under-relaxation factors, equation limits, and AMG controls;
- energy and species off;
- DPM continuous-phase interaction off;
- trace DPM injections at 1e-20 kg/s;
- unchanged residual criteria and report definitions.

No child may change the absorber mechanism, open the bottom, add a vapor sink,
patch/reset the field, introduce transient modelling, or change residual
criteria to make a branch appear converged.

## Planned staging

| Tier | Child packets | Purpose |
| --- | --- | --- |
| T0 | t0-rng-reference | Establish the exact reference behaviour and evidence package |
| T1 | t1-standard-kepsilon, t1-realizable-kepsilon | Compare nearby k-epsilon closures |
| T2 | t2-rng-production-limiter, t2-rng-differential-viscosity-off, t2-rng-swirl-off, t2-rng-kato-launder | Isolate RNG options and turbulence-production treatment |
| T3 | t3-scalable-wall-functions, t3-non-equilibrium-wall-functions | Test near-wall compatibility |
| T4 | t4-k-second-order, t4-multiphase-turbulence-dispersion | Separate turbulence-equation order from phase-slip/turbulence coupling |

The first scientific comparison was T0, T1-standard-kepsilon, and
T1-realizable-kepsilon. The remaining queue is now ordered as T2 production
limiter, T2 differential viscosity off, T2 swirl off, T2 Kato-Launder, T3
scalable wall functions, T3 non-equilibrium wall functions, T4 second-order
`k`, and T4 multiphase turbulence dispersion.

## Deferred escalation branches

These are not child setup packets yet:

- SST k-omega, after the k-epsilon family fails to explain the coupled
  instability;
- Reynolds Stress Model, only if strong anisotropy/rotation evidence justifies
  the cost and additional convergence risk;
- curvature correction, after the simpler production and RNG-option probes;
- enhanced or Menter-Lechner wall treatment, only after wall-distance evidence;
- GEKO, which is deferred because its additional coefficients would make the
  first diagnosis less interpretable.

## Shared discovery evidence contract

Every child that eventually enters execution must capture, at minimum:

- exact parent case/data identity and full setup readback;
- prepared save/reopen proof;
- native scaled residual histories for continuity, three momentum components,
  k, epsilon, and phase-2 volume fraction;
- turbulence residual histories and turbulent-viscosity limiting/clipping
  diagnostics;
- phase-resolved and mixture fluxes at liquidinlet, steaminlet, steamoutlet,
  bottom, and absorber source accounting;
- lower-zone, adjacent-zone, broad-zone, and total liquid inventories;
- reverse-flow and outlet phase-routing evidence;
- commanded absorber source and realized phase-2 removal evidence;
- warnings, divergence, floating-point, and AMG diagnostics;
- matching checkpoint/final case-data pairs;
- unchanged residual criteria and report definitions.

The absorber command is an input, not proof of realized removal. The result
must distinguish the commanded -116.92 kg/s phase-2 source from the measured
phase-resolved balance and inventory response.

## Core figure plan

Each child uses the same three core figure questions:

1. **Turbulence stability history** — native iteration versus continuity, k,
   epsilon, phase-fraction residuals, and turbulent-viscosity limiting,
   compared against the T0 reference. The campaign-level residual comparison
   is `figures/turbulence-family-residual-comparison.png`.
2. **Coupled phase/source balance** — native iteration versus phase-2 inlet,
   absorber/source accounting, steam-outlet phase fluxes, and lower/total
   liquid inventories.
3. **Spatial turbulence/phase state** — matched-checkpoint contours or derived
   fields for k, epsilon, turbulent viscosity or viscosity ratio, and phase-2
   volume fraction, with the lower absorber zone marked. This queue captured
   selected-cell inventory histories rather than contours, so the spatial
   figure is explicitly partial and makes no field-level claim.

These figures support a bounded discovery judgement only. They do not establish
physical separator validation or Phase 08 readiness.

## Lifecycle note

The phase-root phase-state.yaml records the passed DISCOVERY_DESIGN gate, the
completed first-screen execution, and the active direct-human T2-T4 extension
queue. All extension items remain discovery-only. The bounded
DISCOVERY_EVIDENCE outcome does not authorize Q-TURB-CLOSURE or a hypothesis
route; qualification work remains separately gated.
