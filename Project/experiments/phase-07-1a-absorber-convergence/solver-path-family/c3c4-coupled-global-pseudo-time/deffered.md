# P71A-C3C4-COUPLED-GLOBAL-PSEUDO-TIME setup

> **Status — DEFFERED (2026-09-22):** Deferred after the Server-3 approach
> was paused; retain this setup as planning provenance only.

| Field | Value |
| --- | --- |
| Status | READY_FOR_PHASE_LOOP_AFTER_LIVE_PREFLIGHT |
| Lifecycle role | Discovery numerical-stabilization screen |
| Phase context | [Phase 7.1A CONTEXT](../../CONTEXT.md) |
| Candidate | `C3C4-COUPLED-GLOBAL-PSEUDO-TIME` |
| Origin | Direct human phase-loop invocation on 2026-09-15 |
| Authority | Current human request to try steady pseudo-transient stabilization |
| Decision gate | `G0 / DISCOVERY_DESIGN` extension |
| Baseline | [Active Fluent baseline](../../baseline-setup-record.md) |
| Parent identity | `P7-E5-CZ-ABSORB-COLD-RAMP11692` active-1000 paired case; see [parent reference](../../turbulence-family/parent-reference.md) |
| Novelty | New steady solver-path package; not a transient-model branch |
| Planned horizon | 50-iteration smoke, then 500 attached discovery iterations |

## Question

Can a pressure-based Coupled solver with its compatible steady Global Time Step
(pseudo-time) treatment produce a more bounded numerical trajectory from the
same difficult active-1000 absorber state, while preserving the lower,
phase-2-only liquid-removal interpretation and vapor-only outlet routing?

This is a numerical-path discovery screen. It does not test whether the RNG
model is physically correct, does not validate the absorber, and does not turn
the calculation into a physical transient.

## Prior evidence and competing explanation

The matched T0/standard/realizable k-epsilon screen retained nonstationarity,
reverse flow, and broad turbulent-viscosity limiting for all three closures.
The fixed-source continuation reached active 1,960 before repeated divergence,
with positive liquid-inventory drift. That evidence leaves pressure correction,
velocity coupling, source conditioning, and equation treatment as competing
explanations; turbulence closure alone was not promoted.

The candidate tests the specific numerical explanation that the SIMPLE pressure
correction path is too weak or too abrupt for this source-dominated Mixture
state. Pseudo-time is treated as a continuation/stabilization device only. It
is not expected to repair a physically inconsistent source or create a local
mass balance by itself.

An independent adversarial design review rated the candidate scientific value
`3/4`, interpretability `2/4`, and cost-effectiveness `3/4`. Its disposition
was **viable after repair**: name the combined solver package honestly, append
it to the lifecycle queue, resolve the live-supported global-step controls
before execution, and require inventory, routing, limiter, and warning
evidence in addition to residual survival.

## Controlled solver-path change

The intended package is:

1. pressure-velocity coupling: `SIMPLE` → Fluent pressure-based `Coupled`;
2. steady pseudo-time: enable the Coupled-compatible **Global Time Step** /
   pseudo-transient treatment while retaining steady, iteration-based solving.

This is deliberately a combined C3+C4 solver-package delta. It is **not** an
isolated pseudo-time test, and results may not be described as proving that
pseudo-transient stabilization alone caused any improvement.

Before mutation, the live Fluent 2025 R2 parent must expose and the
implementation must record:

- the allowed pressure-coupling values and exact Coupled formulation;
- the exact Global Time Step / pseudo-time control path;
- fixed versus adaptive step policy;
- initial, maximum, and any lower-bound step or equivalent Courant controls;
- any automatic ramp or relaxation associated with the coupled solver;
- confirmation that physical transient/time-accurate advancement remains off.

These controls are a hard pre-run dependency. If the live Mixture case does
not support this route, stop and record a blocker. Do not substitute Local
Time Step, a transient solver, PISO/SIMPLEC, a different model formulation, or
reactive tuning during the run.

## Frozen comparison context

Load the exact active-1000 paired parent without initialization, patching,
resetting, remeshing, resplitting, or restart-field alteration. Preserve:

- the two-continuous-phase Mixture formulation and implicit dispersed treatment;
- phase 1 water vapor and phase 2 water liquid;
- RNG k-epsilon, RNG differential viscosity, RNG swirl option, standard wall
  functions, and all turbulence options;
- Green-Gauss node-based gradients, PRESTO! pressure, second-order momentum,
  first-order `k`, second-order epsilon, and QUICK volume fraction;
