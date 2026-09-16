# Phase Context — Phase 07A Simplified Purnanto Liquid-Removal Mechanisms

## Status

- **Planning state:** human-reframed mechanism-discovery record; historical
  execution evidence retained and the convergence follow-on moved to Phase
  7.1A
- **Last human review:** 2026-09-11
- **Experiment-selection authority:** human-approved-context-only
- **Current decision:** Phase 07A retains the completed mechanism-discovery
  evidence. The lower cell-zone, phase-2-only absorber is the human-selected
  working liquid-removal path, but it is not physically qualified or shown to
  be numerically converged. The new convergence-focused work is recorded in
  [Phase 7.1A](../phase-07-1a-absorber-convergence/). A separately authorized
  E6 localized radial-band pressure-outlet diagnostic is now designed, but no
  Fluent placement or execution has been authorized yet.

- **Historical execution authorization (2026-09-08):** the human explicitly
  directs the agent to attempt all 16 concrete setup packets currently
  compiled under this phase (E0 plus the 15 initial E1–E5 children), to
  overwrite active Fluent session state when required, and to use maximum
  contract-preserving parallelism. This authorizes dependency-gated attempts;
  it does not waive the E0 initialized-parent requirement, adaptive
  normalization requirement, E3 phase-specific capability check, E5
  liquid-only source-accounting check, or the fixed-mesh/no-tuning/evidence
  contracts. Conditional fourth points, 500→2,000 continuations, numerical
  tuning, and qualification paths remain outside this authorization.

- **Historical follow-on planning authorization (2026-09-10):** the human explicitly
  authorizes the creation and implementation planning of the `E5-CZ`
  cell-zone family, including a disposable Fluent split of the current mesh
  and a three-setting native source screen. The family must preserve the
  supplied coordinates/connectivity where the split-by-mark operation allows,
  record any generated adjacent face zones, and pass the same readback,
  save/reopen, smoke, history, balance, and claim-limit gates. The
  phase-planner launch decision was selected in this chat on 2026-09-10.

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

The human has now clarified a hard mechanism boundary: liquid removal must be
localized at the bottom/lower collector region. Liquid remaining higher in the
separator is acceptable and is expected to persist for some time because the
high-velocity turbulent inlet can leave wall-held liquid that drains downward
slowly. The phase does not need to remove all liquid immediately; it needs to
show whether liquid that reaches the lower brine-pool region can be absorbed
there without silently removing upper liquid. A conventional outlet is not the
desired representation of this pool because it would impose a new boundary
flow path and change the separator flow. The intended abstraction is a
localized numerical sink: continuous liquid disappears after entering the
lower pool region, while steam/vapor is not directly absorbed and should be
allowed to pass through to the extent supported by the multiphase
formulation. A zero bottom-boundary liquid flux is therefore not, by itself,
evidence against this absorber concept; the primary evidence is bounded
lower-region inventory, reduced total liquid buildup, phase-selective source
accounting, and acceptable numerical closure.

The human has selected a longer continuation of G100 because the 500-iteration
screen may still be dominated by the evolving flow field. The selected scope
is `2,000` additional active iterations from the verified active-500 pair,
reaching a total of `2,500` active iterations. The current lower cell zone,
source law, gain, momentum coupling, mesh, and numerical settings remain
unchanged; the controlled delta is the horizon only.

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
| H4 | Split the existing fluid zone into a lower cell zone and apply the liquid-removal source there as a numerical brine-pool absorber. | Tests whether Fluent's native zone-scoped source terms can recover the blocked E5 mechanism while preserving the same mesh coordinates/connectivity and allowing liquid to disappear locally without a bottom outlet. | human-approved follow-on discovery family on 2026-09-10 |
| H5 | Continue G100 for `2,000` additional active iterations, reaching a total of `2,500`, before rejecting the mechanism. | Tests whether the positive 500-iteration inventory slope is only an early transient response or persists after the flow field evolves. | human-approved continuation completed on 2026-09-10; bounded result returned to the human with no automatic follow-on |
| H6 | Treat the lower cell zone as an externally controlled brine-pool absorber: absorb liquid volumetrically after it reaches the lower region, leave vapor without a direct mass sink, and adapt the sink from lower-region inventory. | Tests whether the absorber concept is viable when source capacity and feedback are matched to the liquid actually present near the bottom, rather than only to total separator inventory. | human-approved absorber-control family on 2026-09-10; setup design authorized, Fluent launch still gated |
| H7 | Partition the existing planar bottom into several radial bands, retain the inner bands as walls, and expose the thin outermost band as a pressure outlet first. | Tests whether spatially localizing the full-bottom pressure outlet changes vapor shortcut, lower-region routing, and numerical survivability while preserving a wall over most of the cutoff plane. | human-approved localized pressure-routing diagnostic on 2026-09-15; mesh catalogue and face-zone capability proof required before execution |

