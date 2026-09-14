# Phase Context — Phase 7.1A Absorber Convergence and Solver Stability

## Status

- **Planning state:** phase framing
- **Last human review:** 2026-09-11
- **Experiment-selection authority:** human-approved-context-only
- **Current decision:** preserve the lower cell-zone, phase-2-only absorber as
  the working liquid-removal path and begin the convergence-focused phase with
  a matched turbulence-closure comparison before considering Phase 08.
- **Steady-state boundary:** the phase remains steady-state. A transient or
  time-accurate solver branch is not an automatic fallback and is outside the
  current Phase 7.1A experiment families.

## Human thinking

### Current intent

The human is satisfied that the lower cell-zone absorption idea is the most
promising liquid-removal route found so far. The main Phase 07 goal was to find
a way for lower liquid to disappear while allowing steam to remain in the
separator flow, and that mechanism is now accepted as the working direction.
The human does not yet want to commit to Phase 08 because the absorber itself
has not been shown to converge robustly. Phase 7.1A should therefore preserve
the absorber and systematically change the remaining numerical or modelling
choices until the scaled residuals and continuity behaviour are understood.
The human now wants the work organized from high-impact decisions down to
lower-impact numerical refinement: first assess the governing solver/model
families and turbulence closure, then narrow into pressure coupling,
discretization, relaxation, and boundary details. The solution space should be
enumerated through controlled steady branches rather than by starting with a
large under-relaxation or scheme sweep.
The human has now selected the contrastive family-screen structure as the
preferred planning route because each family answers a critical, separable
question and should identify useful failures faster than committing to one
solver choice and tuning it extensively before comparing alternatives. This
selects the family-level route, not yet an exact setup queue or every branch
within each family.
The human has now selected turbulence as the first and highest-weight family.
The near-term work should therefore spend most of its decision effort on
separating turbulence-closure effects from turbulence-specific numerical and
wall-treatment effects before moving to the remaining solver families.
The human agrees with the recommended first contrast: compare the current RNG
(k)-epsilon closure against the closest available standard or realizable
(k)-epsilon alternative before opening SST or RSM branches. This approves the
first turbulence direction, but the exact alternative, parent state, and
short-horizon gate still require evidence and setup framing.

### Ideas raised by the human

| ID | Human idea | Why it matters | Status |
| --- | --- | --- | --- |
| H1 | Keep the lower cell-zone absorber and investigate convergence as a separate phase. | Separates the accepted removal mechanism from the unresolved solver-stability problem. | selected direction |
| H2 | Change the other settings one by one, including solver/equation treatment where justified. | Keeps residual improvements interpretable instead of mixing multiple causes. | selected planning principle |
| H3 | Do not promote this to Phase 08 yet. | Preserves uncertainty about whether the absorber is ultimately the right path. | selected phase boundary |
| H4 | Stay with steady-state calculations and do not move into transient modelling. | Keeps the phase focused on finding a steady numerical branch for the selected absorber. | selected hard boundary |
| H5 | Start with high-impact solver/model decisions, then close down to lower-impact numerical settings. | Prevents early tuning of a model family that may be fundamentally unsuitable and gives each branch a clear scientific question. | selected planning structure |
| H6 | Use the previously proposed contrastive family screen as the fastest route to finding what works and what does not. | Makes each run answer a distinct question and preserves useful information even when a branch fails. | selected planning structure; exact first candidate pending |
| H7 | Give turbulence first priority and substantially more weight within the family screen. | The observed failure involved (k), epsilon, and turbulent-viscosity limiting, so a deeper turbulence screen can distinguish closure effects from downstream numerical effects. | selected planning priority; exact branches pending |
| H8 | Begin turbulence screening with the closest matched standard or realizable (k)-epsilon alternative against the RNG reference. | Isolates closure-form effects with less physical and computational change before escalating to SST or RSM. | selected first turbulence direction; exact alternative pending verification |

### Constraints expressed by the human

- Liquid removal must remain localized at the bottom/lower cell-zone region.
- Liquid higher in the separator may remain and need not be removed
  immediately.
- The bottom remains a wall; a conventional bottom outlet is not the selected
  absorber representation.
- Steam/vapor must not receive a direct mass sink.
- Patching or resetting the field remains a human-only last resort and is not
  an autonomous recovery route.
- The phase should not be promoted to Phase 08 merely because one numerical
  branch produces low residuals; the absorber must remain interpretable and
  its phase-resolved balances must be credible.
- Transient or time-accurate calculations are outside this phase and may not be
  introduced as an autonomous recovery route.

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
approved after this audit. The queue remains non-executable until the
independent lifecycle review passes and the implementation performs full
prepared-parent and closure readback.

## Phase contract

### Phase question

> Can the selected bottom-only cell-zone absorber reach credible scaled-residual
> and continuity convergence while preserving phase-selective liquid removal?

### Scope, invariants, and claim limit

- **In scope:** one-at-a-time convergence and stability sensitivities attached
  to the existing absorber branch.
- **Out of scope:** a new liquid-removal mechanism, automatic Phase 08
  promotion, physical brine-outlet validation, transient/time-accurate
  modelling, or unapproved field patching.
- **Must remain fixed:** bottom-only absorber interpretation, phase-2-only
  direct sink, zero direct phase-1 mass source, bottom wall, and the simplified
  Purnanto geometry for the primary comparison.
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

