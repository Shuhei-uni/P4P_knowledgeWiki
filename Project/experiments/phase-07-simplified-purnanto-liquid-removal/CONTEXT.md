# Phase Context — Phase 07 Simplified Purnanto Liquid-Removal Mechanisms

## Status

- **Planning state:** scientific-phase-loop entered by explicit human direction;
  E0 execution and available-Fluent-server takeover are authorized, with all
  later action restricted to the approved G1 gates
- **Last human review:** 2026-09-08
- **Experiment-selection authority:** human-approved-context-only
- **Current decision:** the human-approved contrastive fixed-mesh setup series
  is fully defined and compiled. On 2026-09-08 the human explicitly entered
  `scientific-phase-loop`, authorized takeover of available Fluent servers,
  and directed execution to begin with `P7-E0-REF` through its full
  `2,000`-iteration discovery horizon. Remaining placement, implementation,
  and execution gates still apply, and progression remains limited to the
  approved G1 actions.

## Human thinking

### Current intent

The human does not want to continue developing the full geometry because its
complexity is obstructing useful progress. The selected direction is to return
to a simpler Purnanto model and deliberately try pragmatic or “hacky” ways of
removing separated liquid. The immediate aim is to find whether some bottom
geometry or outlet treatment can produce a possible steady operating point in
which liquid inventory and mass flow stop drifting materially.

A method is useful only if its intervention, artefacts, conservation behaviour,
and claim limits remain explicit. Draining liquid or obtaining small residuals
alone does not establish a physically faithful brine outlet or a credible
steady mass balance.

The human has confirmed that this recorded context should be used as the
current thinking for Phase 07 and that the workflow should proceed to
experiment framing.

The human has now supplied the Phase-07 mesh. They report that it retains the
original Purnanto geometry except that the separator bottom is the cutoff plane
representing where the real brine-pool surface would normally be. The mesh is
therefore the reference geometry for screening; Phase 07 does not need to
reconstruct or independently choose a cut elevation before beginning setup
inspection.

The human expects the new mesh to reproduce the relevant setup-`08b` behaviour,
but has confirmed that E0 is not technically identical: it includes the bottom
cutoff, a different discrete mesh, and correction of the steam-outlet diameter
from the previously documented `0.724 m` to `0.876 m`. This is recorded as the
reference hypothesis, not an observed result. They selected detailed
mesh/geometry inspection as the first action before any reference solve or
outlet experiment.

The human confirmed on 2026-09-08 that all geometry in the supplied mesh is
intended. Its measured `steamoutlet` area of `0.602608 m²` gives an
area-equivalent diameter of `0.875936 m`, consistent with the human-corrected
`0.876 m` geometry fact. The former `0.724 m` outlet fact is superseded; that
dimension belongs to the square inlet. Phase-07 outlet turbulence/backflow
settings must use and verify the corrected outlet scale.

The human approved E0 on 2026-09-08 as the first Phase-07 experiment. They
proposed approximately `2,000` iterations, which is accepted as the initial
discovery horizon. This horizon is intended to characterize the corrected
reference case and its liquid-inventory buildup; it is not itself a steady-
convergence criterion.

The human then explicitly requested that E0's `setup.md` be created first and
that a series of later setups be defined before entering the autonomous
scientific phase loop. This separates E0 reference-setup preparation from the
later G1 contrastive treatment campaign. It authorizes the E0 setup record, not
an E0 solve and not any proposed E1–E3 treatment.

### Ideas raised by the human

| ID | Human idea | Why it seems worth considering | Status |
| --- | --- | --- | --- |
| H1 | Add holes or openings at the bottom so accumulated liquid has a direct escape route. | Tests whether a simple geometric drain can prevent indefinite liquid accumulation. | deferred until after fixed-mesh boundary screens |
| H2 | Develop and test new outlet functions or outlet behaviours. | Tests whether a numerical outlet treatment can preferentially remove liquid and allow a bounded steady state. | selected as first experiment family |
| H3 | Change the lower part of the simplified Purnanto geometry. | Tests whether lower-domain shape or drainage geometry is the main obstacle to liquid leaving the model. | deferred until after fixed-mesh boundary screens |

