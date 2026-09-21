# Phase Context — Phase 7.1A Absorber Convergence and Solver Stability

## Status

### Human contract override — 2026-09-22

Phase 7.1A is completely redirected to a v2 baseline built on the supplied
`Separator-purnanto-60k.msh.h5` mesh. The former lower-inventory controller is
replaced by a throughput-controlled virtual liquid outlet:

\[
Q_{\rm cmd}=|\dot m_{l,in}|,\qquad
S_l=-Q_{\rm cmd}\frac{\alpha_l}
{\max(\int_{V_a}\alpha_l dV,10^{-6}\ {\rm m^3})}.
\]

The sink acts directly on phase 2 only and removes matching liquid momentum;
phase 1 receives no direct mass sink. The lower-zone liquid volume is now a
starvation diagnostic, not the controller input or primary success metric.

The [v2 setup contract](baseline-v2-virtual-liquid-outlet/setup.md) and
[verified build result](baseline-v2-virtual-liquid-outlet/results.md) are the
active Phase 7.1A baseline. The prepared/reopened 60k pair is loaded on
`student`. It contains `60,964` fluid cells, including the `715`-cell
`p71a-v2-virtual-outlet` zone. The one-iteration smoke passed, and the first
controlled v2 inlet-development run is now recorded in
[v2-inlet-loading-ramp/results.md](v2-inlet-loading-ramp/results.md). That
finite-horizon run shows that the lower zone develops enough liquid for the
native applied phase-2 source to track the inlet-derived command in its late
window. It also shows continuously increasing total liquid inventory,
persistent pressure-outlet reverse flow, and residuals that do not qualify as
steady convergence. The throughput result is discovery evidence, not a
qualification or physical-performance claim.

The later request for a Coupled/physical-transient comparison was withdrawn by
the human after execution began. That physical-transient branch is scrapped;
no physical-transient result or claim may be selected from it. A future
Coupled pseudo-transient run must be recorded as a separate setup with its own
verified solver controls and evidence.

All earlier Phase 7.1A families with `results.md` remain historical evidence.
Setup records that had no sibling `results.md` were removed by direct human
instruction. The 2026-09-21 C7/C8 direction and all following text describing
it as active are superseded; they must not be used to select new work.

### Human contract override — 2026-09-21

The dynamic thin-outer-ring work is now an **independent Server-3 C8
discovery family**, built from scratch and unrelated to C7. C8 must not use,
inspect, wait on, transfer, or alter any Server-1 or C7 artifact. Its parent
route is a fresh 237k all-wall Server-3 baseline build followed by a local
all-wall C8-D0 inlet-development run. C8-D0 supplies the selected paired
checkpoint and lower-liquid trigger receipt. The named thin outer ring remains
the only boundary permitted to change, after the declared persistent trigger.
This override replaces the prior C7-to-C8 transfer dependency; all prior
cross-server handoff records remain historical evidence only.

- **Planning state:** reframed discovery design
- **Last human review:** 2026-09-21
- **Experiment-selection authority:** human-approved-context-only
- **Current decision:** preserve the lower cell-zone, phase-2-only absorber as
  the working liquid-removal path, but focus the next discovery work on how
  liquid first develops and reaches the lower separator region. Two selected
  families are controlled low-to-base inlet development and a delayed,
  dynamically activated thin-outer-bottom pressure-boundary intervention.
- **Discovery execution:** the approved T0 / standard k-epsilon / realizable
  k-epsilon queue completed in order on `student` from the exact active-1000
  parent. All three children have paired final artifacts and bounded 500-active
  iteration evidence. The direct human phase-loop invocation now extends the
  same bounded queue through the staged T2-T4 turbulence-family setups.
- **Discovery evidence decision:** the finite screen is informative but does
  not pass a qualification/hypothesis transition. All three branches retain
  nonstationarity, reverse flow, and broad turbulent-viscosity limiting; no
  closure is promoted. The T2-T4 extension remains discovery-only and does not
  authorize a hypothesis route.
- **Steady-state boundary for prior families:** the earlier steady branches
  remain steady-state, and physical transient is not an automatic recovery
  route. The withdrawn physical-transient comparison is scrapped; any future
  pseudo-transient branch must be explicitly separated from these results.
- **Superseded queue:** the unrun T2--T4 turbulence packets and the unrun
  C3+C4 Coupled/Global-Time-Step packet are no longer active selection
  candidates. Their prepared records remain preserved as historical planning
  evidence; they are not deleted or silently reinterpreted.
- **Long-horizon maturity hypothesis:** while running the longer cases, the
  human observed that steady-state assessment may not be meaningful until at
  least roughly `4,000` solver iterations, and that the separator may approach
  a plausible operating condition with roughly `2,000 kg` of total liquid
  inventory. These are Phase 7.1A-specific planning markers raised from the
  current runs, not generic Fluent requirements, convergence criteria, or
  evidence that the `2,000 kg` state is physically validated.
- **Bottom-boundary family:** the prepared 237k thin-outer mesh is now the
  selected platform for an iterative boundary-routing study. The thin outer
  ring must remain a wall during early field development, then become a
  pressure outlet only after a declared, monitor-observed lower-liquid state.
  The pressure range and activation rule are deliberately to be screened; the
  outlet remains phase-permissive and is not a claimed liquid-only drain.

## Human thinking

### Current intent

The human is satisfied that the lower cell-zone absorption idea is the most
promising liquid-removal route found so far. The main Phase 07 goal was to find
a way for lower liquid to disappear while allowing steam to remain in the
separator flow, and that mechanism is now accepted as the working direction.
The human does not yet want to commit to Phase 08 because the absorber itself
has not been shown to converge robustly. The immediate scientific focus now
changes from further turbulence/solver-option screening to forming a liquid
field that reaches the lower separator region before high-throughput flow is
fully established. Both liquid and steam inlets should start below their base
targets and increase gradually to the existing base flow, so gravity can act
on a less forcibly developed initial field. This is a testable numerical
initial-development hypothesis, not a claim that inlet velocity alone makes
the physical separator more effective.