The human also supports comparing a range of distinct methods rather than
committing immediately to one mechanism. The original first campaign kept the
supplied mesh unchanged and worked within H2. That campaign has now supplied
the relevant fixed-mesh evidence and exposed E5's region-specific source
limitation. The human has therefore approved a follow-on `E5-CZ` direction in
which the supplied mesh may be split into a lower fluid cell zone. H1 and H3
remain separate human-originated directions and are not being opened as
arbitrary geometry changes by this decision. On 2026-09-15 the human
explicitly reopened the localized H1/H2 sub-direction recorded as `E6-RING-PO`:
the existing bottom may be partitioned into reusable radial bands, with only
the outermost resolved band exposed as a pressure outlet in the first pattern.
This exception does not authorize arbitrary holes, remeshing, lower-geometry
changes, or execution before the disposable face-zone capability test passes.

The E6 design and setup packets are recorded in
[ringed-bottom-pressure-outlet-family](ringed-bottom-pressure-outlet-family/index.md).
The outer-band pressure matrix reuses the already human-approved E1 values
`1.120`, `1.160`, and `1.200 MPa` gauge so that the new spatial topology can be
compared directly with E1. The values remain boundary-condition probes, not
identified physical bottom pressures.

The human has clarified that E5-CZ is intended to imitate a brine pool whose
surface is held by an external component. It is not intended to imitate a
bottom pipe, pressure outlet, or other explicit drainage boundary. The desired
numerical abstraction is that continuous liquid entering the lower absorbing
region is removed from the modeled domain by a phase-2 volumetric sink, while
steam/vapor receives no direct mass sink and remains free to move through the
region. The matched mixture-momentum treatment may still perturb the shared
carrier flow, so vapor inventory, phase routing, and momentum effects must be
measured rather than assumed away.

The human has specifically requested that the patch/reset approach remain a
last-ditch route available only through a later explicit human request. It is
not an autonomous recovery option and must not be prompted as the next step.

### Constraints expressed by the human

- Removal must occur at the bottom/lower collector region; upper liquid is
  allowed to remain and drain downward gradually.
- A conventional bottom outlet is not the desired next representation of the
  brine pool. An outlet changes the boundary flow and therefore tests a
  different physical/numerical mechanism.
- The preferred absorber representation is a localized lower-region
  volumetric phase-2 liquid sink: liquid that enters the lower pool region may
  disappear from the modeled domain, while the direct phase-1 mass source
  remains zero. Vapor transparency is a bounded numerical objective, not an
  assumption that the mixture-momentum coupling has no effect on vapor.
- Future absorber control should use the liquid inventory in the lower region
  as its primary feedback signal, with total separator inventory as supporting
  evidence. The command may start high when lower-region inventory is high and
  decrease as the lower region approaches an explicitly stated pool target.
  Controller updates around every `50` iterations are preferred for the first
  screen, with close lower-region monitoring retained during any high-rate
  startup.
- A longer continuation may be useful before rejecting the mechanism because
  the 500-iteration E5-CZ screens are not necessarily long enough to reveal
  the evolving liquid-transport response.
- The human wants to understand whether lower-zone volume, absorber capacity,
  controller gain, or source cap imposes a true removal-rate limit before
  choosing another mechanism. A gain increase without a cap or feedback
  change may be non-informative when the command is already saturated.

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

