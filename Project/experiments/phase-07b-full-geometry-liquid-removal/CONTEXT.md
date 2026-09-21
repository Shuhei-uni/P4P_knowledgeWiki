# Phase Context — Phase 7b Full-Geometry Steady Liquid Removal

## Status

- **Planning state:** selected screen; API recovered and speed-report repair saved/reopened; S20 resuming
- **Owner:** Andy; separate from Shuhei's Phase 7
- **Last human review:** 2026-09-08
- **Experiment-selection authority:** human-approved-context-only
- **Current decision:** retain the full geometry and investigate a function-based
  liquid-removal zone as an ideal collector in a strictly steady-state model.
  Compare multiple collector thicknesses, with the maximum upper elevation at
  the historical model cut plane representing the assumed pool surface. A
  standing brine pool is not required. Close the physical brine outlet as a
  wall. Five thicknesses (`20%, 40%, 60%, 80%, 100%`) and the carrier-only
  reference are approved, with at most `5,000` steady iterations per case.
  Finish technical preparation and return the comparative evidence to the
  human. Collector coordinates are established; source implementation and
  complete live case readiness remain open.

## Human thinking

### Current intent

The human considers the explicit brine-pool/outlet work too complicated and
does not want a transient model. The selected alternative retains the full
vessel geometry, including its lower brine region, but uses a function to
remove liquid entering a designated zone. The human explicitly selected an
ideal collector with no requirement to preserve a standing pool.

The human clarified that the historical `0.05%` feed tests belonged to the
full-geometry investigation that explicitly represented the water pool and
brine outlet. Phase 7b is motivated by the complexity of that approach and
seeks liquid removal without explicitly resolving the collection/drainage
process. Those tiny-feed diagnostics are not a selected Phase-7b operating
point.

The human selected the reference-model physics and operating condition, with
Energy off, while retaining the full mesh's split inlet. Use the audited
steady pressure-based Mixture/RNG k-epsilon reference as the settings basis,
with liquid `116.92 kg/s` and vapour `80.69 kg/s` (the `1600 kJ/kg` condition).
The human clarified that the intended inlet is Shuhei's earlier equal-velocity
pure-phase split: both faces use velocity-inlet boundaries, with areas sized
to recover the reference phase flows at one common speed. Use that split-inlet
design and its consistent material basis for the inlet adaptation; the
historical 07g mass-flow implementation does not override this direction.
The two phases enter through separate faces on this geometry, unlike the
reference's single face carrying both phases. The human does not want the
transient low-feed study to drive this phase's setup or development path,
given the available timeframe.

The human selected closing the physical brine-outlet face as a wall, leaving
the collector function as the only intended lower liquid-removal mechanism.
The steam outlet remains the reference pressure-outlet route; liquid
carryover there must still be measured.

The human selected five cases varying the collector region's vertical
thickness at `20%, 40%, 60%, 80%, 100%` of the common lower-datum-to-cutoff
span, covering the fluid region below each top. The largest region may extend
up to the old truncated-model cut
plane associated with the water-pool assumption; no collector may extend above
that cap. The [geometry proof](geometry-proof.md) maps the historical cutoff
to `y=+0.020 m`, using `y_b=-1.4845837354660034 m` as the numerical lower datum.
The historical assumed surface sets a numerical removal boundary here;
it does not reintroduce a requirement to preserve a standing liquid pool.

The human approved a carrier-only screen with DPM and EWF off, the same fresh
initialization for every case, and no deliberately patched standing pool.
Each case may advance up to `5,000` steady iterations, followed by review of
what happened. Total water volume and whether it changes, residual histories,
and conservation of mass are expressly required. Results and observations
must be documented using the existing Project experiment-record structure.
The human authorized finishing technical preparation; no longer continuation
or new experimental family is approved by this instruction.

Phase 7b is Andy's separate full-geometry investigation. Shuhei's
[Phase 7](../phase-07a-simplified-purnanto-liquid-removal/CONTEXT.md) continues
to own the simplified, truncated Purnanto direction. Neither phase supersedes
the other. Phase 06 remains concluded with its historical evidence intact.

### Ideas raised by the human

| ID | Human idea | Why it seems worth considering | Status |
| --- | --- | --- | --- |
| H1 | Keep the full geometry and replace reliance on the physical brine outlet with a function that removes liquid entering a defined zone. | Seek steady liquid removal while simplifying the pool/outlet representation. | Selected through E1; five-case design recorded, implementation verification pending |
| H2 | Compare five collector thicknesses at 20%, 40%, 60%, 80%, 100% of the lower-datum-to-historical-cutoff span. | Determine how collector extent affects liquid removal and steady behaviour. | Human-approved five-case carrier-only screen; up to 5,000 iterations per case |

