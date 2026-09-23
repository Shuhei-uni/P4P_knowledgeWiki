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
- **Shuhei — Phase 7.2A:** starting from the completed 7.1A R0 control, can
  wall roughness or Eulerian Wall Film reduce phase-2 liquid carryover through
  `steamoutlet` while preserving absorber tracking, mass closure, liquid
  inventory behaviour, and credible vapor routing?
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

**Phase 7.2A was created by the human on 2026-09-22.** Its starting baseline
is the verified terminal Phase 7.1A R0 Coupled / Global-Time-Step continuation,
not the earlier prepared v2 pair. The baseline is the full-loading smooth-wall,
no-EWF endpoint with case SHA-256
`4fd493972839929f1f0922ad42679456d1f4aea294da86e4b13d6b7c32f754fc` and data
SHA-256 `b2261fac8626b2e338c3a9c80c334c8a910d1bfb536f782ef9234623f00e1a72`.
Its final native report/transcript state is iteration `5586`, with phase-2
`steamoutlet` flux `-24.3344 kg/s`; the absorber command remains matched to the
applied removal, and the run has useful late residuals without qualifying as
fully steady or physically validated. The historical R0 comparison ledger
still uses the expected `4580–5580` checkpoint window; 7.2A starts from the
final `5586` state.

The new phase screens wall roughness and EWF as separate mechanisms from this
developed endpoint. The old first-2,000-iteration v2 inlet ramp is not replayed
in 7.2A children, and the first screen does not combine roughness with EWF.
The current [Family E result](experiments/phase-07-2a-wall-liquid-routing/ewf-family/results.md)
has completed E0, basic-EWF E1, and the subsequently human-selected E1-plus-R3
interaction E3 at native 8586. E1/E3 formed no measured film; E2 phase
accretion diverged early, and a smaller-initial-film-step recovery reproduced
the FPE. E2 has no late-window comparison, so the film-capture question remains
open under a numerical block. The student Fluent endpoint became unresponsive
after that recovery FPE; Server 1 is not part of Family E execution.
See the [Phase 7.2A record](experiments/phase-07-2a-wall-liquid-routing/index.md),
[context](experiments/phase-07-2a-wall-liquid-routing/CONTEXT.md), and
[throughout-run monitoring contract](experiments/phase-07-2a-wall-liquid-routing/monitoring-contract.md).

Phase 7.1A remains the parent/evidence phase below; its prepared v2 pair,
loading history, and solver-control records are retained for provenance.

### Phase 7.1A parent evidence

Phase 7.1A is complete as the parent-development phase for Shuhei's 60k virtual
liquid outlet. The selected endpoint is the R0 smooth-wall run4 continuation at
native state `5586`: full loading, steady Coupled / Global Time Step, EWF off,
and the v2 phase-2-only throughput-controlled absorber.

It was promoted because the combined late behaviour was the strongest obtained
so far: liquid inventory was bounded and substantially more stable, mass closure
and continuity were the best obtained in the phase, absorber command tracking
remained exact, and the 1,000-iteration continuation completed without fatal
solver events.

This is **not** a claim of a fully converged or physically correct separator.
Multiphase/turbulence residuals remain oscillatory and phase-2 liquid carryover
through `steamoutlet` remains about `24.33 kg/s`. That unresolved routing error
is now the main target of Phase 7.2A.

The decision rule carried forward is therefore: preserve bounded inventory,
closure, continuity and absorber tracking first; then judge whether the new wall
mechanism improves phase routing. Lower residuals alone do not justify promotion
if the macroscopic behaviour becomes worse.

See the [Phase 7.1A parent record](experiments/phase-07-1a-absorber-convergence/index.md)
and the [Phase 7.2A baseline handoff](experiments/phase-07-2a-wall-liquid-routing/baseline-control-handoff.md).

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
and verified after reload. S20 completed its 5,000-iteration screen with all histories and final sections.
It did not achieve acceptable mass closure; S40, S60 and S80 also completed 5,000 iterations with final artifacts and full analyses;
none of the four meets the numerical criteria. S100 suffered numerical failure
at attempted N4183; all completed N1–4182 records and a labelled N4000 recovery
field set are preserved. The [G1 comparison](experiments/phase-07b-full-geometry-liquid-removal/results.md)
is complete; no case is qualified and check-ins stop. See the
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
- for Shuhei's Phase 7.1A, whether any later, separately authorized numerical
  treatment can improve the selected lower cell-zone absorber's scaled-residual
  and continuity behaviour while preserving bottom-only liquid removal and
  negligible direct vapor absorption;
- for Shuhei's Phase 7.1A, whether the finite turbulence-family differences
  persist over a declared qualification horizon or are dominated by pressure
  coupling, outlet reverse flow, source/local conditioning, or equation
  treatment;
- for Andy's Phase 7b, which separately authorized diagnostic could distinguish
  source-strength/coupling effects from collector coverage after the G1 screen;
- whether liquid reaches the collector and can be removed without unacceptable
  steam loss, phase-routing distortion, mass imbalance, or numerical instability;
- why the fixed-treatment Phase 7b cases retain strong mass imbalance and
  nonstationarity, including S100's numerical divergence; and
- which external, analytical, or measured targets would eventually support a
  physical validation claim.

## What happens next?

**Phase 06 is concluded for now by explicit human direction.** Its blocked
lifecycle record is retained as historical evidence rather than silently
upgraded to a completed physical validation.

Phase 7.1A's v2 60k virtual-outlet baseline is prepared, reopened, smoke-tested,
and loaded on `student`. The first 2,000 iterations of the v2 baseline are now
explicitly defined as a shared inlet-loading ramp from `0.25` to `1.00` of the
recorded `116.92 kg/s` liquid and `80.69 kg/s` steam targets, updated every 10
iterations. The immediate active planning direction is [Family N numerical
improvement](experiments/phase-07-1a-absorber-convergence/solver-improvement-family/index.md),
with roughness and EWF retained as later mechanism branches. Family N must
monitor the full loading, absorber, routing, closure, residual, warning, and
timing trajectory over the run; its detailed monitoring contract is recorded
in the family record. The old turbulence, solver-path, C7, and C8 packets
remain historical and are not eligible parents.
Andy's Phase 7b has verified its
five collector masks and PC/API paths and declared a common finite source
coefficient and evidence contract in its
[design](experiments/phase-07b-full-geometry-liquid-removal/design.md).
The approved five-case screen now has a complete G1 comparison: four
N5000 endpoints fail numerical criteria and S100 has a documented numerical
block at attempted N4183. Review its [results](experiments/phase-07b-full-geometry-liquid-removal/results.md)
before authorizing any new scientific treatment. Shuhei's Phase 7
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
these preparation checks were followed by the completed G1 discovery screen
linked above; no credible steady collector solution was established.

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