### Conditional fourth-branch activation audit — 2026-09-09

The following bounded branches are activated under the human-approved
conditional rules above. This is a Phase Loop recovery/sensitivity action, not
a new unbounded candidate and not qualification authority:

| Family | Activated child | Trigger evidenced in completed screen | Scope/claim limit |
| --- | --- | --- | --- |
| E2-OV | `P7-E2-OV-K010` | K=7 completed its 500-iteration screen, is the upper tested setting, and the inventory/closure response remains unresolved | one 500-iteration discovery screen at K=10; current truncated mesh only; prior full-geometry K=10 is collision context, not a result transfer |
| E3-MFO | `P7-E3-MFO-Q14615` | Q025/Q050/Q100 completed with phase-specific readback; Q100 remains positively drifting while vapor loss is near zero, so the upper edge is unresolved | one 500-iteration discovery screen at 146.15 kg/s; prescribed-rate closure remains diagnostic only |
| E4-ADAPT | `P7-E4-ADAPT-G150` | G=1.00 completed without saturation, remains positively drifting, and its final command is below the 146.15 kg/s cap | one 500-active-iteration discovery screen at G=1.50; no controller or plant claim |

E1 activates no fourth branch because the corrected P1160/P1200 attempts both
failed during smoke after proving their requested pressure readbacks, so the
named E1 transition conditions are not satisfied. E5 activates no fourth
branch because all three children are blocked at the same region-specific
source-binding capability gate. These branches preserve the exact E0 parent,
instrumentation, comparison boundary, and no-tuning contract.

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
- Keep the supplied Phase-07 mesh exactly fixed during the original boundary-
  treatment campaign. This lock does not prohibit the explicitly approved H4
  follow-on from splitting the current mesh into cell zones while retaining
  its coordinates/connectivity.
- The H4 split must be performed on a disposable copy or a preserved recovery
  pair. Total cell/face/node counts, extents, mesh statistics, and mesh check
  must be compared against the unsplit pair before the result is used as a
  family parent. Generated adjacent face zones are part of the recorded
  topology delta.
- The explicitly approved H7 ring branch may partition the existing `bottom`
  face zone into named radial bands, but it must not overwrite the supplied
  mesh or silently become a CAD/remeshing change. The initial catalogue uses
  the existing square-annular face resolution and treats the outermost
  resolved row as the thin outer ring. A face-zone capability test, global
  mesh-invariant check, and save/reopen proof are required before any pressure
  outlet is activated.
- H7 is a boundary-topology contrastive diagnostic, not a replacement for the
  E5 absorber interpretation. A pressure outlet is not assumed to be
  liquid-selective; ring liquid and vapor fluxes must be reported separately.