The prepared thin outer bottom band is now treated as an intentionally
artificial, dynamically switched boundary intervention. It should begin as a
wall, remain closed while the early field is predominantly vapor at the lower
region, and be opened only when declared liquid-development monitors show a
sufficient lower-region liquid presence. The study should iterate over a
bounded pressure range and activation times/criteria, with phase-resolved ring
fluxes determining whether the intervention preferentially routes liquid or
merely vents steam.
The human has now selected the contrastive family-screen structure as the
preferred planning route because each family answers a critical, separable
question and should identify useful failures faster than committing to one
solver choice and tuning it extensively before comparing alternatives. This
selected the family-level route; the exact first turbulence queue is now
recorded below and complete.
The human has now selected turbulence as the first and highest-weight family.
The near-term work should therefore spend most of its decision effort on
separating turbulence-closure effects from turbulence-specific numerical and
wall-treatment effects before moving to the remaining solver families.
The human agrees with the recommended first contrast: compare the current RNG
(k)-epsilon closure against the closest available standard or realizable
(k)-epsilon alternative before opening SST or RSM branches. This approves the
first turbulence direction. The exact parent, closure deltas, and short-horizon
gate were then framed and executed; the resulting evidence does not promote a
closure or authorize SST/RSM escalation.
The human's longer-run observation now adds a provisional maturity hypothesis:
the inventory response may need roughly `4,000` steady solver iterations to
develop, with a plausible separator operating inventory near `2,000 kg`.
This hypothesis is to guide observation-window planning only. It must be
tested against bounded late-window behaviour, not converted into an automatic
steady-state pass condition.

### Ideas raised by the human

| ID | Human idea | Why it matters | Status |
| --- | --- | --- | --- |
| H1 | Keep the lower cell-zone absorber and investigate convergence as a separate phase. | Separates the accepted removal mechanism from the unresolved solver-stability problem. | selected direction |
| H2 | Change the other settings one by one, including solver/equation treatment where justified. | Keeps residual improvements interpretable instead of mixing multiple causes. | selected planning principle |
| H3 | Do not promote this to Phase 08 yet. | Preserves uncertainty about whether the absorber is ultimately the right path. | selected phase boundary |
| H4 | Stay with steady-state calculations and do not move into transient modelling. | Keeps the phase focused on finding a steady numerical branch for the selected absorber. | selected hard boundary |
| H5 | Start with high-impact solver/model decisions, then close down to lower-impact numerical settings. | Prevents early tuning of a model family that may be fundamentally unsuitable and gives each branch a clear scientific question. | selected planning structure |
| H6 | Use the previously proposed contrastive family screen as the fastest route to finding what works and what does not. | Makes each run answer a distinct question and preserves useful information even when a branch fails. | selected planning structure; first finite screen complete |
| H7 | Give turbulence first priority and substantially more weight within the family screen. | The observed failure involved (k), epsilon, and turbulent-viscosity limiting, so a deeper turbulence screen can distinguish closure effects from downstream numerical effects. | selected planning priority; first finite screen complete |
| H8 | Begin turbulence screening with the closest matched standard or realizable (k)-epsilon alternative against the RNG reference. | Isolates closure-form effects with less physical and computational change before escalating to SST or RSM. | first finite screen complete; no closure promoted |
| H9 | Treat roughly 4,000 solver iterations as the earliest point at which steady-state assessment may become meaningful, and roughly 2,000 kg total liquid as a plausible operating-point marker. | Allows the inventory response to mature before judging the branch, while keeping the proposed inventory separate from the actual convergence proof. | human-raised planning hypothesis; requires long-horizon evidence |
| H10 | Start both liquid and steam inlets below their base targets, then ramp both to the existing base flow on the 237k thin-outer mesh while every bottom band remains a wall. | Directly tests whether a gentler two-phase formation path increases lower-region liquid presence before high-throughput circulation dominates. | selected direction; exact profile not yet selected |
| H11 | Keep the thin outer bottom ring as a wall initially and dynamically convert it to a pressure outlet only after lower liquid has developed; screen a wide but bounded pressure range. | Tests an artificial boundary analogue for bottom routing while avoiding an initially vapor-dominated open path. | selected direction; activation criterion and pressure ladder not yet selected |

### Constraints expressed by the human

- Liquid removal must remain localized at the bottom/lower cell-zone region.
- Liquid higher in the separator may remain and need not be removed
  immediately.
- Except during the explicitly selected thin-outer-ring intervention, the
  bottom remains a wall. The conventional full-bottom outlet is not selected.
- Steam/vapor must not receive a direct mass sink.
- Patching or resetting the field remains a human-only last resort and is not
  an autonomous recovery route.
- The phase should not be promoted to Phase 08 merely because one numerical
  branch produces low residuals; the absorber must remain interpretable and
  its phase-resolved balances must be credible.
- Transient or time-accurate calculations are outside this phase and may not be
  introduced as an autonomous recovery route.
- The proposed `~4,000`-iteration horizon and `~2,000 kg` total-liquid level
  are maturity/operating-point hypotheses only. Neither is a sufficient
  steady-state acceptance criterion; any claim still requires bounded
  late-window inventory and key-monitor behaviour, credible phase-resolved and
  mixture mass closure including storage/source terms, acceptable residual
  behaviour, and explained routing/reverse-flow behaviour.

## Evidence anchors

- **Observed:** the [Phase 7.1A active-model baseline record](baseline-setup-record.md) captures the current live Fluent readback, active absorber source, numerics, boundaries, dormant branches, and parent/helper reconciliation.
- **Observed:** [Phase 07A absorber family](../phase-07a-simplified-purnanto-liquid-removal/cell-zone-absorber-control-family/index.md) contains the current lower-zone absorber records and source-accounting evidence.
- **Observed:** [Phase 07A cold continuation results](../phase-07a-simplified-purnanto-liquid-removal/cell-zone-absorber-control-family/p7-e5-cz-absorb-cold-ramp11692-cont5000/results.md) reached a valid active-1,960 history but repeatedly diverged in the following block; no active-5,000 endpoint exists.
- **Observed:** the valid late history showed a nearly closed integrated mixture balance while continuity, (k), ε, and volume-fraction residuals rose; pressure-outlet reverse flow and turbulent-viscosity limiting became widespread.
- **Reported:** the [CFD Wiki absorber guidance](../../../CFD_wiki/wiki/synthesis/fluent-separator-efficiency-methods.md) treats the phase-selective lower sink as a diagnostic unresolved-reservoir abstraction and requires source accounting, phase balances, bounded inventory, and residual evidence together.
- **Reported:** the [CFD Wiki model ladder](../../../CFD_wiki/wiki/physics-basis/governing-equations-and-modeling-levels.md) supports keeping a lower-complexity mixture/RNG baseline until the unresolved mechanism specifically requires a different turbulence or phase model.
- **Inferred:** the first convergence screen should target numerical treatment and source/outlet conditioning before replacing the mixture or RNG model family.
- **Missing Info:** which individual change—discretization, relaxation, pressure coupling, phase treatment, turbulence closure, outlet backflow treatment, or source conditioning—most improves the residual trajectory without sacrificing absorber behaviour.