The human also supports comparing a range of distinct methods rather than
committing immediately to one mechanism. The first campaign will keep the
supplied mesh unchanged and work within H2. H1 and H3 remain human-originated
conditional directions, but no geometry change is permitted until some
fixed-mesh outlet experiments have been assessed. No exact H2 treatment is yet
approved; the controlled changes and decision gate remain under human review.

The human approved the full H2 mechanism-ladder architecture on 2026-09-08:
E0 wall reference, conventional bottom pressure outlet, resistive outlet,
prescribed withdrawal, adaptive prescribed withdrawal, and an adaptive phase-
selective continuous-liquid sink, in that order. They require at least three
meaningfully separated settings within every treatment family
before the family is judged good or bad. The purpose is to distinguish a poor
parameter choice from a poor mechanism. This approves the family architecture
and replication principle, not the still-unsettled parameter values, run
horizons, or executable child setups.

The human then approved a common staged run protocol. Every initial treatment
variant receives `500` steady iterations from the same initialized E0 state.
The strongest valid setting within each family may continue from its own
iteration-500 checkpoint to a matched total of `2,000` iterations. The initial
500 iterations are a survivability, response-direction, vapor-loss, inventory,
phase-routing, and numerical-behavior screen; they cannot alone establish a
bounded or converged state.

Each family begins with three meaningfully separated settings. One additional
pre-bounded fourth setting is conditionally authorized in principle only when
the initial three leave the useful stable-to-failure transition unresolved,
show a material non-monotonic response, or place the best valid response at a
tested range boundary. The exact fourth-point interval and deterministic
selection rule must be specified with each family before execution; this is
not permission to invent an unbounded post-hoc setting.

The human approved the initial E1–E3 parameter sets on 2026-09-08:

| Family | Approved initial children | Controlled values |
| --- | --- | --- |
| E1-PO pressure outlet | `P7-E1-PO-P1120`, `P7-E1-PO-P1160`, `P7-E1-PO-P1200` | `1.120`, `1.160`, `1.200 MPa` gauge |
| E2-OV outlet vent | `P7-E2-OV-K000`, `P7-E2-OV-K003`, `P7-E2-OV-K007` | constant normal-velocity loss coefficient `K=0`, `3`, `7` |
| E3-MFO prescribed withdrawal | `P7-E3-MFO-Q025`, `P7-E3-MFO-Q050`, `P7-E3-MFO-Q100` | intended liquid withdrawal `29.23`, `58.46`, `116.92 kg/s` (`25%`, `50%`, `100%` of nominal liquid inflow) |

E1 uses the higher-pressure bracket chosen by the human rather than a tight
bracket around the `1.120 MPa` steam outlet. E3's intended vapor target is
zero, but live Fluent capability inspection must prove whether the selected
outlet formulation can impose and expose phase-specific withdrawal. If it can
only impose total mixture flow, that limitation is material and must be
returned to the human rather than relabelled as pure-liquid withdrawal.

The conditionally permitted fourth points are:

- **E1-PO:** add `1.180 MPa` if `1.160 MPa` is valid and `1.200 MPa` is
  invalid; add `1.140 MPa` if `1.120 MPa` is too permissive and the useful
  transition lies below `1.160 MPa`; or add at most `1.240 MPa` if all three
  are valid and improvement remains unresolved at the upper edge. Only one
  branch may activate, and no pressure outside `1.120–1.240 MPa` is permitted.
- **E2-OV:** add `K=5` if `K=3` is valid and `K=7` invalid; add `K=10` if
  `K=7` is valid and remains the unresolved best upper-edge setting; or add
  `K=1` if the useful transition lies between `K=0` and `K=3`. Only one branch
  may activate, and no `K>10` is permitted.
- **E3-MFO:** add `87.69 kg/s` if `58.46 kg/s` is valid and `116.92 kg/s`
  invalid; add at most `146.15 kg/s` if all three are valid and the upper edge
  still under-removes liquid without unacceptable vapor loss; or add
  `14.615 kg/s` if even `29.23 kg/s` is too aggressive for a useful
  survivability diagnostic. Only one branch may activate, and no withdrawal
  above `146.15 kg/s` is permitted.