- The H4 native source family must distinguish phase-specific mass from
  mixture-level momentum source capabilities. It may not claim the old
  local-mass-weighted liquid/momentum UDF law unless that law is separately
  implemented and verified.
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
- Patching or field reset is a human-only last resort for this phase and is
  excluded from autonomous prompts and recovery choices.

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
  are not permitted in the original campaign. The approved H4 candidate
  explicitly names the cell-zone topology split as its controlled delta.
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
| E5-CZ | H4/H6 — human-approved cell-zone brine-pool absorber | Starting from the exact E0 iteration-500 checkpoint, split the supplied single fluid zone by the frozen `0≤y≤0.10 m` register into a lower fluid zone, then apply a native zone-scoped phase-2 mass source with matched mixture-momentum accounting at `G=0.25`, `0.50`, or `1.00`. The lower zone represents an externally controlled brine pool; it is not an outlet. | Does native zone separation recover a usable, auditable liquid-absorber route in which lower-region liquid can disappear without a direct vapor sink, and how sensitive is the response to source capacity and gain? | Split invariants; lower-zone cell count/volume; phase-2 mass-source readback; mixture momentum-source readback; zero phase-1 mass source; integrated user sources; nested lower-region liquid inventory; phase-resolved balances; residuals; commands; vapor response; and generated face-zone topology. Bottom phase-2 boundary flux is a supporting diagnostic, not a required removal path for this abstraction. | In-place split fails or changes mesh metrics; source tree cannot be bound to the lower zone; momentum coupling is unaccounted; source saturates or destabilizes; lower-region and total inventories remain positively unbounded; vapor is directly removed or materially disturbed; or apparent closure is source-dominated/open. | human-approved follow-on family and three-setting discovery screen on 2026-09-10; future high-capacity/local-feedback extension requires a separate setup decision |
| E5-CZ-ABSORB | H6 — human-approved absorber-control extension | Starting from the exact verified G100 active-2,500 pair, preserve the lower cell-zone absorber but replace the total-inventory feedback with a parent-relative lower-zone phase-2 inventory signal at fixed `G=2.00`; compare only the predeclared command caps `146.15`, `292.30`, and `584.60 kg/s`. No outlet is introduced. | Can a high-capacity, lower-inventory-controlled absorber pull the accumulated lower liquid toward a bounded numerical pool target while keeping direct vapor absorption at zero and avoiding source-dominated or unstable behaviour? | Parent active-2,500 readback; lower-zone and nested-band liquid inventories; parent-relative target/error provenance; command/cap/saturation history; phase-2 get_sum source audit; zero direct phase-1 source; mixture-momentum source; vapor inventory/flux; phase and mixture balances; residuals; warnings; and paired checkpoints. | Parent cannot be proven; target rule is not reproducible; source cap remains saturated without useful lower-inventory response; lower and total inventories remain positively drifting; vapor is directly removed or materially disturbed; source/momentum audit is incomplete; or high-capacity settings destabilize the carrier solution. | human-approved family design on 2026-09-10; explicit Phase Loop launch entered in this chat; three discovery children queued in orders 24–26 |
| E6-RING-PO | H7 — direct human request on 2026-09-15 | Split the existing planar `bottom` into five named radial bands; retain R01–R04 as walls and convert only the thin outermost resolved band R05 to a pressure outlet at `1.120`, `1.160`, or `1.200 MPa` gauge. | Does spatially localized bottom discharge change E1’s vapor shortcut and numerical failure behaviour while allowing liquid reaching the outer lower region to leave? | Disposable face-zone capability proof; per-band counts/areas/plane/adjacency; unchanged global mesh invariants; save/reopen topology readback; per-ring total/liquid/vapor flux; reverse flow; pressure/velocity at wall/outlet junctions; lower and total inventories; phase-resolved closure; residuals; warnings; and matched E0/E1 comparisons. | Face split cannot be proven; ring is too jagged or changes mesh metrics; unselected bands do not remain walls; apparent inventory improvement is vapor-dominated; outlet flux is negligible; reverse flow or FPE dominates; or the response is not persistent over the discovery window. | human-approved design on 2026-09-15; setup packets prepared, mesh catalogue and Fluent capability proof required before placement; no queue execution authorization yet |

Arbitrary H1 bottom holes and H3 lower-geometry changes remain deferred human
ideas and are not executable candidates. The explicitly authorized E6 branch
is the narrower reusable radial-band diagnostic recorded above; it remains
blocked from placement until its disposable face-zone capability proof passes.
H4 is the separate approved absorber follow-on candidate recorded above.

## Approved follow-on: E5-CZ cell-zone family

The first H4 implementation is the native Fluent `separate cell zone by mark`
operation. A disposable student-server test on 2026-09-10 created a register
for `0≤y≤0.10 m`, separated `3,794` marked cells from the `342,609`-cell
`separator-purnanto` zone with adjacent-face movement enabled, and renamed
the new lower fluid zone `p7-e5-lower-y010`. The original parent retained
`338,815` cells. A direct unsplit/split pair comparison preserved `342,609`
cells, `1,647,633` faces, `1,046,255` solver nodes, domain extents, volume and
face-area statistics, and a clean mesh check. This is implementation evidence,
not yet scientific E5 performance evidence.