## Current-model audit (read-only, 2026-09-11)

Before creating a Phase 7.1A setup, the currently loaded Fluent session was
inspected through PyFluent and reconciled against the actual P7-E0 readback,
the absorber continuation records, and the reusable carrier-setup helper. No
settings were changed and no iterations were run during this audit.

### Identity and confidence

- **Observed:** the reachable runtime is `student@10.0.0.5:55780`, running
  Fluent 2025 R2; the live session is not currently advancing.
- **Missing Info:** Fluent did not expose a definitive loaded case filename
  through the inspected Settings tree. The loaded state is **Inferred** to be
  from the cold-continuation/recovery lineage because its autosave and report
  roots identify `CellZoneAbsorberColdContinuation` and
  `P7-E5-CZ-ABSORB-COLD-RAMP11692-CONT5000`. That lineage label must not be
  treated as a substitute for a saved case/data identity.
- **Observed:** current general settings, original boundary roles, model
  states, solution methods, and solution controls match the actual P7-E0
  execution/reference readback for the settings that were compared.
- **Observed:** the current live state is not identical to every older source
  snapshot or to the reusable setup helper. Those discrepancies are recorded
  below rather than silently normalized.

### What is actually active

| Area | Live readback | Classification and consequence |
| --- | --- | --- |
| Solver and frame | Pressure-based, absolute velocity formulation, steady; gravity `[0, -9.81, 0]`; operating pressure `0 Pa`; reference pressure method `Connected and disconnected fluid zones` | **Active.** The current branch is a steady pressure-based calculation, not a transient or pseudo-time case. |
| Multiphase | Mixture model; two phases; implicit VOF formulation; dispersed interface; VOF cutoff `1e-6`; implicit body force off | **Active.** Phase 1 is `water-vapor-at-psep`; phase 2 is `water-liquid-at-psep`. The Mixture formulation supplies the phase transport/slip framework used by this branch. |
| Mixture transport equations | Solution equations `flow=true`, `mp=true`, and `drift=true` | **Active solver flags.** The flags show that mixture and drift-related transport equations are being solved. They do not, by themselves, prove a separate interphase mass-transfer law. |
| Turbulence | RNG `k-epsilon`; RNG differential viscosity on; swirl-dominated-flow option on; standard wall functions; curvature correction, Kato-Launder production, production limiter, turbulence damping, and multiphase turbulence dispersion in relative velocity off | **Active.** This is the turbulence closure and wall treatment that must be frozen as the reference before a turbulence comparison. |
| Energy/species | Energy off; species off | **Active absence.** There is no temperature or species equation in the current carrier solve. |
| Pressure/velocity numerics | SIMPLE; Green-Gauss node-based gradients; PRESTO! pressure; second-order-upwind momentum; first-order-upwind `k`; second-order-upwind epsilon; QUICK volume fraction | **Active.** The first-order `k` treatment is especially important: it is part of the current reference and must be explicitly held fixed or declared as a delta in a future turbulence experiment. |
| Solver controls | URFs: pressure `0.3`, momentum `0.7`, `k` `0.8`, epsilon `0.8`, mixture/phase `0.4`, drift `0.1`; all flow, `k-epsilon`, mixture, and drift equations enabled | **Active.** These controls can materially influence residual behaviour and are not safe to infer from a generic recipe. |
| Lower absorber | Fluid zone `p7-e5-lower-y010`; phase-2 mass source enabled at `-379.2377886984495 kg/m3/s`; geometric volume `0.3083026098250161 m3`; integrated command `-116.92 kg/s` | **Active.** This is the liquid-removal mechanism actually in the case: a direct phase-2 cell-zone source, equivalent to a localized lower-zone sink. It is not a conventional outlet and it does not directly remove vapor. |
| Absorber momentum treatment | Lower-zone mixture x/y/z momentum source fields read `-0.0` in the current cold-start state | **Observed, not a hidden sink.** The matched momentum law evaluates from the lower-zone phase-2 velocity basis; in this cold lineage that basis is effectively zero, so the source evaluates to zero. Earlier G100 states had nonzero values. |
| Other fluid zone | `separator-purnanto`; no cell-zone sources | **Active baseline.** The parent zone is not receiving a direct phase-2 or phase-1 source. |
| Boundaries | `liquidinlet` and `steaminlet` are mass-flow inlets; `steamoutlet` is a pressure outlet; `bottom`, `wall`, `separator-purnanto:1`, and `wall:004` are walls | **Active.** The bottom remains a stationary no-slip wall. The steam outlet has gauge pressure `1,120,000 Pa`, Total Pressure backflow specification, and backflow phase-2 volume fraction `0`. |
| Inlet targets | Liquid inlet phase-2 mass flow `116.92 kg/s`, vapor phase-1 mass flow `80.69 kg/s`; the complementary phase targets are zero | **Active.** These are the principal continuous-phase inputs against which the absorber and outlet fluxes must be reconciled. |

