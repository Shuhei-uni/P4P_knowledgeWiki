# Phase 7.1A — N1 Coupled + Global Time Step

> **Status — NEXT DISCOVERY CANDIDATE (2026-09-22):** Prepare from the exact
> v2 prepared pair. This record defines the experiment but does not authorize a
> solve until live preflight, save/reopen, instrumentation, and smoke gates
> pass.

## Question and hypothesis

Does replacing the v2 baseline’s SIMPLE pressure correction with Fluent’s
pressure-based Coupled scheme together with the steady Coupled-compatible
Global Time Step treatment produce a more bounded numerical trajectory for the
phase-2-only virtual liquid outlet?

Hypothesis: simultaneous pressure–velocity treatment plus controlled numerical
pseudo-time marching may reduce the nonlinear lag or abrupt pressure/velocity
response caused by the local liquid sink. The test does not assume that it can
repair an unavailable-liquid request or a physically inconsistent phase path.

## Exact parent and controlled delta

- Parent: the prepared/reopened pair recorded in
  `../baseline-v2-virtual-liquid-outlet/run-paths.yaml`.
- Parent identity: `P71A-BASELINE-V2-VIRTUAL-OUTLET`; verify both case/data
  hashes before mutation and save a child recovery pair before replacing or
  altering the live state.
- Solver: pressure-based, steady, absolute velocity formulation.
- Controlled solver package: pressure–velocity coupling `SIMPLE` → `Coupled`
  and steady pseudo-time method → `Global Time Step`.
- Pseudo-time policy: `Automatic` initially, with every exposed initial,
  maximum, growth, Courant, or equivalent control recorded before solving.
- Physical time: remain off; do not use `dual-time-iterate`, transient
  advancement, or physical-time monitors.

The two solver settings are intentionally one combined N1 package. N1 cannot
be described as a test of pseudo-time alone. No `Coupled with Volume Fractions`
option is to be enabled; retain the parent’s Mixture volume-fraction/slip/drift
treatment and verify its compatibility in the live tree.

## Frozen invariants

Keep all other v2 settings unchanged, including:

- the `60,964`-cell 60k mesh and `p71a-v2-virtual-outlet` 715-cell zone;
- Mixture, phase identities, implicit dispersed treatment, RNG k-epsilon,
  wall treatment, gravity, materials, and operating/reference conditions;
- PRESTO!, gradient/discretization schemes, under-relaxation, AMG controls,
  residual definitions, DPM state, and energy/species-off state;
- the v2 source law `P71V2Sink`, matching phase-2 velocity momentum removal,
  shared `k`/epsilon removal, and direct phase-1 source disabled;
- mass-flow inlets, `steamoutlet` as the only pressure outlet, all bottom
  boundaries as walls, and the parent’s phase-resolved outlet backflow state;
- fresh Hybrid Initialization from the prepared pair, with no patch, reset,
  sink-off warm-up, remeshing, resplitting, or source retuning;
- the common loading history: `0.25` start multiplier, linear ramp to
  `116.92 kg/s` liquid and `80.69 kg/s` steam over native iterations `1–2,000`,
  update every `10` iterations.

## Preflight and proof gates

Before any long solve:

1. verify the prepared parent case/data pair and mesh/cell-zone identity;
2. read back the baseline coupling and pseudo-time settings;
3. inspect the live Fluent 2025 R2 tree for the exact Coupled and Global Time
   Step controls; do not infer them from another server or Fluent version;
4. apply only the N1 package and read it back, including proof that physical
   transient advancement remains disabled;
5. configure or verify the report histories before iteration 1;
6. save/reopen the prepared N1 child and repeat the critical readback;
7. run a short smoke block, preserving a paired smoke/recovery checkpoint;
8. confirm native iteration advancement, finite residuals, command/source
   instrumentation, and no setup drift before the main discovery horizon.

If a required control or report is unavailable, record the capability/evidence
block and stop the child. Do not substitute Local Time Step, PISO/SIMPLEC,
transient solving, or a different model formulation.

## Horizon and checkpoints

After the smoke gate, run the same `2,000` native steady iterations as the N0
loading history in `10`-iteration inlet-control blocks. Preserve paired local
checkpoints at active iterations `0`, `500`, `1,000`, `1,500`, and `2,000`.
Keep working checkpoints on the Fluent host’s local disk and copy only the
terminal pair and durable evidence package to the recorded final artifact
location.

The run may be extended only after the 2,000-iteration evidence is classified;
extension is not an automatic qualification pass.

## Evidence required before interpretation

Record on native solver iterations:

- coupling and Global Time Step/pseudo-time readback and any pseudo-time
  history Fluent exposes;
- continuity, x/y/z momentum, `k`, epsilon, and phase-2 volume-fraction
  residuals;
- `liquidinlet`, `steaminlet`, and `steamoutlet` mixture/phase fluxes;
- `P71V2Command`, named removal, native applied phase-2 source, and phase-1
  source audit;
- lower-zone available liquid, lower-zone liquid mass/volume, total liquid
  mass/volume, and phase-1 vapor inventory;
- source-inclusive phase and mixture closure with storage terms when the
  trajectory is not stationary;
- pressure-outlet reverse flow, AMG messages, FPE/non-finite diagnostics, and
  turbulent-viscosity limiting; and
- paired checkpoint hashes and wall-clock/iteration timing.

The command must remain distinct from the realized source. Exact command
tracking is not enough to claim physical absorber capacity when the local
liquid inventory is small.

## Decision use and claim limit

Classify N1 as one of:

- **stabilization evidence:** late residuals and inventory are materially more
  bounded than N0 and routing/source closure remain credible;
- **endurance-only evidence:** the case survives longer or avoids an early
  failure, but remains drifting, limiter-dominated, or reverse-flow dominated;
- **no useful improvement:** failure is earlier or the diagnostics worsen; or
- **ambiguous:** instrumentation or phase routing is insufficient for a fair
  comparison.

Only the first two categories justify designing N2, and N2 must use the
specific live control/evidence that explains what to change. N1 cannot isolate
pseudo-time from coupling, cannot establish physical-time response, and cannot
qualify the absorber or promote the phase.