The follow-on family consists of three matched discovery children:
`P7-E5-CZ-G025`, `P7-E5-CZ-G050`, and `P7-E5-CZ-G100`. Each starts from the
same split, source-off E0 iteration-500 parent. The lower zone is kept at the
same frozen `0≤y≤0.10 m` extent across children. The phase-2 mass source is
set as a negative uniform SI volumetric source whose integrated requested
removal follows the existing normalized inventory-error law; the mixture
momentum source is set and audited consistently with the phase-2 removal
velocity available from the lower-zone reports. The implementation must
report the native phase/momentum source split explicitly. It does not inherit
the old E5 local-cell mass-weighted UDF claim.

The family is discovery-only: each child receives `500` controller-active
iterations, with the same `50`-iteration smoke and `50`-iteration update
cadence. A valid member may continue only through the predeclared G2 rule
after all three children are classified. No qualification path is opened by
this family.

### Human clarification of the absorber interpretation

For E5-CZ, the lower cell zone is a numerical stand-in for a brine pool with
an external level-control component. Liquid entering that region is allowed to
disappear through the explicitly accounted phase-2 volumetric sink. The model
does not need a bottom liquid outlet to represent that disappearance, and a
zero bottom phase-2 boundary flux is compatible with the intended abstraction.
The desired evidence is instead that lower-region liquid remains bounded or
returns toward its declared pool target, total liquid buildup is reduced, the
direct phase-1 mass source remains zero, and the phase/momentum/source balances
remain auditable.

The completed G100 continuation used total separator liquid inventory as its
feedback signal and a `146.15 kg/s` command cap. Because the accumulated
inventory made the uncapped command much larger than that limit, a future
`G=2.00`/G200 case with the same cap would reach the same saturated command
immediately and would not constitute a meaningful higher-capacity test. A
future absorber-control family should therefore predeclare whether it changes
the lower-region feedback signal, the source cap, or both. It should monitor
nested lower-region inventories at approximately `50`-iteration controller
updates and retain full source, vapor, balance, and residual evidence. This is
planning context only; it does not authorize a new run, a new gain, or a new
source law by itself.

G025 passed the split, source readback, save/reopen, and smoke gates. Its first
source-active attempt used an invalid lower-zone geometric-volume query and is
retained only as an invalid implementation record. The corrected G025 rerun
completed the 500-active-iteration screen; the source audit was then corrected
to use Fluent's `get_sum` reduction for the mass-flow field. G050 was recovered
from its durable active-250 pair after a connection reset during the first
attempt's final readback, and G100 completed as a fresh exact-parent rerun.
The three-gain execution/analysis package now exists. G050 has the smallest
provisional late inventory slope, but its current report package is a recovered
native 748--998 continuation window; all three gains still show positive
inventory drift and open boundary-only mixture closure.

## Approved continuation: E5-CZ G100 to active 2,500

The human selected `P7-E5-CZ-G100-CONT2500` on 2026-09-10. It continues the
verified G100 active-500 case/data pair for `2,000` additional active
iterations, reaching active `2,500` (approximately native `3,000`). This is a
bounded discovery continuation to distinguish a slow evolving response from
persistent positive inventory drift.

The continuation keeps the current `0≤y≤0.10 m` lower cell zone, source law,
`G=1.00` gain, mixture-momentum coupling, mesh/topology, numerics, monitors,
and bottom-only interpretation unchanged. It does not re-split, remesh,
reinitialize, enlarge the lower zone, change the outlet, patch/reset fields,
or introduce a new source law. Its setup packet is
[p7-e5-cz-g100-cont2500](cell-zone-treatment-family/p7-e5-cz-g100-cont2500/setup.md).
The corrected continuation completed at active `2,500`; its bounded results
are recorded in [results.md](cell-zone-treatment-family/p7-e5-cz-g100-cont2500/results.md)
and its paired remote final state is recorded in
[run-paths.yaml](cell-zone-treatment-family/p7-e5-cz-g100-cont2500/run-paths.yaml).
The final runtime-counter limitation and open inventory/closure behaviour are
retained as explicit evidence limits.

## Approved absorber-control extension: E5-CZ-ABSORB