The human approved the shared E4/E5 adaptive architecture on 2026-09-08:

- start every adaptive child from the exact E0 iteration-500 case/data
  checkpoint;
- define the numerical target `M*` as E0 total continuous-liquid mass at
  iteration 500;
- define `ΔMref` as the positive E0 liquid-mass increase from iterations 500
  to 1,000;
- update the command every 50 controller-active solver iterations using
  `e = max(0, (Mcurrent - M*) / ΔMref)` and
  `command = clamp(G × 116.92 kg/s × e, 0, 146.15 kg/s)`;
- screen `G=0.25`, `0.50`, and `1.00` for both actuators, giving nominal
  commands of `29.23`, `58.46`, and `116.92 kg/s` when `e=1`;
- record every inventory input, normalized error, requested/clamped command,
  saturation state, realized removal, phase routing, and balance at every
  controller update; and
- treat the target as a numerical inventory reference, not a real separator
  level or plant control setpoint.

The approved adaptive child IDs are:

| Family | Low | Medium | High |
| --- | --- | --- | --- |
| E4 adaptive prescribed withdrawal | `P7-E4-ADAPT-G025` | `P7-E4-ADAPT-G050` | `P7-E4-ADAPT-G100` |
| E5 adaptive phase-selective sink | `P7-E5-PSINK-G025` | `P7-E5-PSINK-G050` | `P7-E5-PSINK-G100` |

For each adaptive family, one conditional fourth tuning is permitted:
`G=0.75` if `G=0.50` is valid but `G=1.00` is unstable/oscillatory;
`G=1.50` if `G=1.00` is valid, remains too weak, and is not materially cap-
limited; or `G=0.125` if even `G=0.25` is too aggressive. Only one branch may
activate per actuator, and no `G>1.50` is permitted. If `ΔMref` is not positive
and measurable, no adaptive child may run and the design returns to the human.

For E5, the human approved one frozen bottom-adjacent sink region containing
only cells in fluid zone `separator-purnanto` whose centroids satisfy
`0 ≤ y ≤ 0.10 m`. The selected cell IDs, count, volume, and initial/activation
liquid mass must be recorded and identical across E5 children. The commanded
sink is distributed in proportion to local continuous-liquid mass, applies no
direct vapor sink, and must remove associated continuous-liquid momentum
consistently and report every explicit mass/momentum source contribution.

### Constraints expressed by the human

- The fixed source mesh is
  `/Users/shuheiyokkaichi/Library/CloudStorage/OneDrive-TheUniversityofAuckland/2026 Sem 1/700/P4PCFD/CAD PurnantoV2/Separator-purnanto342k.msh.h5`.
- **Human-reported geometry:** apart from the bottom cutoff, the mesh geometry
  is unchanged from the original Purnanto geometry.
- **Human-reported geometry intent:** the mesh bottom is already located at the
  plane where the real separator's brine-pool surface would normally be.
- Setup `08b` is the selected physics, materials, inlet, turbulence, and
  numerical parent. Its old mesh is not inherited; its settings must be
  reconciled onto the supplied Phase-07 mesh. The historical `0.724 m`
  steam-outlet backflow hydraulic diameter is not inherited: Phase 07 must use
  and read back `0.875936 m` (`≈0.876 m`) for the supplied outlet.
- The supplied 08b parent candidate is
  `/Users/shuheiyokkaichi/Library/CloudStorage/OneDrive-TheUniversityofAuckland/P4P-Fluent-Artifacts/TwoPhaseInletV2(Purnanto).cas.h5`.
  Its exact settings and lineage must be verified by Fluent readback before it
  is accepted as the proven parent; its filename alone is not proof.
- Locate the actual `08b` case/setup on the Fluent server before implementation.
  If it is absent or cannot be proven, return to the human, who has offered to
  supply it; do not substitute a different parent silently.
