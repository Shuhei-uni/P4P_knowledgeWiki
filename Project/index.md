# Project

This is the default entry point for the project's current scientific truth.
`Project/` owns the question being pursued, stable model assumptions, selected
experiments, evidence interpretation, and claim limits. Reusable CFD knowledge
belongs in `CFD_wiki/`; executable implementation and machine evidence belong
in `PyAnsys/`.

## What are we trying to answer now?

What practical numerical mechanism can remove separated liquid from the
bottom of a simplified Purnanto separator model while preserving useful and
interpretable separation behaviour?

The simplified geometry will be truncated at the elevation corresponding to
the real separator's brine-pool surface. Phase 07 will use human-originated,
explicitly approved liquid-removal candidates at the bottom of this truncated
computational domain.

## Active/latest experiment

The current scientific lane is Phase 07: simplified Purnanto liquid-removal
mechanism development. No particular removal method or runnable experiment has
yet been selected. The most direct records are:

- [Phase-07 direction and boundaries](experiments/phase-07-simplified-purnanto-liquid-removal/index.md)
- [Phase-07 human-approved planning context](experiments/phase-07-simplified-purnanto-liquid-removal/CONTEXT.md)
- [Phase-06 human-directed conclusion](experiments/phase-06-full-geometry-with-brine-pool/conclusion.md)

The predecessor evidence remains available through these records:

- [03A tracer index](experiments/phase-05-full-geometry-v2/full-geometry-03a-mixture-08b-parity-baseline/index.md)
- [Stage-4 setup contract](experiments/phase-05-full-geometry-v2/full-geometry-03a-mixture-08b-parity-baseline/stage-04/setup.md)
- [Stage-4 execution evidence](experiments/phase-05-full-geometry-v2/full-geometry-03a-mixture-08b-parity-baseline/stage-04/results.md)
- [Stage-5 inherited summary; detailed packet unavailable](experiments/phase-05-full-geometry-v2/full-geometry-03a-mixture-08b-parity-baseline/index.md#current-status)
- [Phase-06 Full Geometry with Brine Pool contract](experiments/phase-06-full-geometry-with-brine-pool/setup.md)
- [Phase-06 Stage-01 setup](experiments/phase-06-full-geometry-with-brine-pool/stage-01-level-observable-and-outlet-response/setup.md)
- [Phase-06 pre-decision results](experiments/phase-06-full-geometry-with-brine-pool/results.md)
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

**Human decision as of 2026-09-08.** The full geometry is too complex to
remain the immediate development platform. Phase 06 is therefore concluded
for now, and the project is returning to the simplified Purnanto geometry.

## What remains unresolved?

- the exact brine-pool-surface elevation in the real separator and its mapped
  coordinate in the simplified Purnanto geometry;
- which numerical mechanism can remove liquid at the truncated bottom without
  unacceptable steam loss, phase-routing distortion, mass imbalance, or
  numerical instability;
- how the candidate methods should be compared and what evidence is sufficient
  to select one; and
- which external, analytical, or measured targets would eventually support a
  physical validation claim.

## What happens next?

**Phase 06 is concluded for now by explicit human direction.** Its blocked
lifecycle record is retained as historical evidence rather than silently
upgraded to a completed physical validation.

Phase 07 must first establish the exact geometry cut plane and then use
`phase-grill` to capture and approve any bottom liquid-removal candidates for
the simplified Purnanto model. Pragmatic numerical workarounds are permitted,
but each must make its intervention, tuning, artefacts, conservation behaviour,
claim limits, and decision gate explicit before it can be retained.

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