The human approved a new discovery family on 2026-09-10 after reviewing the
G100 active-2,500 continuation. The family preserves the no-outlet brine-pool
abstraction but changes the controller signal from total separator liquid to
the phase-2 liquid inventory in the lower absorbing region. It fixes `G=2.00`
and varies only the predeclared source cap:

| Setup | Gain | Source cap |
| --- | ---: | ---: |
| `P7-E5-CZ-ABSORB-G200-CAP14615` | `2.00` | `146.15 kg/s` |
| `P7-E5-CZ-ABSORB-G200-CAP29230` | `2.00` | `292.30 kg/s` |
| `P7-E5-CZ-ABSORB-G200-CAP58460` | `2.00` | `584.60 kg/s` |

Each child starts from the exact verified G100 active-2,500 case/data pair and
keeps the split topology, lower zone, phase-2-only source, matched
mixture-momentum source, numerics, and outlet settings unchanged. The
parent-relative numerical target rule is:

```text
M_L0       = lower-zone phase-2 mass read from the active-2,500 parent
M_L,target = 0.50 × M_L0       (numerical control target, not a plant level)
e_L        = max(0, (M_L - M_L,target) / M_L,target)
command    = clamp(2.00 × 116.92 kg/s × e_L, 0, source_cap)
```

The `0.50 × M_L0` factor is an explicit numerical planning assumption and
must be read back and recorded before solving; it is not a claim about the
real brine-pool height. The controller updates every `50` iterations. Nested
lower-region bands, total liquid inventory, vapor response, source audits,
phase/mixture balances, residuals, warnings, and paired checkpoints are hard
evidence requirements. The family is discovery-only and is not qualification
or permission to introduce an outlet, patch/reset, UDF, remesh, or automatic
follow-on. The human then explicitly invoked `$phase-loop` in this chat on
2026-09-10, which supplied the launch decision for queue orders 24–26. On
2026-09-11 the human explicitly invoked Phase Loop followed by Auto Loop for
the separately approved cold-start balance probe, with a hard local stop at
09:00 Pacific/Auckland.
Execution remains subject to live parent/readback, save/reopen, smoke,
instrumentation, terminal-horizon, and evidence gates.

## Approved cold-start balance probe: E5-CZ-ABSORB-COLD

The human selected a separate cold-start discovery setup on 2026-09-11 after
asking whether the absorber can find a steady numerical branch when it is
present from initialization rather than applied to an accumulated continuation
state. The setup ID is `P7-E5-CZ-ABSORB-COLD-RAMP11692`.

This probe starts from the exact E0-style initialized case/data pair before any
treatment iterations. It then preserves the split lower zone, lower-zone
phase-2-only source, matched mixture-momentum source, bottom wall, outlets,
materials, models, and numerics. Its only treatment schedule is a fixed
integrated absorber command:

```text
Q_abs(n) = 116.92 kg/s × min(n / 100, 1)
```

where `n` is the child active-iteration coordinate and the schedule is
updated every `10` active iterations. The final held value matches the
measured liquid-inlet rate. This is a global mass-balance probe, not a claim
that the lower zone will automatically receive liquid at that rate or that
the physical brine pool has this capacity.

The setup is discovery-only with a `1,000` active-iteration horizon. Its main
question is whether the total liquid inventory and lower-zone liquid inventory
approach bounded late trends after the ramp, while the phase-2 source audit,
direct phase-1 source-off state, vapor response, phase/mixture balances, and
residuals remain credible. A later Phase Loop launch is required; this setup
record does not authorize execution or a qualification continuation.

## Human-approved cold-start time-horizon continuation

On 2026-09-11 the human requested a direct continuation of the completed
`P7-E5-CZ-ABSORB-COLD-RAMP11692` child from total active iteration `1,000` to
`5,000`. This is recorded as setup
`P7-E5-CZ-ABSORB-COLD-RAMP11692-CONT5000` with origin
`human-selected-continuation`. It must load the durable active-1,000
case/data pair, keep the same `p7-e5-lower-y010` split, hold the same
`116.92 kg/s` lower-zone phase-2 absorber, and preserve the bottom wall and all
no-outlet, no-patch/reset, no-remesh, and no-resplit boundaries. The only
scientific delta is the additional 4,000 iterations. This extension remains a
discovery/time-horizon result and does not authorize qualification or a new
liquid-removal mechanism.

