# Project

This is the default entry point for the project's current scientific truth.
`Project/` owns the question being pursued, stable model assumptions, selected
experiments, evidence interpretation, and claim limits. Reusable CFD knowledge
belongs in `CFD_wiki/`; executable implementation and machine evidence belong
in `PyAnsys/`.

## What are we trying to answer now?

The liquid-removal work has two separate planning lanes:

- **Shuhei — Phase 7:** what practical numerical mechanism can remove separated
  liquid from the truncated simplified Purnanto model while preserving useful
  and interpretable separation behaviour?
- **Andy — Phase 7b:** can a function-based ideal liquid collector in the lower
  full-geometry vessel support a balanced, numerically stable steady-state
  solution while preserving useful separation above the collector?

Andy's Phase 7b retains the lower brine geometry and explicitly does not require
a standing pool. Shuhei's Phase 7 retains its simplified-geometry scope. Each
phase has its own planning authority; neither supersedes the other. The
human-supplied Phase 7 mesh is accepted as the intended truncated geometry; its
steam-outlet diameter is `0.876 m`, correcting the former Project value of
`0.724 m`.

## Active/latest experiment

Both phases are in planning. In Shuhei's Phase 7, E0 is human-approved as the
corrected fixed-mesh reference experiment, with an initial `2,000`-iteration
discovery horizon; no bottom liquid-removal treatment is approved yet. Its
server-neutral setup is complete, but no execution is authorized until the
treatment series is defined. For Andy's Phase 7b, a function-based ideal
collector is the selected mechanism direction; its exact zone, source law,
parent, screening experiment and gate remain to be defined. The most direct
records are:

- [Shuhei's Phase 7 direction and boundaries](experiments/phase-07-simplified-purnanto-liquid-removal/index.md)
- [Shuhei's Phase 7 planning context](experiments/phase-07-simplified-purnanto-liquid-removal/CONTEXT.md)
- [Shuhei's Phase 7 supplied-mesh inspection](experiments/phase-07-simplified-purnanto-liquid-removal/mesh-inspection.md)
- [Shuhei's Phase 7 E0 setup contract](experiments/phase-07-simplified-purnanto-liquid-removal/e0-08b-corrected-reference/setup.md)
- [Andy's Phase 7b direction and boundaries](experiments/phase-07b-full-geometry-liquid-removal/index.md)
- [Andy's Phase 7b planning context](experiments/phase-07b-full-geometry-liquid-removal/CONTEXT.md)
- [Phase-06 human-directed conclusion](experiments/phase-06-full-geometry-with-brine-pool/conclusion.md)
- [Historical liquid-sink evidence and accounting corrections](experiments/parallel-andy-studies/closed-bottom-liquid-sinks.md)
- [Historical resolved-outlet and transient VOF evidence](experiments/parallel-andy-studies/resolved-brine-outlet.md)

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

The separate historical resolved-outlet lane did switch to transient VOF.
Its short, very low-feed drainage success did not persist in later holds.
Earlier steady closed-bottom liquid sinks also failed to establish accepted
stability windows; the preserved notes identify limited liquid availability
in the sink band and a corrected source-accounting error. These are related
diagnostics with distinct meshes and parents, not one continuous experiment.

**Human decision as of 2026-09-08.** Phase 06 remains concluded for now.
Shuhei's Phase 7 pursues simplified-geometry liquid removal. Andy's separate
Phase 7b retains full geometry with an ideal liquid collector and requires
steady state. A standing pool is explicitly not required in Phase 7b.

## What remains unresolved?

- for Shuhei's Phase 7, solver-side mesh quality and live Fluent topology
  readback, removal candidates, and the screening gate;
- for Andy's Phase 7b, the exact full-geometry mesh/parent, collector location and extent, and
  treatment of the former brine outlet;
- whether liquid reaches the collector and can be removed without unacceptable
  steam loss, phase-routing distortion, mass imbalance, or numerical instability;
- the source law and coupling, numerical screening horizon, comparison and
  acceptance gate; and
- which external, analytical, or measured targets would eventually support a
  physical validation claim.

## What happens next?

**Phase 06 is concluded for now by explicit human direction.** Its blocked
lifecycle record is retained as historical evidence rather than silently
upgraded to a completed physical validation.

Andy's Phase 7b must define the collector region and exact reference, then use
`phase-grill` to sharpen the selected function-based mechanism into an
interpretable screening experiment. The intervention, tuning, artefacts,
conservation behaviour, claim limits and decision gate must be explicit.
Any numerical collector elevation must be declared honestly. Shuhei's Phase 7
will next build the approved E0 08b-derived reference on the accepted mesh,
including the corrected steam-outlet turbulence/backflow length scale. Its
`2,000`-iteration discovery history will establish the comparison scale before
`phase-grill` is used to approve any bottom liquid-removal candidate.
Experiment selection and gates belong to each phase's own `CONTEXT.md`.

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