## Candidate experiment pool

The phase direction is selected. The human has approved the finite first
turbulence screen, but its lifecycle execution gate remains pending.

| ID | Origin | Controlled delta | Screening question | Required evidence | Artifact/rejection signal | Human status |
| --- | --- | --- | --- | --- | --- | --- |
| C1 | H5/H6 — human-directed family screen | Multiphase formulation/solver family, beginning with the current Mixture baseline and bounded steady alternatives | Is the current phase formulation the main reason the absorber branch cannot reach a steady converged field? | Model readback, phase-fraction histories, residuals, phase routing, absorber delivery, balances, vapor carryover | Alternative form cannot establish a valid steady field, changes the scientific question, or loses auditable phase/source accounting | family selected; follow-on after turbulence screen |
| C2 | H5/H6/H7/H8 — human-directed family screen | First compare RNG (k)-ε with standard and realizable (k)-ε; then isolate RNG production/options, wall treatment, turbulence-equation order, and Mixture turbulence-dispersion coupling; defer SST/RSM escalation | Is the turbulence closure or its treatment, rather than the absorber or another coupled family, driving the (k)/ε and viscosity-limit blow-up? | Turbulence residuals, viscosity limiting, pressure/velocity field, phase balances, carryover, steady convergence, wall-treatment evidence where relevant | Added turbulence complexity worsens stability, or an apparent improvement is caused by an uncontrolled non-turbulence change | family selected; finite first screen approved, lifecycle gate pending |
| C2-T0 | C2 — human-approved turbulence family | Use the active RNG k-epsilon absorber state as the same-parent reference | What is the reproducible baseline against which the two closure changes are judged? | Full baseline readback, residuals, turbulence limits, phase/source balances, inventories, core figures | Parent or readback mismatch; incomplete evidence; no executable comparison basis | approved first-screen control; ready for Phase Loop |
| C2-T1-STD | C2 — human-approved turbulence family | RNG k-epsilon to standard k-epsilon only | Does the standard closure change the coupled turbulence/residual behaviour? | Same-parent closure readback, residuals, turbulence limits, phase/source balances, inventories, core figures | Any uncontrolled non-closure change; phase/source evidence lost; no valid same-parent comparison | approved first-screen branch; ready for Phase Loop |
| C2-T1-REAL | C2 — human-approved turbulence family | RNG k-epsilon to realizable k-epsilon only | Does the realizable closure change the coupled turbulence/residual behaviour? | Same-parent closure readback, residuals, turbulence limits, phase/source balances, inventories, core figures | Any uncontrolled non-closure change; phase/source evidence lost; no valid same-parent comparison | approved first-screen branch; ready for Phase Loop |
| C3 | H5/H6 — human-directed family screen | Steady pressure–velocity algorithm, with a selected model scaffold held fixed | Is continuity limited mainly by pressure correction and velocity coupling? | Coupling/Courant readback, continuity/momentum histories, balances, absorber delivery, warnings | No continuity improvement, immediate AMG instability, or confounded model changes | family selected; follow-on after turbulence screen |
| C4 | H5/H6 — human-directed family screen | Spatial discretization, equation order, under-relaxation, or steady pseudo-time treatment | Can the selected model family be stabilized and then upgraded without changing its physical interpretation? | Scheme/relaxation readback, residual trajectory, order-ramp behaviour, balances, phase routing | Only an over-diffusive first-order endpoint survives, or higher order immediately re-diverges | family selected; follow-on after turbulence screen |
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

This remains a planning structure. The closure direction, parent, and short
screen are now human-selected, but the runnable setup contracts remain
non-executable until the lifecycle gate passes and the implementation performs
the required immediate closure readback.

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
previously tried is useful planning prior, but no directly matched Phase 7A
records have yet been located that are strong enough to mark those branches as
rejected results. Historical runs from other phases are not interchangeable
with the present absorber/geometry. Until a matched record is recovered, those
options remain prior context rather than closed Phase 7.1A conclusions.

## Approved screening campaign

The contrastive family-screen route and the turbulence-first direction are
human-selected. The initial turbulence planning packet is recorded in the
[turbulence-family README](turbulence-family/README.md), with paired draft
records for the reference, closure, RNG-option, wall-treatment,
turbulence-equation, and multiphase-dispersion branches.

The finite first screen of T0 RNG reference, standard k-epsilon, and realizable
k-epsilon is human-approved and recorded as a draft queue in
[phase-state.yaml](phase-state.yaml). The queue uses the active-1000 absorber
parent in [parent-reference.md](turbulence-family/parent-reference.md).
It remains non-executable until the independent lifecycle review passes and
each child performs its required prepared readback.

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
2026-09-11. The queue is now ready to enter Phase Loop; this does not establish
that any setup has run or that the turbulence family will qualify.

### G0 — Phase 7.1A candidate framing

- **Evidence required:** one human-approved controlled delta; unchanged
  absorber invariants; exact parent/reference; evidence contract; short
  horizon; and a rejection/continue condition.
- **Decision condition:** the candidate changes one declared non-absorber
  treatment and can distinguish residual convergence from source-dominated or
  globally cancelled mass balance.
- **Allowed next action:** enter Phase Loop with the three paired setup packets
  listed below. Phase Loop must still verify the exact parent, read back the
  complete active state, apply only the declared closure delta, save/reopen,
  and smoke-test each child before solving.
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