- Do not return to full-geometry development during this phase.
- Keep the supplied Phase-07 mesh exactly fixed during the first boundary-
  treatment experiments. Geometry holes and lower-domain reshaping require a
  later human decision after some fixed-mesh evidence exists.
- The first useful target is a possible steady numerical state with materially
  improved mass-flow closure, or at least a reduced liquid-inventory buildup
  rate, rather than a faithful model of the real outlet hardware.
- Multiple pragmatic mechanisms may be screened, including artificial ones,
  provided their effects remain interpretable.
- Prefer bottom steam loss as close to zero as practicable. This is a strong
  ranking preference and interpretation constraint, not an arbitrary hard
  numerical gate at the current screening-design stage.
- The immediate objective is a useful and interpretable computational
  workaround, not validation of physical outlet hardware or level control.
- New experiment directions require explicit human approval in this file.

## Evidence anchors

- **Observed:** [Phase 06 conclusion](../phase-06-full-geometry-with-brine-pool/conclusion.md)
  records that the full-geometry F11 steady Mixture/RNG bracket did not
  establish a controlled pool state.
- **Observed:** [Phase 07 direction](index.md) identifies bottom liquid removal
  in the truncated simplified geometry as the next project uncertainty.
- **Reported predecessor:** setup [`08b`](../phase-02-parity-reset-and-pre-v2-qualification/purnanto-08b-parity-split-inlet/setup.md)
  is the human-selected parent. Its reported target inlet flows are
  `116.92 kg/s` liquid and `80.69 kg/s` vapor, its continuous phase uses the
  Mixture model with RNG `k-epsilon`, and its historical whole-domain mixture
  imbalance ratio was `0.5873`; this is parent context, not a Phase-07 result.
- **Observed artifact identity:** the supplied mesh exists at the fixed
  OneDrive path, is `40,685,983` bytes, was modified at
  `2026-09-08T11:26:11+12:00`, and has SHA-256
  `59b7cf3bcf1cf0266587d4b98f8c6d67bbca007a4381ceb16a05fd8728b37801`.
- **Observed parent-candidate identity:**
  `TwoPhaseInletV2(Purnanto).cas.h5` exists at the supplied OneDrive path, is
  `243,137,956` bytes, was modified at `2026-09-08T14:43:41+12:00`, is a valid
  HDF5 container, and has SHA-256
  `b75a69dcad7da29fa9576c15d478a187798029b51d45ac773a265ecdf146ae56`.
- **Human-reported:** the mesh bottom encodes the intended brine-pool-surface
  cutoff and the remaining geometry is unchanged from original Purnanto.
- **Observed structural inspection:** [mesh inspection](mesh-inspection.md)
  verifies `342,609` cells, `1,077,053` nodes, one fluid cell zone, six external
  face zones, a distinct planar `bottom` wall at `y≈0`, boundary areas, and
  internally consistent connectivity.
- **Observed parity support:** the new liquid and steam inlet areas agree with
  the recorded 08b/07 split to within approximately `0.0067%` and `0.0001%`,
  respectively.
- **Observed and human-confirmed geometry correction:** the new `steamoutlet`
  area is `0.602608 m²` (area-equivalent diameter `0.875936 m`), and the human
  confirmed that the former `0.724 m` steam-outlet fact was wrong. The active
  geometry value is `0.876 m`; `0.724 m` remains the inlet side length.
- **Observed discrete-mesh difference:** the new mesh has about `22.2×` fewer
  cells than the user-reported 08b mesh metadata.
- **Missing Info:** solver-side mesh quality, the actual 08b artifact identity,
  server-side OneDrive mesh path, and flow-behaviour parity remain unverified.

## Phase contract

### Phase question

> What practical numerical mechanism can remove separated liquid from the
> bottom of the truncated Purnanto separator model while preserving a useful
> and interpretable representation of the separation behaviour?

### Scope, invariants, and claim limit

- **In scope:** mechanism discovery for liquid removal at or near the truncated
  lower boundary of the supplied simplified Purnanto mesh.
- **Out of scope:** physical validation of the real brine-pool interface,
  outlet hardware, drainage rate, and level-control response.
