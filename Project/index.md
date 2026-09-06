# Project

This is the default entry point for the project's current scientific truth.
`Project/` owns the question being pursued, stable model assumptions, selected
experiments, evidence interpretation, and claim limits. Reusable CFD knowledge
belongs in `CFD_wiki/`; executable implementation and machine evidence belong
in `PyAnsys/`.

## What are we trying to answer now?

Can a full-geometry CFD model reproduce a physically credible, controlled
bottom brine-pool operating condition for the separator, rather than merely a
response to a fixed brine-outlet pressure?

The immediate technical question is whether the F11-derived model can provide
a defensible level-related observable and phase-aware outlet-flow basis before
we test a more physically meaningful brine-outlet response representation.

## Active/latest experiment

The current scientific lane is the canonical full-geometry Mixture `03A`
brine-pool level-control phase, following the completed Stage-5 fixed-pressure
discovery work. Its Project tracer is the shortest route through the selected
record:

- [03A tracer index](experiments/phase-05-full-geometry-v2/full-geometry-03a-mixture-08b-parity-baseline/index.md)
- [Stage-4 setup contract](experiments/phase-05-full-geometry-v2/full-geometry-03a-mixture-08b-parity-baseline/stage-04/setup.md)
- [Stage-4 execution evidence](experiments/phase-05-full-geometry-v2/full-geometry-03a-mixture-08b-parity-baseline/stage-04/results.md)
- [Stage-5 fixed-pressure evidence](experiments/phase-05-full-geometry-v2/full-geometry-03a-mixture-08b-parity-baseline/stage-05/results.md)
- [Phase-06 Full Geometry with Brine Pool contract](experiments/phase-06-full-geometry-with-brine-pool/setup.md)
- [Phase-06 Stage-01 setup](experiments/phase-06-full-geometry-with-brine-pool/stage-01-level-observable-and-outlet-response/setup.md)
- [Phase-06 results and closure](experiments/phase-06-full-geometry-with-brine-pool/results.md)
- [Phase-06 Stage-06 long-horizon evidence](experiments/phase-06-full-geometry-with-brine-pool/stage-06-long-horizon-surrogate-hypothesis/results.md)

The earlier Project experiment records preserve the migrated setup and result
memory for the Purnanto, full-geometry, DPM, EWF, VOF, and reconstruction
families. Their historical status is part of the evidence; they are not
silently upgraded to current conclusions.

## What did the latest experiment show?

The completed Phase-06 discovery screens and the Stage-06 10,000-iteration
long numerical-surrogate hypothesis test did not establish a controlled pool
state in the F11 steady Mixture/RNG bracket. In the long test, the lower-region
proxy remained well above its deliberately non-plant 200 kg target after the
bounded pressure actuator saturated, while the final-window phase-liquid net
rate and imbalance remained positive. The final endpoint has a verified paired
checkpoint and complete file-backed report histories; the PyFluent residual
monitor did not populate, so no convergence claim is made.

This is a bounded model result, not evidence that the physical separator
cannot be level controlled.

## What remains unresolved?

- the real level sensor datum/location, target and operating band;
- the brine outlet hardware/line characteristic, downstream condition, and
  controller behaviour required to model a physical controlled outlet;
- whether a human-approved new transient/model-form/control scope is warranted
  after the current steady surrogate has failed to establish control;
- which external, analytical, or measured targets are appropriate for a
  validation claim.

## What happens next?

**Phase 06 is not closed under the current mandatory lifecycle gates.** The
10,000-iteration calculation usefully weakened the Stage-04 hypothesis: after
pressure saturation, the numerical proxy remained above target with positive
late storage/phase-liquid accumulation. However, only three valid discovery
cases are identified, the canonical long-run job is `BLOCKED`, and the required
residual history and named final pair are absent. Those gaps prevent discovery,
hypothesis-evidence, and closure gates from passing.

The human has authorized a bounded numerical-surrogate route whose purpose is
to mimic the main level-control behaviour without claiming plant fidelity. The
persisted state is now `DISCOVERY_DESIGN`. The next permitted step is a
gate-reviewed campaign of 6–12 nonredundant full-geometry steady surrogate
cases with durable numerical and physical histories. Mixture/RNG is the
reference, but justified steady multiphase and turbulence alternatives are
allowed. Transient work or a physical validation claim still requires a return
to the human.

## Project map

- [experiment phase structure](experiments/README.md)
- [scope](scope.md)
- [stable model assumptions](model.md)
- [V&V and claim limits](vnv.md)
- [selected-experiment contract](experiments/README.md)
- [cross-experiment observations](observations/index.md)
- [technical project records](technical)

## Supporting source input

The original project source inputs and retired written project wiki were
removed from the current checkout at the user's request. Their exact history
is recoverable from Git; they are not active authorities.
