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
- **Shuhei — Phase 7.1A:** can the 60k-mesh, phase-2-only virtual liquid outlet
  track commanded liquid-inlet throughput while preserving credible phase
  routing, source-inclusive mass closure, bounded inventory behaviour, and
  useful steady convergence?
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

**Phase 7.1A was redirected by the human on 2026-09-22.** The active baseline
is now [v2 on the supplied 60k mesh](experiments/phase-07-1a-absorber-convergence/baseline-v2-virtual-liquid-outlet/results.md).
It replaces the v1 lower-inventory/uniform absorber with a feed-forward virtual
liquid outlet whose command is the phase-2 liquid-inlet throughput and whose
local source is weighted by phase-2 volume fraction. The prepared/reopened pair
is verified and loaded on `student`: `60,964` total fluid cells, including a
`715`-cell lower virtual-outlet zone. Its one-iteration setup smoke passed, but
the fresh lower zone was liquid-starved, so throughput tracking and convergence
remain untested. Earlier Phase 7.1A records with `results.md` are historical;
the C7/C8 direction is superseded.

Shuhei's Phase 07A mechanism-discovery record is retained as historical
evidence. The lower cell-zone, phase-2-only absorber is now the human-selected
working removal path, but it is not yet physically qualified or numerically
converged. Phase 7.1A now focuses on liquid-field development and artificial
bottom-boundary routing: retain the absorber, develop both inlet phases from
reduced conditions to base flow on the 237k thin-outer mesh with every bottom
band closed, then assess a delayed thin-outer-ring pressure intervention using
phase-resolved evidence. E0 is
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
On 2026-09-15 the human authorized a separate E6 localized bottom-boundary
diagnostic: partition the existing planar bottom into reusable radial bands,
retain the inner bands as walls, and start with the outermost resolved band as
a pressure outlet. The [E6 design packet](experiments/phase-07a-simplified-purnanto-liquid-removal/ringed-bottom-pressure-outlet-family/index.md)
records the five-band catalogue, the three reused E1 pressure points, and the
hard disposable face-zone/save-reopen gate. It is design-ready but not placed
or executed; the pressure outlet remains a phase-permissive diagnostic, not an
assumed liquid-only drain.
The new Phase 7.1A planning record is:

- [Phase 7.1A convergence direction](experiments/phase-07-1a-absorber-convergence/index.md)
- [Phase 7.1A planning context](experiments/phase-07-1a-absorber-convergence/CONTEXT.md)

The earlier Phase 7.1A turbulence-first finite screen is execution-complete and
is retained as historical v1 evidence.
T0 RNG reference, T1 standard k-epsilon, and T1 realizable k-epsilon ran in
order on `student` from the exact active-1000 absorber parent, each with 500
active iterations, paired final artifacts, and plot-led evidence. The closures
produced distinct finite trajectories, but all retained nonstationarity,
reverse flow, and broad turbulent-viscosity limiting; no branch is qualified
or promoted. The unrun T2-T4 and Coupled/Global-Time-Step packets are now
superseded as active candidates and retained only as planning history. The
former low-to-base inlet-development and delayed thin-outer-ring families are
also superseded by the 2026-09-22 v2 virtual-outlet reframe. Their staged
[C7/C8 plan](experiments/phase-07-1a-absorber-convergence/liquid-development-and-dynamic-ring-family.md)
is historical and is not execution authority.

The human has also raised a Phase 7.1A-specific long-horizon planning
hypothesis from the current extended runs: steady-state assessment may not be
meaningful until at least roughly `4,000` solver iterations, with a plausible
separator operating inventory near `2,000 kg`. This is recorded as a maturity
and operating-point marker—not as a generic Fluent requirement, a convergence
criterion, or a physical conclusion. The steady-state gate remains conjunctive:
late-window boundedness and slope, residual behaviour, phase-resolved and
mixture mass closure including storage/source terms, and credible phase routing
must all be demonstrated.

For Andy's Phase 7b, a function-based ideal collector with five thickness
cases (`20%, 40%, 60%, 80%, 100%`) is approved, with at most `5,000` steady
iterations per case, DPM/EWF off, and the same fresh initialization without a
patched pool. Its maximum top is the historical cut plane / assumed pool
surface. The clean Python-only reference, save/reopen and source-free smoke passed.
The Cortex fault was reproduced in phase-velocity expression syntax and avoided
with component-first syntax; all three components match native phase reports
at nonzero slip. Corrected collector expressions completed a 50-iteration
startup diagnostic with complete histories. Exact mask-face flux recording
also passed its live smoke. The API has recovered and the S20 report-context error is corrected, saved
and verified after reload. S20 is resuming its approved screen; no
5,000-iteration case is complete yet. See the
[technical diagnostics](experiments/phase-07b-full-geometry-liquid-removal/diagnostics.md).
Gate G1 returns the comparative observations to Andy. The selected condition
is steady Mixture/RNG physics with Energy off and full-feed `1600 kJ/kg`,
supplied through separate liquid and steam inlet faces using the earlier
equal-velocity split design, with the physical brine outlet closed as a wall.
The most direct
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
- [Shuhei's Phase 07A localized radial-band pressure-outlet family](experiments/phase-07a-simplified-purnanto-liquid-removal/ringed-bottom-pressure-outlet-family/index.md)
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

- for Shuhei's Phase 7.1A, whether the v2 virtual outlet can realize its
  inlet-throughput command after liquid reaches the lower zone, without direct
  vapor deletion or unacceptable source-inclusive imbalance;
- for Shuhei's Phase 7.1A, whether the v2 60k branch can reach bounded liquid
  inventory and credible steady numerical behaviour after the outlet is no
  longer starved;
- for Andy's Phase 7b, API/session recovery, complete reference phase-interaction
  readback, collector source/velocity implementation and file-backed instrumentation;
- whether liquid reaches the collector and can be removed without unacceptable
  steam loss, phase-routing distortion, mass imbalance, or numerical instability;
- verified source coupling and persistence before the approved five-case,
  5,000-iteration screen and G1 review; and
- which external, analytical, or measured targets would eventually support a
  physical validation claim.

## What happens next?

**Phase 06 is concluded for now by explicit human direction.** Its blocked
lifecycle record is retained as historical evidence rather than silently
upgraded to a completed physical validation.

Phase 7.1A's v2 60k virtual-outlet baseline is prepared, reopened, smoke-tested,
and loaded on `student`. The next Phase 7.1A action is a predeclared discovery
run from that exact pair with native applied-source, command, liquid-availability,
inventory, phase-routing, closure, and residual evidence. The old turbulence,
solver-path, C7, and C8 packets remain historical and are not to be executed.
Andy's Phase 7b has verified its
five collector masks and PC/API paths and declared a common finite source
coefficient and evidence contract in its
[design](experiments/phase-07b-full-geometry-liquid-removal/design.md).
Complete the first fully instrumented child and execute the approved five-case
screen with the verified Python-only source and exact-face recording route.
Shuhei's Phase 7
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

For Phase 7b, the resolved-outlet study's 620,431-cell mesh has been copied to
Extreme SSD and its SHA-256 verified. The copied PC phase folder under
`C:/Users/qtra338/P4P/experiments/` was verified accessible through Fluent/PyFluent,
with output text round-trips and a historical compiled source-free geometry
probe. Fresh-process clean N3 reload and client-exit preservation are now verified;
this establishes current recovery, not a runnable collector.

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