- **Must remain fixed during a controlled screen:** the supplied reference
  geometry; the reconciled `08b` physics, materials, inlet definitions,
  turbulence model, corrected `0.875936 m` steam-outlet turbulence/backflow
  scale, initialization basis, numerics, monitors, and evidence horizon unless
  an approved candidate explicitly names another delta. H1/H3 geometry changes
  are not permitted in the first campaign.
- **Must remain explicit:** intervention, tuning, phase-routing effects,
  liquid inventory, phase-resolved mass balance, and numerical behaviour.
- **Claim limit:** a successful candidate is only a computational liquid-removal
  mechanism until separately supported by physical evidence.

### Useful evidence standard

A useful phase result identifies whether an approved mechanism can either move
the model toward credible mass closure or materially reduce the rate of liquid
inventory buildup relative to its matched reference. A stronger result would
approach a bounded state in which liquid inventory no longer drifts materially
and the phase-resolved inlet/outlet balance is acceptably closed. Residual
behaviour, steam loss, phase-routing distortion, and numerical stability must
be checked alongside that balance. Bottom vapor discharge should remain as
close to zero as practicable and must be reported explicitly, but no hard
numerical steam-loss threshold is fixed yet. The exact comparison thresholds
remain human-unconfirmed.

## Candidate experiment pool

| ID | Origin | Controlled delta | Screening question | Required evidence | Artifact/rejection signal | Human status |
| --- | --- | --- | --- | --- | --- | --- |
| E0 | H2 reference implied by the human-selected fixed-mesh comparison | Reconcile setup `08b` onto the supplied mesh with its bottom as a non-draining wall and correct the steam-outlet turbulence/backflow hydraulic diameter to `0.875936 m`; no removal treatment. | Does the corrected fixed-mesh case reproduce the relevant 08b inlet realization and flow behaviour closely enough to serve as the matched Phase-07 reference? | Verified mesh/zone and 08b-setting readback, including the controlled outlet-scale correction; phase-resolved boundary fluxes; liquid inventory; native residual histories; matched late-window slopes over the `2,000`-iteration discovery horizon. | Unproven parent reconciliation, unintended setting drift beyond declared geometry/outlet corrections, invalid monitor package, or failure before a comparable reference horizon. | human-approved 2026-09-08 for setup creation under G0; execution awaits completed series planning and loop gates |
| E1-PO | H2 — human-inspired variant | Change only the existing `bottom` wall to a conventional pressure outlet at `1.120`, `1.160`, or `1.200 MPa` gauge. | Across the approved pressure range, can passive bottom discharge reduce liquid accumulation without disastrous vapor loss? | E0 evidence plus bottom phase-resolved fluxes and matched setting-response comparisons. | Apparent improvement is vapor-dominated, numerically unstable, non-monotonic without explanation, or no tested setting improves the E0 trend. | initial three settings, bounded fourth rule, and 500→2,000 protocol human-approved |
| E2-OV | H2 — human-inspired variant | Change only `bottom` to a constant normal-velocity outlet-vent treatment at `K=0`, `3`, or `7`. | Can added outlet resistance trade liquid drainage against vapor loss more usefully than an unrestricted passive outlet? | E0/E1 evidence plus pressure drop, normal velocity, bottom phase flux, and coefficient-response comparisons. | Resistance merely delays failure, causes reversal/instability, blocks useful liquid drainage, or leaves vapor loss unacceptable. | initial three settings, bounded fourth rule, and 500→2,000 protocol human-approved |
| E3-MFO | H2 — human-inspired variant | Change only `bottom` to intended liquid withdrawal of `29.23`, `58.46`, or `116.92 kg/s`, subject to live proof of the outlet's phase-specific capability. | Does the approved controlled-removal range reveal a setting that materially reduces buildup without phase-routing or numerical failure? | E0 evidence plus commanded-versus-observed withdrawal, bottom phase split, and rate-response comparisons. | Fluent cannot impose/verify the intended phase routing, numerical failure dominates, or apparent closure is only the imposed sink with unacceptable vapor removal. | initial three settings, bounded fourth rule, and 500→2,000 protocol human-approved; capability proof required |
| E4-ADAPT | H2 — human-inspired variant | From E0 iteration 500, adapt the `bottom` prescribed-withdrawal command every 50 iterations using the approved normalized inventory-error law at `G=0.25`, `0.50`, or `1.00`. | Can adaptive boundary withdrawal reduce liquid drift more robustly than fixed withdrawal without saturation, oscillation, or vapor-driven closure? | E0–E3 evidence plus `M*`, `ΔMref`, error, command, gain/bounds, saturation state, bottom phase split, inventory, and balance histories. | Invalid/nonpositive normalization, controller saturation/cycling, sensitivity to one tuning, hidden phase routing, or vapor-dominated removal. | initial three tunings, bounded fourth rule, controller law, activation state, and 500→2,000 active protocol human-approved |
| E5-PSINK | H2 — human-selected phase-selective variant | From E0 iteration 500, apply the same approved adaptive law at `G=0.25`, `0.50`, or `1.00` as an explicitly accounted continuous-liquid-only sink in the frozen `0≤y≤0.10 m` fluid-cell region. | Can a deliberately artificial liquid-only actuator reduce inventory drift without hiding conservation or destabilizing the carrier solution? | E4 evidence plus sink-region identity, selected cells/volume, `M*`, `ΔMref`, error/command, realized liquid removal, associated momentum removal, total inventory, phase balances, and proof of zero direct vapor sink. | Invalid/nonpositive normalization, unaccounted mass/momentum removal, region drift, source saturation, numerical instability, or balance inconsistency. | initial three tunings, bounded fourth rule, controller law, region, activation state, and 500→2,000 active protocol human-approved |