The continuation was executed on `student` with the exact fixed-rate absorber.
It passed parent readback, save/reopen, smoke, and source-audit checks and
reached a valid active-1,960 history, but the solver diverged in the block
ending at active 1,970. The requested active-5,000 endpoint and final pair do
not exist. The valid continuation evidence shows total-liquid buildup and
negligible lower-zone liquid; the unchanged setting is therefore blocked from
supporting a bounded long-horizon branch. The result is retained as a
time-horizon discovery block. An exact restart from the durable active-1,900
pair, with the nonessential report-file query removed, reproduced the same
epsilon/flow-field blow-up and terminal Fluent node failure. The frozen
settings are therefore repeatably blocked. After a human relaunch of Fluent,
a third exact-settings restart reproduced the same active-1,970 blow-up and
node failure on the new endpoint. Any stabilization or altered absorber
recovery requires a separately authorized setup.

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

## G2 — E5-CZ cell-zone recovery screen

- **Status:** human-approved on 2026-09-10; the three-gain screen and the
  selected G100 continuation are complete under the same cell-zone contract.
  G050 remains the most promising provisional member by late inventory slope,
  but no member has established a successful bounded absorber state or
  qualification result. The continuation returned the unchanged absorber
  direction to the human for a source-capacity and lower-inventory-feedback
  decision; no outlet substitution or automatic follow-on is authorized.
- **Purpose:** determine whether a genuine lower fluid cell zone recovers a
  useful native phase-2 source route for the blocked E5 idea, and whether the
  response is meaningfully sensitive to three predeclared gains.
- **Validity evidence required:** exact E0 iteration-500 parent; split-by-mark
  register readback; unsplit/split mesh-invariant comparison; generated face
  zone inventory; lower-zone cell count and volume; source-tree readback for
  phase-2 mass and mixture momentum; zero phase-1 mass source; save/reopen;
  50-iteration smoke; and complete native histories.
- **Scientific evidence required:** controller commands, integrated user
  sources, realized phase-2 removal, mixture and phase balances, lower-zone
  inventory, residuals, bottom vapor loss, and the same core figures used for
  the original E5 comparison where they remain applicable. For the absorber
  interpretation, bottom phase-2 boundary flux is a supporting diagnostic,
  not a required liquid-removal path.
- **Invalid comparison:** split changes mesh metrics, the lower zone cannot be
  addressed, source signs/units cannot be proven, momentum accounting is
  missing, or children start from unmatched split parents.
- **Allowed next action:** return the completed absorber evidence to the human
  for a separate decision on lower-region feedback, source-capacity limits,
  and any new bounded high-gain family. A future family must preserve the
  lower absorbing-zone abstraction unless the human explicitly selects a
  different controlled change. The gate may not substitute a conventional
  outlet, originate an unbounded gain sweep, or launch automatic follow-on
  work.
- **Claim limit:** even a successful child is a computational, zone-scoped
  source mechanism. Native zone sources are uniform volumetric values; the
  family does not support the former local-cell mass-weighted E5 claim.

## Human locks and handoff rules

- The supplied mesh is the fixed geometry source for the original campaign.
  Its bottom cutoff is accepted as human-reported geometry intent. The H4
  follow-on may split this exact mesh into a lower cell zone, but may not move
  the cutoff or replace the mesh without a further explicit human approval.
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
- Patching or field reset is not an autonomous recovery path. It remains a
  human-only last resort and must not be suggested by the loop.
- `scientific-phase-loop` may not create, select, or promote an experiment
  until a human-approved candidate and gate are recorded here.
- The loop may not start from E0 alone. Before loop entry, the human-requested
  treatment series must be defined, each executable candidate must be
  explicitly approved, and G1 discovery-design coverage must pass independent
  verification.