- the lower `p7-e5-lower-y010` phase-2-only absorber, commanded integrated
  source `-116.92 kg/s`, and matched source accounting;
- the bottom stationary wall, both mass-flow inlets, steam pressure outlet,
  and vapor-only phase-2 backflow specification;
- gravity, materials, operating/reference conditions, mesh, DPM state, energy
  and species-off state, residual criteria, and report definitions;
- the restart field from the exact active-1000 parent.

Do not add an outlet, direct phase-1 sink, UDF, UDS, species equation, source
retuning, sink-off warm-up, patch, reset, mesh change, or residual-criteria
change. The generic 100–200-iteration sink-off warm-up is not part of this
same-parent test: it would change the tested restart/source history and would
confound the solver-path comparison.

## Run and decision intent

The run is discovery-only and remains attached. After parent readback and
prepared child save/reopen:

1. run the required 50-iteration smoke test;
2. verify iteration advancement, report creation, residual capture, and no
   setup drift;
3. run 500 active iterations synchronously;
4. save a paired final checkpoint and preserve the last valid paired state if
   AMG divergence, floating-point exceptions, or non-finite fields occur.

Classify the result before interpretation:

- **Numerical stabilization with credible branch evidence:** residuals are
  bounded or decreasing in the final window, inventory slopes flatten relative
  to the reference, reverse-flow/limiter activity does not grow, and
  phase-selective routing remains credible.
- **Improved endurance only:** the child survives longer or avoids immediate
  failure, but residuals remain nonstationary, inventories drift, or limiter /
  reverse-flow activity remains broad. This is useful discovery evidence but
  not a steady-branch qualification.
- **No useful stabilization:** immediate AMG/FPE failure or rapidly worsening
  residual, inventory, or limiter diagnostics.
- **Numerically calmer but scientifically invalid:** residuals improve while
  lower-zone phase-2 delivery, source accounting, or vapor routing is not
  preserved.

Completion of 500 iterations alone is not a success criterion.

## Required evidence

Capture before and during the smoke/main solve:

- exact parent identity and complete pre/post-mutation readback;
- Coupled and Global Time Step/pseudo-time readback, including all controls;
- native scaled residual histories for continuity, all momentum components,
  `k`, epsilon, and phase-2 volume fraction;
- turbulence limiter/clipping diagnostics, warnings, AMG messages, and FPE or
  non-finite-field diagnostics;
- phase-resolved and mixture fluxes at `liquidinlet`, `steaminlet`,
  `steamoutlet`, `bottom`, and the absorber accounting region;
- commanded lower-zone phase-2 source, realized lower-zone phase-2 source,
  lower-zone phase-2 mass/volume, adjacent-zone and broad-zone liquid mass,
  and total liquid inventory histories;
- phase-1 vapor inventory history, not only inlet/outlet fluxes;
- outlet reverse-flow and phase-routing evidence;
- matching prepared, smoke/recovery, and final case/data pairs.

The source command must remain distinct from actual phase-2 delivery and
removal. If vapor-inventory instrumentation cannot be established before the
smoke test, the run may only support a limited numerical-path observation and
the full phase-balance judgement remains blocked.

## Core figure plan

1. **Solver-path stability history** — native iteration versus continuity,
   momentum, `k`, epsilon, and phase-fraction residuals, with the T0 reference
   on the same active-iteration basis; add limiter/warning markers where the
   native evidence permits.
2. **Phase/source balance and inventory** — phase-resolved inlet/outlet fluxes,
   commanded and realized absorber source, lower/adjacent/broad/total liquid
   inventories, and vapor inventory versus native iteration.
3. **Routing and turbulence state** — matched checkpoint fields or derived
   histories for phase-2 volume fraction, turbulent viscosity/limiting, and
   outlet reverse flow, with the lower absorber zone identified.

Each figure supports a bounded discovery comparison only. No figure may be
used to claim physical separator validation, plant performance, or a
qualification-ready steady absorber solution.

## Claim limits and continuation

The strongest permitted conclusion is whether the **Coupled + Global Time Step
solver package** improved, failed to improve, or only extended the numerical
endurance of this exact active-1000 absorber state. The result cannot attribute
an effect to pseudo-time alone, establish a generally converged steady branch,
or promote the absorber to Phase 08.

If a credible bounded trajectory appears, any continuation or longer run must
be separately designed and gated. If the Student endpoint remains unavailable,
the setup remains `NOT_RUN`; do not run it on the reachable unrelated server-3
session.