H1 bottom holes and H3 lower-geometry changes remain deferred human ideas and
are not executable candidates in the first campaign.

## Approved screening campaign

E0 is approved as the first reference experiment and its server-neutral setup
has been created under G0. The mechanism ladder and minimum three-setting rule
for E1-PO, E2-OV, E3-MFO, E4-ADAPT, and E5-PSINK are human-approved. The
independent G1 design review passed, and server-neutral setup/results packets
now exist for all 15 approved initial children. The campaign is not executable
until the remaining phase-contract, fleet/session, placement, implementation-
capability, and execution gates pass.

The initial E0 discovery horizon is `2,000` solver iterations. The experiment
design must preserve the full native histories and compare at least the
`1,000–1,500` and `1,500–2,000` windows, with the final `500` iterations as the
primary late-window basis for liquid-inventory and balance slopes. Earlier
valid samples remain part of the evidence and must not be discarded merely to
make a trend look favourable.

Every E1–E3 child starts from the exact same save/reopen-proven E0 initialized
case/data pair, not from the solved E0 endpoint or another treatment case.
Every E4/E5 child starts from the exact same E0 iteration-500 checkpoint under
the approved adaptive activation rule. Each initial child attempts 500
treatment-active iterations. The family member selected by the predeclared G1
evidence rule may continue from its own valid screen checkpoint to 2,000 total
treatment-active iterations; it is not restarted or seeded from a different
family.

## Decision gates

### G0 — E0 corrected-reference setup preparation

- **Status:** human-approved on 2026-09-08 for design and creation of E0's
  server-neutral `setup.md`.
- **Purpose:** establish a precise, evidence-complete reference contract before
  choosing the contrastive liquid-removal series.
- **Required design evidence:** exact parent and mesh identities; declared
  corrections and invariants; collision check; `2,000`-iteration run intent;
  hard pre-run instrumentation; core figures; invalidity conditions; and claim
  limit.
- **Allowed next action:** create E0's `setup.md` and paired empty `results.md`.
- **Not authorized:** live Fluent mutation, E0 execution, selection or setup of
  E1–E3, or entry into `scientific-phase-loop`.
- **Return condition:** if E0 cannot be specified without an additional
  scientific choice or a changed parent/geometry/model boundary, return to the
  human.

### G1 — Fixed-mesh liquid-removal screen

