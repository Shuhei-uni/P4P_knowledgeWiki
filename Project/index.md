# Project

This is the default entry point for the project's current scientific truth.
`Project/` owns the question being pursued, stable model assumptions, selected
experiments, evidence interpretation, and claim limits. Reusable CFD knowledge
belongs in `CFD_wiki/`; executable implementation and machine evidence belong
in `PyAnsys/`.

## What are we trying to answer now?

The liquid-removal work has two separate planning lanes:

- **Shuhei — Phase 07A:** what practical numerical mechanism can remove
  separated liquid from the truncated simplified Purnanto model while
  preserving useful and interpretable separation behaviour?
- **Shuhei — Phase 7.1A:** can the selected lower cell-zone absorber reach
  credible scaled-residual and continuity convergence when the remaining
  solver/model treatments are changed one at a time?
- **Andy — Phase 7b:** can a function-based ideal liquid collector in the lower
  full-geometry vessel support a balanced, numerically stable steady-state
  solution while preserving useful separation above the collector?

Andy's Phase 7b retains the lower brine geometry and explicitly does not require
a standing pool. Shuhei's Phase 07A and Phase 7.1A retain the
simplified-geometry scope. Each
phase has its own planning authority; neither supersedes the other. The
human-supplied Phase 7 mesh is accepted as the intended truncated geometry; its
steam-outlet diameter is `0.876 m`, correcting the former Project value of
`0.724 m`.

## Active/latest experiment

Shuhei's Phase 07A mechanism-discovery record is retained as historical
evidence. The lower cell-zone, phase-2-only absorber is now the human-selected
working removal path, but it is not yet physically qualified or numerically
converged. Phase 7.1A is the new planning phase for convergence and solver
stability. Its purpose is to keep the absorber mechanism fixed while changing
the remaining solver/model treatment one controlled step at a time. E0 is
human-approved as the
corrected fixed-mesh reference experiment, with an initial `2,000`-iteration
discovery horizon. Its server-neutral setup and the human-approved five-family,
15-child fixed-mesh treatment series are complete. Dependency-gated execution
of all 15 initial child packets has now been attempted under explicit human
authorization: 10 produced their approved 500-iteration discovery artifacts,
two corrected E1 pressure cases blocked during smoke, and all three E5 packets
were capability-blocked before solve because the live Fluent tree exposes no
region-specific source binding. E0 and the completed treatment screens have
plot-led analyses and core figures. The one activated E2 fourth point (K=10)
also blocked during smoke. The activated E3 Q=146.15 and E4 G=1.50 fourth
points were subsequently rerun on the only reachable `student` Fluent
endpoint from their exact approved parents/checkpoint. Both completed their
500-iteration discovery screens and analyses; Q=146.15 retained positive
inventory drift/open mixture balance, while G=1.50 reached the command cap
with positive inventory drift. Discovery evidence remains finite-horizon and
inconclusive, and no qualification is authorized. The subsequently approved
E5-CZ-ABSORB lower-inventory family also completed its Phase Loop screen:
CAP14615 reached 500 iterations but missed its lower target and retained
positive global liquid drift, while CAP29230 and CAP58460 encountered verified
solver divergence during the block ending at active 450 after valid active-400
readbacks. No member is promoted; any stabilization change requires a separate
human decision. A separate [cold-start setup](experiments/phase-07a-simplified-purnanto-liquid-removal/cell-zone-absorber-control-family/p7-e5-cz-absorb-cold-ramp11692/setup.md)
was created from the E0-style initialized state with a ramp to
`116.92 kg/s` and completed its active-1,000 discovery horizon. The requested
[1,000-to-5,000 continuation](experiments/phase-07a-simplified-purnanto-liquid-removal/cell-zone-absorber-control-family/p7-e5-cz-absorb-cold-ramp11692-cont5000/results.md)
then reached a valid active-1,960 history before solver divergence in the
active-1,970 block; it did not produce an active-5,000 pair. Its valid history
shows continuing total-liquid buildup and negligible lower-zone liquid, so no
bounded branch or qualification claim is supported. An exact restart from the
durable active-1,900 pair reproduced the same epsilon/flow-field blow-up and
terminal Fluent node failure after the report-query wrapper issue was removed;
the frozen-settings continuation is therefore a repeatable numerical block.
After Fluent was relaunched, a third exact restart reproduced the same failure
on the new endpoint, confirming that the block is not tied to the prior Fluent
session.
The new Phase 7.1A planning record is:

- [Phase 7.1A convergence direction](experiments/phase-07-1a-absorber-convergence/index.md)
- [Phase 7.1A planning context](experiments/phase-07-1a-absorber-convergence/CONTEXT.md)

For
Andy's
Phase 7b, a function-based ideal
collector is the selected mechanism direction; its exact zone, source law,
parent, screening experiment and gate remain to be defined. The most direct
records are:

- [Shuhei's Phase 07A direction and boundaries](experiments/phase-07a-simplified-purnanto-liquid-removal/index.md)
- [Shuhei's Phase 07A planning context](experiments/phase-07a-simplified-purnanto-liquid-removal/CONTEXT.md)
- [Shuhei's Phase 07A supplied-mesh inspection](experiments/phase-07a-simplified-purnanto-liquid-removal/mesh-inspection.md)
- [Shuhei's Phase 07A E0 setup contract](experiments/phase-07a-simplified-purnanto-liquid-removal/e0-08b-corrected-reference/setup.md)
- [Shuhei's Phase 07A E0 execution result and blocker](experiments/phase-07a-simplified-purnanto-liquid-removal/e0-08b-corrected-reference/results.md)
- [Shuhei's Phase 07A fixed-mesh treatment series](experiments/phase-07a-simplified-purnanto-liquid-removal/fixed-mesh-treatment-screen/index.md)
- [Shuhei's Phase 07A campaign design](experiments/phase-07a-simplified-purnanto-liquid-removal/fixed-mesh-treatment-screen/design.md)
- [Shuhei's Phase 07A cell-zone recovery family](experiments/phase-07a-simplified-purnanto-liquid-removal/cell-zone-treatment-family/design.md)
- [Shuhei's Phase 07A absorber-control family](experiments/phase-07a-simplified-purnanto-liquid-removal/cell-zone-absorber-control-family/index.md)
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

- for Shuhei's Phase 7.1A, whether the selected lower cell-zone absorber can
  reach credible scaled-residual and continuity convergence while preserving
  bottom-only liquid removal and negligible direct vapor absorption;
- for Shuhei's Phase 7.1A, which numerical, pressure-coupling, turbulence, or
  phase-treatment change is responsible for improving or degrading residual
  behaviour when changed one at a time;
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

Phase 7.1A must first define its controlled convergence screens and evidence
gate; it does not yet have an executable setup queue. Andy's Phase 7b must
define the collector region and exact reference, then use
`phase-grill` to sharpen the selected function-based mechanism into an
interpretable screening experiment. The intervention, tuning, artefacts,
conservation behaviour, claim limits and decision gate must be explicit.
Any numerical collector elevation must be declared honestly. Shuhei's Phase 7
retains the original E0--E4 fixed-mesh campaign as the comparison record and
now executes the human-approved E5 cell-zone recovery family. The first
student-server split placed `3,794` lower cells in a second fluid zone without
changing solver mesh counts, extents, volume/face statistics, or mesh-check
status. Corrected G025 completed the full screen but did not improve the E0
inventory trend; recovered G050 and fresh G100 are now also complete with the
corrected `get_sum` source audit. G050 has the smallest provisional late
inventory slope, but all three gains retain positive inventory drift and open
boundary-only closure. No qualification path is authorized. Patching or reset
remains a human-only last resort and is not an autonomous prompt. The cold-start
fixed-rate continuation is now a verified execution block with a durable
solver-divergence limitation; any stabilization, instrumentation repair, or
altered absorber law requires a separate human-approved setup. Experiment
selection and gates belong to each phase's own `CONTEXT.md`.

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
