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
- [Phase-06 Stage-01 results](experiments/phase-06-full-geometry-with-brine-pool/stage-01-level-observable-and-outlet-response/results.md)

The earlier Project experiment records preserve the migrated setup and result
memory for the Purnanto, full-geometry, DPM, EWF, VOF, and reconstruction
families. Their historical status is part of the evidence; they are not
silently upgraded to current conclusions.

## What did the latest experiment show?

The first Phase-06 short fixed-pressure reference is complete. Its retained
native report histories show continued growth in total and lower-region
phase-2 liquid mass and a positive phase-liquid net rate; the short screen
remained materially mass-unclosed. The lower-region liquid-mass reports are
useful inventory-response proxies, but they are not a calibrated pool level or
instrument signal. Residual history was unavailable after reconnecting, so no
convergence claim is made.

This result confirms why a fixed pressure outlet must be treated as a
reference condition, not the real separator's level-control mechanism.

## What remains unresolved?

- whether the F11-derived model can represent the real brine-pool level and
  its measurement location with a defensible geometric/phase observable;
- whether an explicitly specified level-control outlet condition can establish
  a controlled steady operating point with credible residuals and phase flows;
- whether any resulting remaining drift is caused by retained model form,
  setup fidelity, or a requirement for time-dependent control modelling;
- whether the rebuilt case is truly at parity with the audited Purnanto carrier
  settings apart from its declared project change;
- which external, analytical, or measured targets are appropriate for a
  validation claim;
- whether later DPM evidence is complete enough to support more than a bounded
  carryover diagnostic.

## What happens next?

Phase 06 has now completed that matched steady outlet-vent resistance screen.
At the deliberately non-plant-calibrated `K=10`, it substantially reduced
liquid brine drainage and worsened liquid accumulation, liquid carryover, and
the retained imbalance indicators. The screen rules out that exact arbitrary
resistance representation as a controlled-pool candidate; it does not select a
different coefficient or make any claim about the real valve. The next step is
geometry-to-level mapping and a physically specified outlet/feedback relation,
not another arbitrary resistance or fixed-pressure sweep.

Actual plant level setpoint, measurement position, level band, outlet
hardware/line characteristic, downstream condition, and controller behaviour
remain required before any model can claim physical level-control fidelity.

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