- **Status:** approved in principle by the human on 2026-09-08; exact numerical
  thresholds remain deliberately open until E0 establishes the new mesh's
  natural scale.
- **Validity evidence required:** exact mesh and 08b-parent identity; mesh and
  boundary-zone readback; save/reopen-proven setup; fixed geometry, physics,
  initialization, numerics, reports, and horizon across comparisons; and
  explicit readback of the corrected `0.875936 m` steam-outlet
  turbulence/backflow hydraulic diameter.
- **Scientific evidence required:** native residual histories; total liquid
  inventory and late-window slope; phase-resolved flux at both inlets, the
  steam outlet, and the treated bottom; derived liquid and mixture balances;
  bottom vapor loss normalized by the `80.69 kg/s` reference vapor inlet; and
  evidence that any improvement persists rather than being an endpoint effect.
- **E0 horizon interpretation:** reaching iteration `2,000` completes the
  planned discovery horizon, not a convergence claim. If the late-window
  histories remain too transient or noisy to establish a stable reference
  slope, the allowed outcome is an explicit inconclusive reference and a
  human-reviewed extension of the same E0; it does not authorize tuning or a
  bottom treatment.
- **Invalid comparison:** a missing/unproven parent, ambiguous zone mapping,
  lost settings, incomplete reports, or unmatched horizon produces no
  scientific result and permits only repair of the same approved screen or
  return to the human.
- **Reject condition:** no meaningful reduction in liquid buildup or imbalance;
  worse behaviour; numerical failure; hidden/unaccounted mass removal; or an
  apparent improvement dominated by disastrous bottom vapor discharge.
- **Diagnostic-improvement condition:** the liquid-inventory buildup rate or
  mass imbalance is materially reduced relative to E0 and the trend persists,
  but bounded state, numerical adequacy, or steam-loss acceptability remains
  unresolved.
- **Qualification-candidate condition:** late liquid-inventory slope approaches
  zero, phase and mixture balances become small and stable, bottom discharge is
  predominantly liquid with vapor loss as close to zero as practicable, and
  the numerical histories remain credible.
- **Allowed next action:** rejection; one named conditionally authorized fourth
  point; or continuation of at most one valid member per family from 500 to
  2,000 treatment-active discovery iterations. After the approved discovery
  evidence is complete, any hypothesis qualification requires a new explicit
  human decision and verified hypothesis contract. The gate cannot originate a
  new treatment, geometry change, or qualification run.
- **Not established by this screen:** final steady convergence, long-term
  boundedness, mesh independence, physical outlet fidelity, plant drainage or
  control behaviour, or validated separation efficiency.
- **Return to human when:** liquid improvement trades against non-negligible
  steam loss, candidates do not clearly dominate one another, the steam-loss
  preference needs a numerical threshold, geometry modification becomes the
  useful next branch, or an unplanned mechanism/result appears.

## Conditional qualification paths

No qualification path is approved.

## Human locks and handoff rules

- The supplied mesh is the fixed geometry source. Its bottom cutoff is accepted
  as human-reported geometry intent; the loop may inspect it but may not move
  the cutoff or replace the mesh without explicit human approval.
- Setup `08b` is the selected parent. If its case/setup cannot be found and
  proven from the supplied parent candidate by Fluent readback, return to the
  human; do not silently substitute another source.
- Reproduction of the relevant 08b behaviour by the corrected E0 case is a
  hypothesis to test. E0 is not bit-for-bit identical to 08b, and the loop may
  not convert structural similarity into a claimed flow-parity result.
- The loop may not return to full-geometry development as an unplanned response
  to a failed simplified-geometry screen.
- A low residual alone, liquid removal alone, or apparent steam dryness alone
  may not be treated as steady mass convergence.
- `scientific-phase-loop` may not create, select, or promote an experiment
  until a human-approved candidate and gate are recorded here.
- The loop may not start from E0 alone. Before loop entry, the human-requested
  treatment series must be defined, each executable candidate must be
  explicitly approved, and G1 discovery-design coverage must pass independent
  verification.