### Constraints expressed by the human

- Use Python/PyFluent instead of a C implementation (human direction, 2026-09-08).
  Investigate native Fluent expressions configured through the Settings API;
  no new C collector compilation or attachment. This route still requires
  live source, phase-velocity, instrumentation and persistence verification.
- Keep the full geometry, including the lower brine region.
- Use steady state; switching to a physical transient formulation is outside
  the selected scope.
- Keep Energy off and use the audited reference's steady pressure-based
  Mixture model and RNG k-epsilon turbulence as the physics basis. Reconcile
  exact settings with the selected geometry during setup; do not inherit the
  transient low-feed case or its pool/outlet controls.
- Treat the removal region as an ideal collector; preserving or regulating a
  standing brine pool is not required.
- Target liquid water for removal.
- Close the physical brine-outlet face as a wall. Retain the reference steam
  pressure outlet and account for any liquid carryover through it. The source
  function is the only intended lower liquid-removal path.
- Vary collector thickness over multiple cases; the maximum upper elevation is
  the old model cut plane associated with the water-pool assumption. Exact
  source strength is specified in design.md; source coupling still requires
  live verification.
- Use DPM off and EWF off, with identical fresh initialization and no patched
  standing pool in all five cases.
- Limit each case to `5,000` steady iterations and return observations for
  human review. Preserve histories of water volume, residuals and mass balance;
  do not substitute an endpoint-only report.
- Hold the reference full-feed condition across the collector-thickness
  comparison: liquid `116.92 kg/s`, vapour `80.69 kg/s`, total `197.61 kg/s`,
  associated with `1600 kJ/kg` at `11.2 bara` separator pressure. Use the
  geometry's equal-velocity split inlet: pure liquid on the liquid face and
  pure vapour on the steam face, both normal-to-boundary velocity inlets.
  Recover the intended common speed and consistent properties from Shuhei's
  split-inlet records, then verify `rho * U * A` against the phase-flow targets
  using the actual mesh areas. These mass rates are verification targets, not
  independently imposed mass-flow boundary conditions. Exact live names,
  areas, types, properties and phase assignments require readback before
  execution.

### Recovered split-inlet reference basis