The official Fluent documentation describes the Mixture model as computing
secondary-phase slip velocities by default and identifies Drift Force as an
optional drift/slip treatment whose inclusion can noticeably affect
convergence. See [Steps for Using a Multiphase Model](https://ansyshelp.ansys.com/public/views/secured/corp/v251/en/flu_ug/flu_ug_sec_multiphase_setup.html)
and [Setting Up the Mixture Model](https://ansyshelp.ansys.com/public/Views/Secured/corp/v251/en/flu_ug/flu_ug_sec_mphase_using_steps_mixture.html).

### What is configured but not active carrier physics

| Area | Live readback | Interpretation |
| --- | --- | --- |
| Explicit phase interaction | `models.multiphase.phase_interaction` is inactive; the active multiphase children are only `model`, `vof_parameters`, `advanced_formulation`, and `phases` | **Not active/proven.** The current absorber is not being implemented through Fluent's explicit Phase Interaction mass-transfer branch. |
| Linearized mass-transfer switch | `solution.advanced.linearized_mass_transfer_udf=true` | **Configured capability, dormant here.** No active phase-interaction branch, UDF, or user-defined mass-transfer object was found, so this is not evidence that interphase mass transfer is occurring. Fluent documents `DEFINE_LINEARIZED_MASS_TRANSFER` as a UDF mechanism for interphase mass transfer; that is distinct from the current cell-zone phase-2 source. See the [Fluent Customization Manual](https://ansyshelp.ansys.com/public/Views/Secured/corp/v251/en/pdf/Ansys_Fluent_UDF_Manual.pdf). |
| DPM | Continuous-phase interaction off; six injection objects exist, but every current total flow is `1e-20 kg/s`; inlet/outlet fate is escape, walls reflect, and bottom traps | **Dormant/trace objects.** They are not carrying meaningful mass into the current carrier solution and must not be mistaken for the absorber or for active carrier coupling. |
| UDM and expressions | UDM locations `0`, node memory `0`, zone-based UDM false; no named expressions; no user-defined report definitions | **Not active.** There is no discovered UDM or expression-based feedback law behind the absorber. |
| Turbulence extensions | Curvature correction, Kato-Launder production, production limiter, turbulence damping, and multiphase turbulence dispersion off | **Not active.** These are possible future controlled deltas, not hidden contributors in the reference state. |
| Additional physics | Energy/species off; radiation none; acoustics, structure, system coupling, cavitation, boiling, and other exposed latent branches not proven active | **Not active/proven.** Exposed Settings paths are not evidence that the associated physics is enabled. |
| Other boundary branches | Perforated-wall setup method `None`; turbo-specific non-reflecting treatment disabled; general non-reflecting parameters exist but are not an active outlet treatment | **Configured defaults/latent branches.** They are not part of the current boundary physics. |
| Initialization and run state | Hybrid initialization; hybrid iteration count `10`; averaged turbulent parameters enabled; no evidence of a new patch during this audit; run count/readback currently around the recovered continuation state | **Historical/runtime state.** Initialization options are recorded, but a stored option is not proof that a patch was executed. The current iteration counter is not a reliable case identity and has shown a mismatch with monitor-history coordinates. |

### Reconciliation findings that matter before setup design

1. **The absorber mechanism is clear.** The current case removes phase 2 by a
   lower cell-zone source integrated to `116.92 kg/s`. It is not using a bottom
   outlet, explicit interphase mass transfer, DPM coupling, or a vapor sink.
2. **The most consequential undocumented numerical detail is first-order
   `k`.** The reusable helper recipe requests second-order `k`, whereas the
   actual E0 parent readback and current live case both show first-order `k`.
   Therefore the helper is an implementation intention, not the source of
   truth for the present case.
3. **Operating-density wording is another documentation mismatch.** The live
   and actual E0 parent state use `minimum-phase-averaged`, while the helper
   recipe requests `mixture-averaged`. The official Fluent multiphase guide
   identifies `minimum-phase-averaged` as the default and says it is suitable
   for most cases, so this is not automatically an error; it is a setting that
   must be pinned in any comparison.
4. **The DPM lineage is inconsistent in the written/source records.** An older
   source candidate contains finite injection payloads, but the actual E0
   execution manifests and current live state show trace `1e-20 kg/s`
   injections with continuous-phase interaction off. Because the coupling is
   off, this does not explain the current carrier residual failure, but it must
   be classified explicitly rather than inherited silently.
5. **The `linearized_mass_transfer_udf` flag is not the absorber.** It is a
   global capability switch for a UDF mass-transfer mechanism; the live tree
   does not show that mechanism active. The absorber remains the explicit
   cell-zone source.
6. **The live session identity and the selected parent identity are distinct.**
   The live session filename was not exposed by the inspected Settings tree,
   but the selected active-1000 absorber case/data pair is now identified by
   the prior manifest and confirmed present on student by a read-only
   file-existence probe. A future child must still load that pair and archive
   its full parent readback before mutation.

### Audit conclusion

The current model is sufficiently understood to frame the turbulence screen.
The reference is a steady pressure-based, two-phase Mixture/RNG k-epsilon
case with standard wall functions, a lower-zone phase-2-only absorber,
SIMPLE/PRESTO!/QUICK numerics, and first-order k. The apparent unknowns are
mostly lineage and documentation details—not evidence of an unseen active
liquid-removal mechanism.

The selected active-1000 parent and finite T0/standard/realizable queue were
approved after this audit. The independent lifecycle review passed, and the
queue has now completed with full prepared-parent and closure readback for each
child.

## Phase contract

### Phase question

> Can a controlled mixture-field development path and a delayed thin-outer
> bottom-boundary intervention increase and retain liquid in the lower
> separator region while preserving interpretable phase routing and mass
> accounting?

### Scope, invariants, and claim limit

- **In scope:** controlled inlet development from low flow to the existing base
  flow; lower-region liquid-development observation; dynamically switching the
  thin outer bottom band from wall to a pressure outlet; and iterative,
  phase-resolved pressure/activation screening attached to the existing
  absorber branch.
- **Out of scope:** a new liquid-removal mechanism, automatic Phase 08
  promotion, physical brine-outlet validation, transient/time-accurate
  modelling, or unapproved field patching.
- **Must remain fixed:** phase-2-only direct sink, zero direct phase-1 mass
  source, the 237k thin-outer simplified Purnanto mesh, existing base inlet
  targets after a completed ramp, and all bottom bands as walls in C7. In C8,
  the named thin-outer ring is the only bottom boundary permitted to change
  state; all other bottom bands remain walls.
- **Baseline inheritance:** first rebuild a baseline-equivalent state on the
  237k mesh, then apply only the family delta. C7 is assigned to the
  `student` Fluent endpoint and C8 to Server 3. The mesh-specific lower-zone source density may be
  recalculated only to preserve the baseline integrated `-116.92 kg/s`
  phase-2 command; it is not a free source-strength change.
- **Claim limit:** numerical convergence under tested settings only; no plant,
  hardware, or mesh-independent physical claim.

### Useful evidence standard

A useful Phase 7.1A result must include, for each controlled branch:

- native scaled residual histories for continuity, momentum, (k),
  ε, and phase fraction;
- phase-resolved and mixture boundary/source balances, including storage where
  the field is not steady;
- liquid flux entering the absorber and integrated phase-2 sink accounting;
- lower-zone and total liquid inventories;
- steam-outlet liquid carryover and any direct vapor removal;
- pressure, velocity, volume-fraction, reverse-flow, and turbulence-limiting
  behaviour;
- a clear record of the single controlled delta and the settings left fixed;
  and
- a decision record separating genuine convergence improvement from merely
  loosening the residual criterion or hiding an imbalance in a global sum.
- For any long-horizon branch testing H9, preserve the full inventory history
  through at least the proposed `~4,000`-iteration maturity point where the
  run remains numerically valid. If total liquid approaches `~2,000 kg`, treat
  that as a candidate operating-point observation and assess whether the late
  inventory slope and variability actually flatten; do not stop or promote the
  branch because the mass value alone has been reached.
- For inlet development, record both inlet commands and realized phase fluxes,
  lower/adjacent/total liquid inventory, lower-zone liquid fraction, residuals,
  and imbalance throughout the ramp and subsequent base-flow hold. Every C7
  and C8 setup runs for 5,000 active iterations with paired case/data
  checkpoints at 1,000-iteration intervals; a checkpoint is evidence, not a
  convergence claim.
- For the dynamic ring, record the wall/open state and exact switch iteration,
  ring pressure, mixture/vapor/liquid ring fluxes, reverse flow, steam loss,
  inventories, and absorber-source accounting. A switch is not a successful
  liquid-routing event unless those phase-resolved measures support it.

## Candidate experiment pool

The phase direction is selected. The T0/T1 closure records remain completed
discovery evidence. The older C1--C6 and unrun T2--T4/C3C4 rows below are
preserved planning history and are no longer active selection candidates.
The active C7/C8 staged family plan is
[liquid-development-and-dynamic-ring-family.md](liquid-development-and-dynamic-ring-family.md).

| ID | Origin | Controlled delta | Screening question | Required evidence | Artifact/rejection signal | Human status |
| --- | --- | --- | --- | --- | --- | --- |
| C1 | H5/H6 — human-directed family screen | Multiphase formulation/solver family, beginning with the current Mixture baseline and bounded steady alternatives | Is the current phase formulation the main reason the absorber branch cannot reach a steady converged field? | Model readback, phase-fraction histories, residuals, phase routing, absorber delivery, balances, vapor carryover | Alternative form cannot establish a valid steady field, changes the scientific question, or loses auditable phase/source accounting | family selected; follow-on after turbulence screen |
| C2 | H5/H6/H7/H8 — human-directed family screen | First compare RNG (k)-ε with standard and realizable (k)-ε; then isolate RNG production/options, wall treatment, turbulence-equation order, and Mixture turbulence-dispersion coupling; defer SST/RSM escalation | Is the turbulence closure or its treatment, rather than the absorber or another coupled family, driving the (k)/ε and viscosity-limit blow-up? | Turbulence residuals, viscosity limiting, pressure/velocity field, phase balances, carryover, steady convergence, wall-treatment evidence where relevant | Added turbulence complexity worsens stability, or an apparent improvement is caused by an uncontrolled non-turbulence change | first screen complete; T2-T4 extension directly human-authorized |
| C2-T0 | C2 — human-approved turbulence family | Use the active RNG k-epsilon absorber state as the same-parent reference | What is the reproducible baseline against which the two closure changes are judged? | Full baseline readback, residuals, turbulence limits, phase/source balances, inventories, core figures | Parent or readback mismatch; incomplete evidence; no executable comparison basis | `COMPLETE_VERIFIED`; no promotion |
| C2-T1-STD | C2 — human-approved turbulence family | RNG k-epsilon to standard k-epsilon only | Does the standard closure change the coupled turbulence/residual behaviour? | Same-parent closure readback, residuals, turbulence limits, phase/source balances, inventories, core figures | Any uncontrolled non-closure change; phase/source evidence lost; no valid same-parent comparison | `COMPLETE_VERIFIED`; no promotion |
| C2-T1-REAL | C2 — human-approved turbulence family | RNG k-epsilon to realizable k-epsilon only | Does the realizable closure change the coupled turbulence/residual behaviour? | Same-parent closure readback, residuals, turbulence limits, phase/source balances, inventories, core figures | Any uncontrolled non-closure change; phase/source evidence lost; no valid same-parent comparison | `COMPLETE_VERIFIED`; no promotion |
| C2-T2-PROD | C2 — direct human phase-loop extension | RNG production limiter off to on | Does limiting modeled production reduce turbulence instability without hiding phase imbalance? | One-option readback, residuals, turbulence limits, phase/source balances, inventories, core figures | queued; not run |
| C2-T2-DIFF | C2 — direct human phase-loop extension | RNG differential viscosity on to off | Is the RNG differential-viscosity option contributing to viscosity limiting? | One-option readback, residuals, turbulence limits, phase/source balances, inventories, core figures | queued; not run |
| C2-T2-SWIRL | C2 — direct human phase-loop extension | RNG swirl modification on to off | Is the RNG swirl option affecting the recirculating turbulence response? | One-option readback, residuals, turbulence limits, phase/source balances, inventories, core figures | queued; not run |
| C2-T2-KATO | C2 — direct human phase-loop extension | Kato-Launder production treatment off to on | Does Kato-Launder production treatment change the strong-rotation response? | One-option readback, residuals, turbulence limits, phase/source balances, inventories, core figures | queued; not run |
| C2-T3-SCALABLE | C2 — direct human phase-loop extension | Standard to scalable wall functions | Is the finite turbulence response sensitive to near-wall treatment? | Wall/y-plus prerequisite, wall readback, residuals, phase/source balances, inventories, core figures | queued; not run |
| C2-T3-NON-EQ | C2 — direct human phase-loop extension | Standard to non-equilibrium wall functions | Does non-equilibrium wall treatment change recirculating/adverse-gradient response? | Wall/y-plus prerequisite, wall readback, residuals, phase/source balances, inventories, core figures | queued; not run |
| C2-T4-K2 | C2 — direct human phase-loop extension | First- to second-order k discretization | Is first-order k acting as a stabilizer or contributing to the observed trajectory? | k-scheme readback, residuals, turbulence limits, phase/source balances, inventories, core figures | queued; not run |
| C2-T4-DISPERSION | C2 — direct human phase-loop extension | Multiphase relative-velocity turbulence dispersion off to on | Does turbulent dispersion alter phase routing and absorber delivery? | Dispersion readback, residuals, phase routing, absorber/source balances, inventories, core figures | queued; not run |
| C7-INLET-DEVELOPMENT | H10 — direct human reframe | On the 237k thin-outer mesh, begin both liquid and steam inlets below their existing base mass-flow targets and ramp both to the unchanged bases; retain every bottom band as a wall | Does a gentler two-phase field-formation route create more durable lower-region liquid presence before base-flow operation? | Declared ramp profile, commanded/realized phase inlet fluxes, lower/adjacent/total liquid inventories, liquid fraction, residuals, and balances through ramp and hold | No material lower-region liquid development; unacceptable imbalance/instability; or a result that cannot separate ramp effects from an uncontrolled source/boundary change | selected direction; exact profile and initialized 237k parent remain to be defined |
| C8-DYNAMIC-THIN-OUTER-RING | H11 — direct human reframe | On the prepared 237k thin-outer mesh, keep the named ring as a wall during field development, then dynamically change only that ring to a pressure outlet across a bounded pressure/activation screen | Can a delayed artificial boundary intervention route lower liquid without predominantly venting vapor or destroying mass accounting? | Exact switch rule/time, ring pressure, ring mixture/vapor/liquid fluxes, reverse-flow evidence, liquid inventories, vapor loss, source accounting, and residuals | Ring opens before usable lower liquid exists; vapor-dominated loss; unacceptable reverse flow/imbalance; or no liquid-routing response | selected direction; executable trigger and pressure ladder remain to be defined |
| C3 | H5/H6 — human-directed family screen | Steady pressure–velocity algorithm, with a selected model scaffold held fixed | Is continuity limited mainly by pressure correction and velocity coupling? | Coupling/Courant readback, continuity/momentum histories, balances, absorber delivery, warnings | No continuity improvement, immediate AMG instability, or confounded model changes | family selected; follow-on after turbulence screen |
| C4 | H5/H6 — human-directed family screen | Spatial discretization, equation order, under-relaxation, or steady pseudo-time treatment | Can the selected model family be stabilized and then upgraded without changing its physical interpretation? | Scheme/relaxation readback, residual trajectory, order-ramp behaviour, balances, phase routing | Only an over-diffusive first-order endpoint survives, or higher order immediately re-diverges | family selected; follow-on after turbulence screen |
| C3C4-COUPLED-GLOBAL-PSEUDO-TIME | H2/H5/H6 — direct human phase-loop extension | SIMPLE to pressure-based Coupled plus the Coupled-compatible steady Global Time Step / pseudo-time treatment | Can a stronger pressure-coupling and steady pseudo-time solver path bound the difficult active-1000 trajectory without changing absorber interpretation? | Coupling and pseudo-time readback, residuals, limiter/warning diagnostics, phase-resolved fluxes, source delivery, liquid and vapor inventories, reverse-flow evidence, paired checkpoints | Immediate AMG/FPE failure; nonstationary inventories despite longer endurance; loss of phase-selective routing; or unavailable live-supported controls | human-authorized discovery candidate; appended after T2-T4 queue; preflight required |
| C5 | H5/H6 — human-directed family screen | Pressure-outlet reverse-flow specification, with the model and numerical scaffold fixed | Is the large reversed-flow region at the steam outlet feeding the residual instability? | Backflow readback, reversed-face behaviour, phase-resolved outlet fluxes, residuals, vapor/liquid routing | No stability improvement, or neighboring-cell backflow admits unacceptable liquid recirculation | family selected; follow-on after turbulence screen |
| C6 | H5/H6 — human-directed family screen | Mesh/absorber-zone conditioning while preserving the bottom-only absorber concept | Is the source discontinuity or lower-zone resolution the remaining local conditioning problem? | Zone geometry, local mesh evidence, source density/integral, absorber-interface flux, residuals, balances | Improvement cannot be separated from changed absorber extent, or upper liquid is removed | family selected; late follow-on after turbulence screen |

## Proposed high-to-low impact hierarchy

This is a planning proposal, not an executable queue. Every family needs a
common conservative steady scaffold before its scientific result is judged;
otherwise a high-impact model can be confounded by a known numerical failure.

1. **Turbulence family:** closure form first, then turbulence-specific
   numerical treatment and wall/near-wall compatibility where the evidence
   justifies it. The Mixture formulation and absorber remain fixed during this
   first screen.
2. **Multiphase formulation:** Mixture baseline versus a bounded steady
   alternative if the turbulence-focused screen does not explain the failure
   or if the human later prioritizes this branch.
3. **Steady pressure coupling:** SIMPLE, SIMPLEC, or pressure-based coupled
   treatment, with model forms held fixed.
4. **Equation treatment:** spatial order, phase-fraction scheme,
   under-relaxation, and steady pseudo-time stabilization.
5. **Outlet reverse flow:** pressure/backflow specification sensitivity.
6. **Local conditioning:** mesh quality, absorber-zone thickness, or source
   distribution, only after the preceding evidence identifies a local
   conditioning problem.

Physical transient modelling is not part of this hierarchy.

## Turbulence-first focus

Turbulence is the priority family, but it is not a license to vary every
turbulence-related setting simultaneously. The planned narrowing is:

1. **Closure form:** first compare the current RNG (k)-epsilon reference with
   the closest available standard or realizable (k)-epsilon alternative. SST
   and eventually RSM remain deeper planning branches, but neither is part of
   the first screen. No branch is an approved setup until its parent,
   controlled delta, and evidence gate are specified.
2. **Turbulence-specific treatment:** if closure form alone is not decisive,
   isolate the turbulence-equation discretization, relaxation, limiting, or
   steady stabilization treatment that could be driving the observed blow-up.
3. **Wall/near-wall compatibility:** only if mesh and wall evidence show that
   the closure comparison is being controlled by near-wall treatment. This is
   a sensitivity question, not an automatic reason to remesh.

The turbulence family receives priority because the current failure visibly
involved (k), epsilon, and turbulent-viscosity limiting. A turbulence branch
still counts as informative only when continuity, momentum, phase fraction,
absorber delivery, source accounting, outlet carryover, and reverse-flow
behaviour are recorded with it. A lower turbulence residual by itself is not a
winner.

The intended first turbulence decision is therefore:

- **Useful positive result:** a closure or turbulence treatment keeps the
  turbulence field bounded and reduces viscosity limiting while preserving the
  absorber interpretation and the coupled phase/mass evidence.
- **Useful negative result:** the alternatives fail in the same coupled way, or
  only improve after an uncontrolled non-turbulence change. This would reduce
  confidence that closure is the main blocker and move attention to the next
  family without declaring the absorber invalid.

The broader hierarchy remains a planning structure. The closure direction,
parent, and short screen were human-selected; the first three runnable setup
contracts have now completed their required immediate closure readbacks. No
later family is authorized by the finite screen.

## Expected outcomes and decision meaning

The words **best** and **worst** below refer to the outcome of a controlled
steady branch under a common comparison scaffold. They do not mean that a
branch is physically validated or that a failed branch proves the mechanism
impossible. A useful comparison must preserve the lower phase-2-only absorber,
the bottom wall, the same parent state, and the same evidence contract.

| Family | Question answered | Best informative outcome | Worst informative outcome | What the result would let us decide |
| --- | --- | --- | --- | --- |
| Multiphase formulation / solver family | Is the Mixture representation itself preventing a credible steady field, or is the problem elsewhere? | A bounded alternative produces a more stable, auditable steady phase field while preserving lower-zone liquid removal, vapor transparency, and source accounting. | The alternative cannot establish a comparable steady field, loses phase/source traceability, or changes the scientific meaning of the absorber. | Keep Mixture as the defensible working formulation, or promote the alternative only if its phase behaviour and balances are clearly better. |
| Turbulence closure | Are the (k)/epsilon blow-up and widespread turbulent-viscosity limiting mainly a turbulence-closure problem? | One closure reduces turbulence residual growth and viscosity limiting while leaving pressure/phase balances and absorber delivery credible. | Every tested closure is unstable, or an apparent improvement comes only from changing schemes/relaxation or hiding phase imbalance. | Choose the closure with the strongest coupled evidence; if none wins, do not blame RNG alone—the blocker is probably coupled to pressure, source, outlet, or local conditioning. |
| Steady pressure coupling | Is continuity primarily limited by pressure correction and velocity coupling? | A different steady coupling reduces continuity and momentum error without destabilizing (k), epsilon, phase fraction, or the absorber balance. | No continuity improvement, or the coupling causes immediate AMG/velocity instability. | Freeze the model family and use the best pressure-coupling branch for the next numerical refinement. |
| Equation treatment | Is the current discretization/order/relaxation combination too aggressive for this source-dominated flow? | A conservative branch reaches a stable state and can then be upgraded toward the target order without losing the branch. | Only an over-diffusive first-order state survives, or even the conservative branch diverges. | Distinguish a numerical-path problem from a deeper model/source/boundary problem; do not call a low-order endpoint final evidence by itself. |
| Pressure-outlet reverse flow | Is the large reversed-flow region at the steam outlet feeding the instability or contaminating phase routing? | A physically defensible backflow state reduces reverse-flow-driven oscillation without admitting unacceptable liquid through the steam outlet. | Reverse flow and residual behaviour are unchanged, or the outlet becomes a hidden liquid-removal route. | Keep the current outlet treatment and look elsewhere, or justify one narrowly defined boundary correction. |
| Mesh / absorber-zone conditioning | Is the local sink discontinuity or lower-zone resolution creating a local numerical bottleneck? | Conditioning changes stabilize the local source/interface behaviour while preserving the same bottom-only removal interpretation and upper-liquid allowance. | Improvement depends on changing the absorber's effective extent or removes liquid above the intended region. | Treat mesh/source distribution as a late conditioning fix, not as evidence that a different absorber mechanism is required. |

The high-level solver decision is therefore not a single switch. It is a
coupled stack: multiphase formulation, turbulence closure, pressure coupling,
and equation treatment. Turbulence can be made the first priority because the
current failure visibly involved (k), epsilon, and turbulent-viscosity
limiting, but it cannot be solved independently of pressure, momentum, phase
fraction, and the absorber source. A turbulence branch is informative only if
those coupled quantities are recorded together.

The human-reported statement that standard and other k-epsilon options were
previously tried remains useful historical planning context, but the matched
Phase 7.1A T0/standard/realizable records are now the current evidence. They
show closure-dependent finite trajectories without a stationary or qualified
branch; historical runs from other phases remain non-interchangeable with the
present absorber/geometry.

## Approved screening campaign

The contrastive family-screen route and the turbulence-first direction are
human-selected. The initial turbulence planning packet is recorded in the
[turbulence-family README](turbulence-family/README.md), with paired draft
records for the reference, closure, RNG-option, wall-treatment,
turbulence-equation, and multiphase-dispersion branches.

The finite first screen of T0 RNG reference, standard k-epsilon, and realizable
k-epsilon was human-approved, passed the lifecycle review, and has now been
executed in order. The direct human phase-loop invocation now extends the
queue through the staged T2-T4 packets. The queue uses the active-1000 absorber
parent in [parent-reference.md](turbulence-family/parent-reference.md). Each
child must perform the required complete parent readback, single declared
delta, save/reopen, smoke test, 500-active attached solve, and evidence
extraction.

## Discovery execution and evidence outcome

The three results are recorded at:

- [T0 RNG reference](turbulence-family/t0-rng-reference/results.md)
- [T1 standard k-epsilon](turbulence-family/t1-standard-kepsilon/results.md)
- [T1 realizable k-epsilon](turbulence-family/t1-realizable-kepsilon/results.md)

The exact parent case/data hashes were read before each mutation as
`cd7f27b45435b0c381f9f01bc02e7a3bce3655fbd6269175aab60c262c4c29d3` and
`16b77042d1d62eb3a56aee1b01aee1bfa9fadf96a94f3c3804c6eab12705268b`. The
active source readback remained `-116.9200000000002 kg/s` on
`p7-e5-lower-y010` for the three successful children. No child introduced an
outlet, transient model, patch, reset, remesh, resplit, or restart-field
alteration.

The family comparison shows closure-dependent finite trajectories, but none is
stationary or numerically qualified over the short horizon. Continuity,
inventory drift, reverse flow, and viscosity limiting remain coupled concerns;
the selected-cell histories also do not provide the planned contour-level
spatial evidence. Therefore `DISCOVERY_EXECUTION` passes while
`DISCOVERY_EVIDENCE` remains blocked for a hypothesis/qualification route.
The first realizable preflight blocker and its corrected fresh-parent retry are
preserved under [the realizable attempts directory](turbulence-family/t1-realizable-kepsilon/attempts/).

## Conditional qualification path

### Q-TURB-CLOSURE — turbulence closure qualification

This is a named conditional path, not an authorization to run it.

- **Triggered only by:** the completed T0/standard/realizable discovery screen
  and a passing DISCOVERY_EVIDENCE review that identifies one closure as a
  defensible candidate or shows that all three fail in the same coupled way.
- **Hypothesis:** under the frozen absorber, boundary, Mixture, and numerical
  scaffold, the selected turbulence closure can maintain a bounded,
  phase-accountable steady branch over a declared qualification window.
- **Strongest competing explanation:** the dominant blocker is pressure
  coupling, source/local conditioning, outlet reverse flow, or turbulence
  discretization rather than closure form.
- **Qualification horizon:** at least 10,000 steady iterations unless a later
  gate explicitly records a scoped shorter qualification with a narrower claim.
- **Required evidence:** native residual histories, phase-resolved balances,
  absorber realization, liquid inventories, outlet routing, turbulence
  limiting, continuation/restart evidence, and core figures.
- **Claim limit:** no plant, mesh-independent, or physical brine-interface
  claim.

## Decision gates

The independent lifecycle review passed for the finite first-screen queue on
2026-09-11. The direct human phase-loop invocation now extends execution to
the staged T2-T4 contracts; this remains discovery-only and does not establish
that any closure or turbulence treatment qualifies.

### G0 — Phase 7.1A candidate framing

- **Evidence required:** one human-approved controlled delta; unchanged
  absorber invariants; exact parent/reference; evidence contract; short
  horizon; and a rejection/continue condition.
- **Decision condition:** the candidate changes one declared non-absorber
  treatment and can distinguish residual convergence from source-dominated or
  globally cancelled mass balance.
- **Allowed next action:** this gate allowed the original three packets and,
  by direct human phase-loop invocation, the eight staged T2-T4 packets listed
  below to enter the attached discovery queue. Every item must still satisfy
  exact-parent, one-delta, save/reopen, smoke, horizon, and evidence gates.
- **Not established by this gate:** absorber physical validity, steady-state
  qualification, or Phase 08 readiness.
- **Human-return condition:** an option requires changing the absorber
  mechanism, introducing an outlet, patching/resetting, introducing transient
  modelling, or combining multiple unresolved treatments.

## Phase Loop setup queue

The following is the human-approved finite queue. It is the only queue entering
Phase Loop from this context:

| Order | Setup path | Candidate | Lifecycle role | Required gate |
| --- | --- | --- | --- | --- |
| 1 | turbulence-family/t0-rng-reference/setup.md | C2-T0 | discovery-reference | DISCOVERY_DESIGN |
| 2 | turbulence-family/t1-standard-kepsilon/setup.md | C2-T1-STD | discovery | DISCOVERY_DESIGN |
| 3 | turbulence-family/t1-realizable-kepsilon/setup.md | C2-T1-REAL | discovery | DISCOVERY_DESIGN |
| 4 | turbulence-family/t2-rng-production-limiter/setup.md | C2-T2-PROD | discovery | DISCOVERY_DESIGN |
| 5 | turbulence-family/t2-rng-differential-viscosity-off/setup.md | C2-T2-DIFF | discovery | DISCOVERY_DESIGN |
| 6 | turbulence-family/t2-rng-swirl-off/setup.md | C2-T2-SWIRL | discovery | DISCOVERY_DESIGN |
| 7 | turbulence-family/t2-rng-kato-launder/setup.md | C2-T2-KATO | discovery | DISCOVERY_DESIGN |
| 8 | turbulence-family/t3-scalable-wall-functions/setup.md | C2-T3-SCALABLE | discovery | DISCOVERY_DESIGN |
| 9 | turbulence-family/t3-non-equilibrium-wall-functions/setup.md | C2-T3-NON-EQ | discovery | DISCOVERY_DESIGN |
| 10 | turbulence-family/t4-k-second-order/setup.md | C2-T4-K2 | discovery | DISCOVERY_DESIGN |
| 11 | turbulence-family/t4-multiphase-turbulence-dispersion/setup.md | C2-T4-DISPERSION | discovery | DISCOVERY_DESIGN |
| 12 | solver-path-family/c3c4-coupled-global-pseudo-time/setup.md | C3C4-COUPLED-GLOBAL-PSEUDO-TIME | discovery | DISCOVERY_DESIGN extension |

## Autonomous recovery and handoff rules

- Preserve the lower cell-zone absorber and its phase-selective interpretation
  unless the human explicitly approves a new absorber change.
- Do not introduce a transient branch as a recovery route; inability to obtain
  a steady branch is evidence to return to the human for reframing.
- A residual improvement does not override phase-resolved source accounting,
  vapor transparency, or lower-zone delivery evidence.
- A failed candidate may motivate a narrow research or sensitivity note, but it
  may not silently originate a new model family or Phase 08 direction.
- Patching/resetting fields remains outside autonomous recovery.
- Phase Loop may execute only a future declared setup queue; it may not invent
  the one-at-a-time convergence matrix.
