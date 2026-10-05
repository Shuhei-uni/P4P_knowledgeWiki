# Project

This is the default entry point for the project's current scientific truth.
`Project/` owns the question being pursued, stable model assumptions, selected
experiments, evidence interpretation, and claim limits. Reusable CFD knowledge
belongs in `CFD_wiki/`; executable implementation and machine evidence belong
in `PyAnsys/`.

## What are we trying to answer now?

**Shuhei — Phase 8 storyline reconstruction:** reproduce the historical simulation steps leading to the current model; closing mass imbalance and reducing continuity are diagnostics, not the phase goal or progression gates. Create five reproducible run families on the
existing 60k simplified mesh to compare one-inlet and split-inlet carriers,
one-way and two-way DPM, five Phase 8 inlet-speed points (`20.11`, `23.46`,
`26.81`, `29.48`, and `32.14 m/s`), injected
DPM shares of 2.5%, 5%, 7.5%, 10%, and 20% of inlet liquid, and EWF with
common report definitions. F0 separates the existing mixed-inlet SIMPLE series from Coupled F1. Families 0–4 have no
absorber; the finalized Phase 7.2A setup will later be rerun at matching
points for an absorber-equipped comparison. This is a new-mesh storyline
series, not a quantitative replay of historical results. See the [Phase 8
context](experiments/phase-08-storyline-reconstruction/CONTEXT.md) and
[common report contract](experiments/phase-08-storyline-reconstruction/report-contract.md).
The [Phase 8 result](experiments/phase-08-storyline-reconstruction/results.md) brings together family plots, native spatial views and the reconstructed model-development storyline. The bounded Server 1 batch is verified complete: five matched F3/F4 points each at N16000, with a uniform final-500 comparison. Phase 8 is paused at that boundary.

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

| Current Phase 7.2A lane | Scope and authority | Record |
| --- | --- | --- |
| Stage 2 adaptive-film development | Server 3; verified N45606 transfer; aggressive-step probes and inner-film repair | [Continuation setup](experiments/phase-07-2a-wall-liquid-routing/stage-02-combined-ewf-roughness/aggressive-server3/setup.md) |
| Stage 3 early Coupled/EWF startup | Server 1; exact A bulk fields; R3/contact model; 500 low-feed updates before the original ramp | [Startup setup](experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/setup.md) |
| Stage 3 shortened reconstruction | Server 3; N8000 adaptive continuation complete; carrier scalars close; film 14.09% of reference; continuity remains high | [Stage 3 setup](experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/setup.md), [results](experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/results.md) |

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
The [Family E result](experiments/phase-07-2a-wall-liquid-routing/ewf-family/results.md)
now includes E2.7 and its additional 5,000-iteration continuation to native
N13586. With phase accretion and coupled film equations on, but Flow Momentum
Coupling off, its exported histories show bulk liquid mass near 63 kg and
liquid carryover near 1.734 kg/s. Film mass increases 3.111→5.842 kg and film
speed 46.34→82.41 m/s. This establishes film development, not steady drainage
or complete conservation. The five committed histories can be independently
checked; the linked full native run bundles are absent from this checkout.
The [26 September cross-branch review](experiments/phase-07b-full-geometry-liquid-removal/convergence-investigation/phase-review-2026-09-26.md)
records this distinction, a roughness-run mixture-ledger double count, and
remaining provenance and drainage questions. Older E0/E1/E3 zero-film results
and E2 recovery failures remain historical evidence, not the current frontier.
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

The independent [R0 audit](experiments/phase-07b-full-geometry-liquid-removal/convergence-investigation/shuhei-audit.md)
also reconstructs approximately 20.8% liquid and 12.1% native-mixture terminal
error from the available reported terms. Its historical promotion is a
development-parent decision, not evidence that the absolute balances close.

The decision rule carried forward is therefore: preserve bounded inventory,
closure, continuity and absorber tracking first; then judge whether the new wall
mechanism improves phase routing. Lower residuals alone do not justify promotion
if the macroscopic behaviour becomes worse.

See the [Phase 7.1A parent record](experiments/phase-07-1a-absorber-convergence/index.md)
and the [Phase 7.2A baseline handoff](experiments/phase-07-2a-wall-liquid-routing/baseline-control-handoff.md).

Andy's **Phase7b is closed by his direction on29 September2026, with no qualified case**. [Phase closure](experiments/phase-07b-full-geometry-liquid-removal/closure.md) records the final evidence and limits. G1–G7 are complete; E7 reachedN5000 with verified histories/spatial evidence but liquid/vapor/native-mixture mean absolute closure errors148.213/1.776/87.000%, inventory increase15.195% and continuitymaximum1.3222. E8 was stopped and preserved atN128 before its first conditioning gate; it is an incomplete startup test, not a failed gate. No further Phase7b run or qualification is authorized, both supervision automations are paused, and no new physical phase is selected. Other owners' phases remain separate.

The [26 September review](experiments/phase-07b-full-geometry-liquid-removal/convergence-investigation/phase-review-2026-09-26.md)
recommended a bounded finish, which Andy accepted on 28 September: complete E7,
audit source treatment, then at most one justified documented startup contrast
if needed, followed by bounded qualification or closure of the tested route.
The [current contract](experiments/phase-07b-full-geometry-liquid-removal/CONTEXT.md)
owns that execution envelope; no new physical phase is selected. Full feed, steady Mixture/RNG, Energy/DPM/EWF
off, the full geometry and closed physical brine wall remain the model.
A standing pool is not required. The ideal collector is a numerical removal
mechanism, not a physical drainage model.

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

## Historical predecessor findings

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

- Whether completing E7 and one isolated startup treatment can establish
  source-inclusive phase/native-mixture closure and stationary inventory in
  the full-geometry ideal-collector model.
- The expression sink's implicit derivative and the cause of the large
  above-collector phase deficit; exact recording and normalized fractions do
  not settle these questions.
- Whether Phase 7.2A's film reaches a documented external drain with a complete
  bulk/film/source ledger and bounded film inventory, and whether its omitted
  reciprocal flow feedback materially changes routing.
- Whether any numerically qualified result agrees with external pressure-drop,
  carryover, brine-flow or separation measurements. No branch is externally
  validated merely by low residuals or source-command tracking.

## What happens next?

Phase7b requires no further simulation. Its [closure](experiments/phase-07b-full-geometry-liquid-removal/closure.md) supports a bounded negative result for the tested route, without claiming that no steady solution exists. A new scientific direction needs its own phase framing and user selection.

For wall-film work, first recover the native evidence, correct the derived
mixture ledger and verify film discharge and combined conservation within
existing Phase 7.2A. A full-geometry film/drainage model changes the physical
representation and needs its own human-framed phase; it is not selected here.
Phase 06 remains concluded. Each phase's `CONTEXT.md` and machine state own
actual authority and progress; historical setup instructions are not new jobs.

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