The relevant design is [Phase 1 setup 07](../phase-01-purnanto-baseline-and-inlet-exploration/purnanto-07-pure-phase-actual-area/setup.md),
carried into the full-geometry velocity-inlet contract in
[Phase 2 setup 02c](../phase-02-parity-reset-and-pre-v2-qualification/full-geometry-02c-mixture-pressure-sensitivity/setup.md#31-inlet-contract).
These supply setup evidence; neither historical solution is promoted to a
qualified Phase-7b parent. The mass-flow 08b parity lane is a distinct inlet
choice. Reconcile the following recovered settings in the selected setup:

| Item | Reference basis for Phase 7b | Status |
| --- | --- | --- |
| Carrier physics | Steady pressure-based Mixture; vapour primary, liquid secondary; RNG k-epsilon; Energy off | Human-selected reference physics |
| Inlet velocities | `27.118 m/s` normal to each face | Recovered equal-velocity design; verify on staged mesh |
| Liquid volume fraction | Liquid face `1.0`; steam face `0.0` | Recovered pure-phase split |
| Constant liquid / vapour densities | `881.77 / 5.73 kg/m3` | Design-consistent material basis, differs from one-face audit |
| Constant liquid / vapour viscosities | `145.96e-6 / 15.188e-6 Pa s` | Recovered split-design material basis |
| Inlet turbulence | Intensity approximately `2.11%`; hydraulic diameter `0.01338 m` liquid and `0.72061 m` steam | Intended Phase-1 setup-07 fields; verify geometry and field identity |
| Gravity / operating pressure | `(0,-9.81,0) m/s2`; `0 Pa` | Reference basis |
| Steam outlet | Pressure outlet `1,120,000 Pa`; liquid backflow fraction `0` | Reference basis; verify outlet turbulence length scale from this geometry |
| Inlet pressure field | `1,140,000 Pa` reference/initial value | Historical velocity-inlet field, not an independently imposed inlet static pressure |
| Walls | Stationary, no slip, smooth; include former brine-outlet face | Reference wall basis plus human-selected brine closure |
| Numerics | SIMPLE, PRESTO!, Green-Gauss node-based gradients, second-order momentum/turbulence and QUICK phase fraction | Intended reference basis; reconcile exact controls in setup |

**Calculated using the exact mesh's reported areas:**
`881.77 * 27.118 * 0.0048896797 = 116.921233 kg/s` liquid and
`5.73 * 27.118 * 0.51928636 = 80.689903 kg/s` vapour. Both recover the target
flows to their stated two-decimal precision. Exact simultaneous equality is
not claimed from rounded speed, areas and material values.

**Observed mismatch to avoid:** the one-face audit densities
`881.21088 / 5.7974339 kg/m3` would give approximately
`116.847095 / 81.639508 kg/s` at the same speed and areas. The
[02c historical flux record](../phase-02-parity-reset-and-pre-v2-qualification/full-geometry-02c-mixture-pressure-sensitivity/historical-run-notes.md)
reports approximately these latter rates. Equal speed alone therefore does
not prove the target mass split; materials and areas must be checked together.

**Observed settings drift to avoid:** the [Phase-1 setup-07 technical extraction](../phase-01-purnanto-baseline-and-inlet-exploration/purnanto-07-pure-phase-actual-area/technical-extraction.md)
records steam-inlet viscosity ratio `0.72061` where the intended setup
specified hydraulic diameter `0.72061 m`, as well as Coupled/first-order
numerics and active DPM content. Do not replay those discrepancies as intended
Phase-7b settings. Use the declared split-inlet design with the selected
reference carrier physics; explicitly reconcile any remaining differences.

### PC handoff and implementation access

- **Human-directed:** the human will attach Extreme SSD to the Fluent PC and
  copy the Phase 7b folder to its local disk. The assistant will then interact
  with PC files through the Fluent API; direct PC filesystem, SSH, and shared
  drive access must not be assumed.
- **Observed:** the staged input is the resolved-outlet study's
  `brine-outlet-620kcells.msh.h5`, copied to
  `/Volumes/Extreme SSD/P4P/experiments/phase-07b-full-geometry-liquid-removal/inputs/`.
  Source and SSD copy SHA-256 both equal
  `0d75a86e53bc020aeefa4b13ef8616413a862b15646355d90d8037d1be888394`.
  The reported mesh size is 620,431 cells. This establishes the staged mesh
  identity, not a qualified case/data parent or steady solver configuration.
- **Prepared:** the SSD phase folder carries a relative input manifest, a
  human-run PC copy verifier, and input/output folders. Its README is a
  transfer guide; this context remains the scientific authority.
- **Execution route:** use `pyansys-workflow`, `fluent-fleet-orchestration`, and
  the existing PyFluent connection/file helpers. Check file existence through
  Fluent; prove writing, source access if needed, and save/reopen persistence
  on the live session before a selected run. Normal gRPC connectivity does
  not establish a separate binary file-transfer service.
- **Human-supplied and observed through Fluent:** PC phase root
  `C:/Users/qtra338/P4P/experiments/phase-07b-full-geometry-liquid-removal`;
  input mesh in its `inputs` subdirectory. The current configured server-1
  connects to Fluent 2025 R2. Endpoint credentials remain private in `.env`;
  server-2 is unconfigured. Directory existence, input-manifest readback and
  unique text write/read probes passed for case-data, reports, checkpoints,
  logs, exports and udf. Four remote project/mesh/case-data path entries are
  now populated; case/data input entries remain blank until a case exists.
- **Observed preparation state:** the user-specified mesh was loaded into the
  initially empty session. The approved Purnanto properties, equal-velocity
  pure-phase BCs, closed brine wall, gravity, Mixture/RNG and reference numerics
  have been applied. This is a preparation state, not a completed reference
  setup: phase-interaction readback, instrumentation and source coupling
  still need verification.
  Subsequent authorized technical checks completed hybrid initialization and
  ten source-free steady diagnostic iterations; no collector screen has run.
- **Observed:** a source-free on-demand diagnostic compiled and loaded through
  the 2025 R2 Settings API with the built-in compiler and ran across 16 fluid
  thread/partition instances. Its source text passed exact API round-trip
  readback using the new ASCII transfer helper. This proves a compiler and
  geometry-inspection route, not an implemented or persisted collector source.
- **Observed case persistence:** the uninitialized preparation case was
  saved as `case-data/phase07b-reference-preparation-uninitialized-20260908T055402Z.cas.h5`
  beneath the verified PC phase root. Strict reference-property/BC/numerics
  checks passed before save and after same-process reload, with equal captured
  state. This saved artifact predates the later hybrid initialization diagnostic. DPM
  interaction is off with no injections; EWF is off; all cell sources are off.
  This is a case-only preparation artifact, not a case/data parent, fresh
  Fluent-process verification or a run-ready collector. The exact machine
  readback is in `PyAnsys/output/phase07b_preparation/reference-preparation-save-reload.json`.
- **Observed phase-interaction readback:** after reload, the read-only
  `solver.rp_vars("domains")` route exposes a constant liquid secondary
  diameter of `1e-5 m`, Manninen slip and Schiller–Naumann drag. The corresponding
  Settings interaction branch is inactive in this Mixture state. These are
  observed settings; the droplet diameter
  is distinct from the inlet hydraulic diameters. The exact domain-property
  lists are retained in `PyAnsys/output/phase07b_preparation/phase-interaction-readback.json`.
- **Observed historical comparison:** the exact old truncated case in
  geometry-proof.md (SHA-256 `2771ef93c30518c5706688814474c3860e2693c2a70ed7893e5c82bcc9361b9c`)
  stores `9.999999747378752e-6 m` liquid diameter, Manninen slip and
  Schiller–Naumann drag in its actual HDF5 `settings/Rampant Variables`
  domains record. Those three properties match within serialization precision.
  The old record has Simonin turbulence interaction and
  `mp-turb-coupling-on?=true`; the current interaction entry is `none`.
  Its applicability is reconciled below; do not import a dormant setting.
- **Reconciled applicability:** the 2025 R2 Theory Guide limits Simonin
  turbulence interaction to Dispersed and Per Phase turbulence models
  ([section 14.5.18.3.1](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_sec_eulermp_theory_turbulence.html)).
  The selected model is the Mixture multiphase formulation with shared RNG
  turbulence; its dispersed/per-phase selector is inactive, and the live
  `mp-ke-type` is 0. Current `mp-turb-coupling-on?` is also true, matching the
  preserved old flag. **Inferred:** the old Simonin entry is not an active
  model requirement for this selected formulation. Keep the shared RNG model
  and current `none` interaction entry; do not enable a different turbulence
  formulation to reproduce that stored tuple. This resolves the identified
  applicability discrepancy, not a claim of every historical setting matching.
- **Remaining implementation checks:** independently verified PC mesh binary
  hash where available, full source-case persistence, actual collector source
  and phase velocity access, required report histories and run-specific
  paths. Populate canonical experiment run-paths.yaml after setup creation.

## Evidence anchors

- **Observed in preserved notes:** the earlier
  [closed-bottom sink studies](../parallel-andy-studies/closed-bottom-liquid-sinks.md)
  already tested steady liquid-only sinks. None established an accepted
  stability window. The completed first 07f matrix case retained 54.5553%
  corrected liquid imbalance; in 07e, available liquid in the band limited
  removal despite the minimum removal time scale. These used a different,
  closed-bottom mesh and do not determine the proposed full-geometry result.
- **Observed in preserved notes:** the separate
  [resolved brine-outlet studies](../parallel-andy-studies/resolved-brine-outlet.md)
  moved from Mixture to transient VOF. Brief drainage at very low feed did not
  persist; later 07n holds failed the sustained balance gate. This is the
  relevant transient predecessor, distinct from the F11 Phase-06 lane.
- **Observed:** [Phase-06 Stage-06](../phase-06-full-geometry-with-brine-pool/stage-06-long-horizon-surrogate-hypothesis/results.md)
  remained steady Mixture/RNG. Its final-window phase-liquid net rate averaged
  +16.10 kg/s after pressure saturation, and it did not establish a controlled
  numerical pool state. Residual-convergence evidence was unavailable.
- **Inferred:** whether liquid reaches the removal zone is a central
  uncertainty. Stronger removal alone did not qualify the historical small
  bottom-band approach. Changing zone coverage may help, but could also change
  separation above it; neither outcome is established.
- **Observed in preserved notes:** the resolved-outlet study's nominal inlet
  feeds were liquid `116.92 kg/s` and vapour `80.69 kg/s`. Those are historical
  model inputs now selected as the Phase-7b reference feed, not newly verified
  plant values.
  Later `0.05%` feed diagnostics do not establish performance at those nominal
  conditions.
- **Reported thermodynamic basis:** those phase feeds are the Purnanto
  `1600 kJ/kg` bulk specific-enthalpy condition at `11.2 bara` separator
  pressure, with total flow `197.61 kg/s`
  ([pressure/enthalpy source summary](../../../CFD_wiki/wiki/physics-basis/operating-pressure-enthalpy-and-phase-split.md),
  Purnanto 2013, p.5;
  [project inlet derivation](../phase-02-parity-reset-and-pre-v2-qualification/purnanto-08c-inlet-loading-sensitivity/inlet-regimes-interpretation.md#pure-phase-equal-velocity-split-calculation)).
  **Calculated:** the rounded flows imply inlet vapour mass fraction
  `80.69 / 197.61 = 0.40833`, approximately `40.83%`; this is inlet mass
  fraction, not volume fraction or outlet steam quality. Scaling both phase
  feeds to `0.05%` preserves this ratio; at the same thermodynamic basis,
  reducing throughput alone does not change the associated specific enthalpy.
- **Observed in the reference audit:** Energy was off; the saved reference
  enthalpy field was `1,600,000 J/kg`
  ([audit setup](../phase-01-purnanto-baseline-and-inlet-exploration/purnanto-00a-live-setup-audit/setup.md)).
  The bulk enthalpy identifies the prescribed inlet phase split. The
  reference-value field is not an active inlet energy boundary condition,
  and identifying this enthalpy does not imply enabling Energy, flashing,
  or transient modelling in Phase 7b.
- **Observed in the original full-mesh setup record:** the exact staged
  620,431-cell mesh has separate `liquid-inlet` and `steam-inlet` boundaries,
  with reported areas `0.0048896797 m2` and `0.51928636 m2`. Historical setup
  names were normalized to `liquidinlet` and `steaminlet`, supplying phase-2
  liquid `116.92 kg/s` and phase-1 vapour `80.69 kg/s`, respectively
  ([07g geometry and setup record](https://github.com/Shuhei-uni/P4P_knowledgeWiki/blob/archive/andy-local-20260908/Setup%20report/07g-split-inlet-resolved-brine-outlet-qualification.md)).
  The raw mesh tagged both faces as velocity inlets, but the prepared case's
  [inlet validator](https://github.com/Shuhei-uni/P4P_knowledgeWiki/blob/archive/andy-local-20260908/PyAnsys/scripts/setup/run_split_inlet_mesh_convergence.py#L441-L448)
  required two mass-flow inlets and zero imposed wrong-phase flow on each.
  Mesh boundary tags alone do not establish final inlet settings. **Missing Info:**
  live Phase-7b readback of names, areas, types, and phase assignments. This
  geometry/setup evidence does not qualify the failed 07g solution as a parent;
  its mass-flow inlet choice is superseded for Phase 7b by the human-selected
  equal-velocity inlet design above.
- **Observed in recovered archive records:** the old truncated mesh's bottom
  was at `y = -6.441 m` in its own coordinates
  ([07c source](https://github.com/Shuhei-uni/P4P_knowledgeWiki/blob/archive/andy-local-20260908/Setup%20report/07c-split-inlet-thickened-constant-water-level-liquid-sink.md)).
  The exact 620,431-cell full mesh separately used a `y <= 0 m` initial-pool
  patch inferred from the brine-outlet crown
  ([07h source](https://github.com/Shuhei-uni/P4P_knowledgeWiki/blob/archive/andy-local-20260908/Setup%20report/07h-split-inlet-resolved-brine-outlet-initial-liquid-pool.md)).
  The [two-artifact geometry proof](geometry-proof.md) now establishes the
  vertical offset `+6.461 m` from matching inlet edges and the independent
  steam-outlet plane. **Inferred:** the selected historical cap is therefore
  `y=+0.020 m` on the staged full mesh; it is distinct from the old `y<=0`
  initialization patch and Shuhei's newer zero-plane truncated geometry.
- **Observed through Fluent:** 620,431 owned fluid cells, zero invalid-volume
  cells in the diagnostic, total fluid volume `27.0630856948 m3` and five
  nonempty nested centroid selections. The 20/40/60/80/100% masks contain
  `21,516 / 41,258 / 59,465 / 78,608 / 98,519` cells and have geometric volumes
  `0.5612436425 / 1.4681621275 / 2.4628949897 / 3.3772762231 / 4.4017292439 m3`.
  These are geometric volumes, not water inventories. Pre-initialization data
  were invalid; no phase-velocity storage or source-readiness claim follows.
- **Missing Info:** complete fresh reference phase-interaction readback,
  source coupling/readback, complete instrumentation and source persistence.
  The common finite coefficient and numerical screening indicators are now
  declared in design.md as numerical conventions, not physical validation
  targets.

## Phase contract

### Phase question

> Can a function-based ideal liquid collector in a defined lower region of the
> full separator geometry remove separated water and support a balanced,
> numerically stable steady-state solution while preserving useful separation
> behaviour above the collector?

### Scope, invariants, and claim limit

- **In scope:** the human-selected collector-thickness comparison and its
  effect on liquid routing, inventory, steam loss, conservation, and separator
  flow. All tested collector tops remain at or below the historical cutoff.
- **Must remain fixed:** full-geometry scope, steady pressure-based Mixture/RNG
  reference physics, Energy off, reference full-feed targets and equal-velocity split-inlet
  phase routing, closed brine-outlet wall, and no requirement to preserve a
  standing brine pool.
- **Out of scope:** physical pool-level control, transient pool/interface
  dynamics, and validation of actual outlet hardware or downstream hydraulics.
- **Claim limit:** success would establish a computational liquid collector.
  It would not validate a physical brine pool or separator efficiency by itself.
- **Planning distinction:** retaining lower-vessel geometry does not imply
  retaining a physically representative liquid pool in that geometry.

### Useful evidence standard

A useful result must distinguish liquid reaching the collector from liquid
actually removed, account for the integrated sink exactly once in the liquid
and total mass balances, and retain steam-outlet phase fluxes, liquid inventory,
pressure/velocity behaviour, and residual histories. Removal coefficient and
zone extent must be explicit. The human selected a 5,000-iteration maximum;
numerical screening indicators are declared in design.md; implementation
proofs remain to be completed.

## Candidate experiment pool

| ID | Origin | Controlled delta | Screening question | Required evidence | Artifact/rejection signal | Human status |
| --- | --- | --- | --- | --- | --- | --- |
| E1 | H1 + H2 — human ideas | Five lower-region collector thicknesses at 20/40/60/80/100% up to the mapped y=+0.020 m cap; reference Mixture/RNG physics, Energy off, full-feed equal-velocity inlet and closed brine wall fixed; common source implementation pending. | How does collector thickness affect delivery, removal and establishment of a useful steady solution? | Transport into the region, integrated removal, phase and total closure, water-volume/mass histories, steam carryover/loss, pressure/velocity and residual histories. | Persistent imbalance/drift, insufficient liquid delivery, wrong-phase removal, or material distortion of separation above the collector. | Human-approved S20/S40/S60/S80/S100; up to 5,000 iterations each; G1 returns observations to human |

## Approved screening campaign

The human approved E1's five-case screen and G1 discovery review. Physical
tops and centroid volumes are established in [geometry-proof.md](geometry-proof.md)
and the live diagnostic evidence. The [design](design.md) defines the required
histories, figure plan, comparison windows and unresolved implementation checks.
Reconcile the selected reference physics with the split-inlet geometry and
closed brine wall, then prove the common source and instrumentation before
execution.
Historical failed sink cases are comparison evidence, not automatically
approved repeat runs.

### Human-approved screen details

- **Collector levels:** five cases at `20%, 40%, 60%, 80%, 100%` of the
  vertical span from a common lower datum to the mapped historical cutoff.
  Use all fluid cells below each top within the connected lower vessel and
  closed brine-pipe region; verify the intended footprint and mesh coverage.
  These percentages specify vertical thickness, not domain-volume fractions.
- **Initial screen scope:** carrier-only Mixture, DPM and EWF off, identical
  fresh initialization for every thickness, and no deliberately patched
  standing pool. This isolates the collector comparison from inherited fields
  and additional liquid representations.
- **Budget and evidence:** at most `5,000` steady iterations per case;
  comparison and return to human under G1. Required evidence includes total
  liquid volume and its iteration trend, residual histories, sink-inclusive
  phase/total closure, liquid mass, removal rate, and steam recovery/carryover
  behaviour. Numerical screening indicators will be declared before running;
  they do not independently authorize qualification or extra runs.

Technical preparation still belongs to the assistant. The geometric cutoff,
PC paths and common finite source law are recorded. Establish source
implementation and instrumentation through Fluent; finish reference
phase-interaction readback and verify complete source-case persistence.
Do not ask the human to supply facts that these checks can recover. A required
physical datum that remains unrecoverable must be returned explicitly.

## Decision gates

### G1 — Five-case discovery review

- **Origin:** the human approved five thickness cases, the carrier-only scope,
  and up to `5,000` iterations per case, then asked to see what happens.
- **Evidence required:** all five terminal case dispositions with complete
  histories of water volume, residuals and phase/total mass accounting;
  source definition and integrated removal; inlet/outlet fluxes, inventories,
  pressure/velocity and spatial routing evidence; verified final/recovery
  artifacts and documented observations.
- **Decision condition:** each approved case has either reached its declared
  horizon or has an explicit execution-blocker disposition. Missing required
  histories mean the affected case is evidence-incomplete, not a pass.
- **Allowed next action:** compare the five cases and return the evidence,
  competing explanations and a proposed next decision to the human. No new
  case, automatic continuation or qualification run is authorized.
- **Not established:** physical separator validation, instantaneous perfect
  collection, long-horizon stationarity or a qualified source-independent
  result merely from reaching `5,000` iterations.
- **Return to human when:** the five-case comparison is ready, required
  geometry/access information cannot be recovered, faithful implementation
  is blocked, or an unapproved scientific change is needed.
- **Execution boundary:** technical preparation is authorized. The connected
  session's identity/ownership, exact paths and disposable build state must be
  resolved before mutation; the phase-planner launch decision and verified
  discovery-design gate remain prerequisites for the scientific run loop.

## Conditional qualification paths

No qualification path is approved.

## Approved execution handoff

**Human launch authorization, 2026-09-08:** the human selected option 1,
continue the scientific phase loop in this chat. This includes finishing
the stated implementation checks before running the approved screen.

The scientific choices are fixed by E1 and G1; the remaining unknowns are
implementation checks, not a request for the human to supply additional
geometry or operating conditions. On loop launch, finish the
reference/source and monitor proofs before advancing the selected cases.
Do not treat the preparation case or compiled geometry probe as run-ready.

Use the currently configured server-1 PC through Fluent/PyFluent only. The
approved session authority covers the disposable Phase-7b preparation state
and its selected children, including saving, reloading and bounded setup
verification. Reconcile endpoint and ownership again before execution; do
not take an unrelated active case or another server without resolving its
authority. Preserve source inputs and verified saved artifacts. Any failed
mandatory implementation check returns a bounded blocker; a scientific
change, coefficient sweep, sixth case or extension beyond 5,000 iterations
returns to the human. This handoff is active following the human's explicit launch choice.

## Human locks and handoff rules

- Do not restore a standing-pool requirement or switch to transient modelling
  without a new human direction.
- Keep Energy off. Use the reference-model physics/full-feed basis; the
  `0.05%` transient diagnostics are historical context only, not a settings
  parent, tuning recipe or continuation route for Phase 7b.
- Preserve the human-selected equal-velocity pure-phase inlet design. Do not
  substitute mass-flow inlet boundaries or mix its design densities with
  another reference's properties without resolving the target-flow mismatch.
- Do not assume the F11 full geometry and the separate 620,431-cell resolved
  outlet mesh are interchangeable. Phase 7b has staged the latter mesh;
  identify any selected case/data parent separately.
- Do not invent a physical pool level to place the collector. Any chosen
  numerical placement must be labelled as such.
- Do not exceed the human-selected historical cutoff cap, or assume a cutoff
  coordinate from Shuhei's separate mesh applies to Andy's full mesh without
  verifying the mapping.
- `scientific-phase-loop` may execute only approved E1 cases and declared G1.
  Five-case selection, technical preparation and loop launch are authorized.
  Verified lifecycle gates still govern implementation and execution.

### Current implementation boundary

**Current verified state (2026-09-12):** rebuilt the approved reference from
only the original mesh through Python, with automatic C compilation disabled.
Settings save/reopen passed; the only whole-snapshot difference was delayed
`domains` metadata population. Clean initialization and paired save/reload
passed, followed by three source-free steady iterations with matching native
and expression water-volume histories and all seven residual histories at
N1–3. Clean N0 and N3 matching case/data pairs are preserved on the PC.

**Current recovery (2026-09-18):** the API responds in a new Fluent process
(Cortex24936 / solver14276). The clean N3 pair reloaded successfully, with
steady Mixture, all sources off, global iteration3 and the saved water volume
`4.190719535637436e-5 m3`. The reload transcript contains no Cortex fatal
errors. A separate client reconnected after the loading client exited and
verified the same process and iteration, proving client exit preserved Fluent
in this check. No additional iterations were issued.

**Implementation progress (2026-09-18):** component-first liquid velocity
expressions passed comparison against all three native phase components at
nonzero slip. Shared turbulence expressions require no explicit phase
context. Corrected source definitions saved/reopened and completed 50 startup
iterations with full histories and zero Cortex faults. Practical removal is
not yet demonstrated: almost no liquid reached S20 during that short startup.
The applied native mass source is lagged relative to the current-alpha
expression; preserve both and use the applied source for discrete closure.

Exact collector-cell zone separation is an instrumentation operation only:
it preserves mesh counts/geometry and the source predicate. S20 membership
matches exactly, its complete boundary contains 7,076 unique faces, and no
crossing faces remain in the upper-zone interior. Phase-face flux sums agree
with native phase reports; the synchronous recorder passed a three-iteration
PC/local readback smoke. The first full screen is being prepared with the
additional pressure/velocity reports, fixed sections and checkpoints. A
maximum-speed report context error was caught at N0. On 2026-09-21 NZ the API
responded again, and the report correction was applied, saved and reopened
successfully. The S20 runner is resuming verification and its approved screen.
All five screen outcomes remain open.
The current `phase-loop` owns these in-scope recoveries; earlier restart locks
are historical. Exact execution status is in `phase-state.yaml` and machine
manifests; evidence and claim limits are in [diagnostics](diagnostics.md).

**Corrected counter interpretation:** `sol/iterations` remained 10 after
Hybrid Initialization and after three solve steps; it is not the global
iteration counter. Use the `Iteration` expression reconciled with native
histories. Historical claims that this RP value proved an N10/N13 progress
inconsistency are withdrawn; the recorded Cortex fatal errors remain separate,
valid failure evidence.

**Current access:** Andy temporarily regained PC access for diagnostics on
2026-09-10, then requested wrapping up before leaving. Fluent API remains the
only authorized remote access route. Do not depend on continued GUI access.
See [technical diagnostics](diagnostics.md) for the current findings and remaining checks.

**Human-directed:** implement through Python/PyFluent instead of C. The
uncompiled collector C draft was withdrawn; prior source-free geometry and
velocity probes are diagnostic evidence only. Native expression sources have now been attached and survived a same-session
save/reload diagnostic. They were disabled afterward; no collector-enabled
iteration or verified runnable recipe is established.

**Source strength:** the design's common `tau=0.0024095893 s` is an untested
numerical implementation choice, not a human-selected or historically proven
optimum. The human asked to reconcile it with the earlier tau studies. Those
records used `0.1 s`, `0.02 s` and adaptive values bounded by `0.002 s`; none
established an accepted steady balance. Keep the five thickness cases
unchanged; no additional coefficient sweep has been authorized.

**Prior operational blocker (API recovered on 2026-09-10):** the Python-issued whole-domain diagnostic
ASCII export has not returned a completion result. A fresh PyFluent connection
and a separate eight-second gRPC health request both failed with deadline
exceeded. Current solver responsiveness and remote export completion are
unverified. The local waiting export client was interrupted and exited with
code 130; this does not prove the remote export stopped or completed. Do not
submit a duplicate export, reload or solve until reconciled.
The last observed physical state was ten source-free steady diagnostic
iterations. A matching pre-diagnostic initial pair was saved at
`case-data/p7b-source-preflight-initial-20260908T102600Z.cas.h5` and `.dat.h5`
beneath the verified PC phase root. Preserve/reconcile that pair and restore
the common fresh initial state before any screen. Health evidence is in
`PyAnsys/output/phase07b_preparation/python-route-health.json`.

**Observed connection-layer diagnostic:** a subsequent read-only test opened
the configured TCP port in `0.016 s` and established gRPC transport readiness
in `0.024 s`, but the authenticated health RPC reached its eight-second
deadline without a response. The configured endpoint is reachable; Fluent
application responsiveness remains unverified. **Inferred:** the fault is
more consistent with an unresponsive/busy application or RPC service than a
completely unreachable endpoint. The first stalled operation was the native
whole-domain velocity export; causation, a blocked export, resource pressure
or a process fault cannot be distinguished from these checks. File-path
restructuring does not explain failure of a health request that uses no
case/data paths. Evidence:
`PyAnsys/output/phase07b_preparation/connection-layer-diagnostic.json`.

**Observed recovery on 2026-09-10:** following the human report of a write
error, the configured API health service returned `SERVING`; normal PyFluent
Settings and Scheme readbacks completed. Fluent 2025 R2 still has the expected
full-geometry fluid zone, steady pressure-based solver, iteration `10`, and
all mixture/phase cell-source enables off. Both files of the recorded initial
recovery pair exist (existence check, not a new integrity/reload proof).
Unique small text writes with exact readback passed in `exports`, `reports`
and `case-data`. Connectivity and small-file write access have recovered;
the earlier large export's completeness and exact write-error cause remain
unverified. No export retry, initialization or additional solve was submitted.
Python/native-expression source and persistence verification remain pending.
Evidence: `PyAnsys/output/phase07b_preparation/retry-after-write-error-health.json`,
`retry-after-write-error-state.json`, and `retry-after-write-error-files.json`.

**Observed write-error evidence:** the human-provided image
`/Users/andy/Downloads/IMG_4358.HEIC` shows `wrote ascii data on cells`,
`Done.`, followed by `Error: Error writing` for the diagnostic CSV
`exports/p7b-phase-velocity-comparison-20260908T102932Z.csv` and
`Error Object: #f`. The native export reported an error; its preceding
`Done.` line is not sufficient success evidence. A bounded API read of that
exact file found the expected velocity/UDM header and initial cell rows. Thus
the destination file was created and populated to some extent; completeness,
finalization and root cause remain unverified. Do not infer disk exhaustion,
permissions failure or solver divergence from this generic message. Keep the
CSV excluded from accepted validation evidence. Current iteration remains 10.
The exact bounded read is in
`PyAnsys/output/phase07b_preparation/failed-export-inspection.json`.
