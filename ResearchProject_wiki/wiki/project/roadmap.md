# Project Roadmap

## Purpose
Create an efficient run sequence from the current project state. Because ANSYS setup is slow and each solve can take hours, every run must have a decision purpose before it is launched.

## Current Starting Point
- Date: 2026-05-21
- Active case: `FFF-2`, with `MWH-WP-2026-05-07-A` retained as the downstream water-pool diagnostic.
- Current phase: parent-case convergence recovery before split-inlet/brine-outlet interpretation.
- Current problem: the mixed wet-half velocity-inlet parent case already has convergence and liquid mass-balance problems after approximately `1020` steady iterations, even without an initialized water pool. The initialized-water-pool case then adds a second failure mode: patched liquid inventory depletion and extreme steam-outlet liquid carryover.
- Current controlled setup change: a `FFF-2` derivative has been prepared with `Operating Pressure = 0 Pa`, both pressure outlets set to `1120000 Pa`, and inlet pressure set to `1140000 Pa`, with all other settings kept the same as `FFF-2`. `Inferred`: this tests pressure-reference parity with Purnanto 2013, where gauge and absolute pressures were treated as equivalent.
- Current controlled setup result: after just above 100 iterations, residuals were user-reported as smooth and flattening, but fluxes remained physically off because liquid inlet was approximately `109.8065 kg/s` while liquid outflow through the outlets was effectively zero. `Inferred`: pressure-reference parity may improve numerical residual behavior but does not yet provide a defensible liquid mass-balance path.
- `Inferred`: the next work should first fix or classify the parent `FFF-2` convergence/mass-balance problem before changing geometry, pressure settings, inlet split, water-pool initialization, mesh, or physics model.
- `Inferred`: because only `FFF-2` and `MWH-WP-2026-05-07-A` exceed `1000` iterations, older lower-iteration outputs should be excluded from quantitative future-scope decisions and kept only as setup/debug history.

## Operating Rules
1. Do not launch a run unless it has one primary question, one planned comparison, and a written stop condition.
2. Change one major feature at a time: initialization, outlet geometry, outlet pressure, inlet allocation, mesh, or physics model.
3. Use short diagnostic runs before long production runs when the expected failure mode should appear early.
4. Save a minimum evidence package for every run:
   - case/data file name,
   - residual history,
   - mass-flow report by phase and outlet,
   - liquid volume fraction near steam outlet and brine outlet,
   - velocity vectors or streamlines near steam outlet intake,
   - pressure drop estimate,
   - short conclusion: `keep`, `reject`, or `needs follow-up`.
5. Define the external or analytical comparison target before any long production run.
6. Keep partner validation/parameter-sweep work separate until Shuhei has one physically stable case to compare, but use partner outputs early as validation target ranges.
7. Do not use low-iteration runs as performance evidence. A short diagnostic run may identify an obvious failure mode, but report-facing results require a documented iteration budget, residual/monitor history, phase mass balance, and physical monitor stability.

## Validation Gate
The roadmap is not complete unless it answers "what should the result be?" before "what should I change next?"

### Required Target Table
Create a small validation target table before R5/R6 production runs:
- inlet mass flow and phase split used by the model,
- expected pressure drop or acceptable pressure-drop range,
- expected steam outlet quality or maximum liquid carryover range,
- expected brine outlet liquid flow or qualitative drainage behavior,
- expected separator efficiency or design benchmark,
- source type: `real-world data`, `analytical estimate`, `design correlation`, `literature CFD`, or `trend-only`.

### Current Benchmark Sources
- `Reported`: spiral-inlet BOC design checks from `../../CFD_wiki/wiki/setups/geothermal-separator-design-screening-2014-overview.md`; Bangma/Lazalde-Crabtree evidence is used only where it is presented as general BOC or empirical separator-performance context.
  - Inlet velocity sanity band: approximately `30-40 m/s`.
  - Breakdown velocity warning: approximately `42 m/s`.
  - Expected separator efficiency range: approximately `99.5-99.99%`.
- `Reported`: Purnanto 2013 separator CFD validation pattern from `../../CFD_wiki/wiki/sources/purnanto-2013-cfd-geothermal-separator.md`.
  - Compare outlet steam quality against Lazalde-Crabtree empirical calculation and Webre separator field-trend data.
  - For this project, prioritize the spiral-inlet result and use other geometries only as method/context.
  - The spiral-inlet case near `26.81 m/s` showed unexpected outlet-quality behavior, so this operating point is known to be sensitive.
- `Reported`: Mubarok 2020 geothermal CFD validation structure from `../../CFD_wiki/wiki/sources/mubarok-2020-cfd-geothermal-flow-meters.md`.
  - Use field/analytical comparison outputs, relative-error reporting, and mesh extrapolation style as the validation-reporting template.
  - Mesh independence should be judged on output stability, not only cell count.
- `Inferred`: DPM carryover check from `../../CFD_wiki/wiki/setups/geothermal-boc-separator-fluent-2013-baseline.md`.
  - After a stable continuous/mixture field exists, inject droplets and classify `trapped`, `escaped`, and `incomplete` particles to estimate steam outlet carryover.
  - Use this as a separate carryover sanity check, not as the first step while the continuous solution is still physically unstable.

### Sanity-Check Equations
- Separator efficiency from carryover:
  - `eta_s = m_s / (m_s + m_b) * 100`
  - `eta_s = (m_w - m_b) / m_w * 100`
- Lazalde-Crabtree empirical efficiency structure, used only as a comparison method for the spiral-inlet case:
  - `eta_eff = eta_m * eta_A`
- Steam pressure-drop check:
  - `Delta P = (NH * u^2 * rho_v) / 2`
  - `NH = 16 * Ao / De^2`
  - `u = QVS / Ao`
- Dryness/phase split check from geothermal two-phase validation workflow:
  - `x = (h - h_f) / h_fg`
  - `m_g = x * m`
  - `m_f = (1 - x) * m`

### How To Use The Gate
- If a metric has real-world or analytical backing, use it as a pass/fail sanity check.
- If a metric has literature-only backing, use it as directional evidence.
- If a metric has no external target, label it `trend-only` and do not use it as proof that the model is correct.
- If the baseline-like case misses all target bands, pause design comparisons and fix baseline assumptions first.
- If the run is below the expected breakdown velocity but still produces extreme steam-outlet liquid carryover, classify that as a setup/geometry/numerics red flag before treating it as physical separator failure.

## Phase 0 | Parent Convergence Triage

### Goal
Extract as much information as possible from `FFF-2` before spending solver time or interpreting the water-pool case. The immediate priority is to understand why the parent no-water-pool case remains non-converged and liquid-imbalanced after more than `1000` iterations.

### Tasks
- Export `FFF-2` residual history and physical monitor history if available.
- Export phase mass-flow reports at available iteration points, especially liquid inlet, brine outlet, steam outlet, and net liquid imbalance.
- Check whether the `FFF-2` liquid imbalance is trending toward zero, staying flat, or worsening after iteration `1020`.
- Confirm outlet backflow phase fractions and pressure settings in the parent case before any water-pool or geometry changes.
- Run or post-process the `FFF-2` pressure-reference parity derivative where `Operating Pressure = 0 Pa`, steam/brine outlet gauge pressures are `1120000 Pa`, and inlet pressure is `1140000 Pa`; compare only against original `FFF-2`.
- For `FFF-2-OP0`, inspect whether liquid volume fraction is moving toward the brine outlet before extending the run; do not accept the smoother residuals alone as convergence evidence.
- Plot liquid volume fraction and velocity vectors near the brine outlet and steam outlet to see whether outlet behavior is numerically plausible before patched water is introduced.
- Check mesh/worst-cell locations in inlet, brine outlet, steam outlet, and main swirl regions.
- Collect partner/analytical target values for pressure drop, steam outlet quality/carryover, brine outlet liquid flow, and separator efficiency if available.
- Calculate implied separator efficiency only if steam-outlet liquid carryover is physically meaningful for the case state; otherwise label it `not interpretable`.
- Compare current inlet velocity against the reported `30-40 m/s` effective band and `~42 m/s` breakdown warning.

### Decision
- If `FFF-2` residuals and phase mass balance are still unstable, run a parent convergence-control case before any water-pool interpretation.
- If `FFF-2` liquid imbalance is driven by brine outlet behavior, prioritize brine outlet pressure/backflow/outlet-type checks.
- If `FFF-2` is stable except for localized steam-outlet or brine-outlet artifacts, use that finding to choose the first geometry/outlet sensitivity.
- Only return to `MWH-WP-2026-05-07-A` after the parent no-water-pool case has a defensible convergence path or a clearly documented failure cause.

## Phase 1 | Cheap Control Runs

### Run R1 | Parent Convergence Control
- Primary question: why does `FFF-2` fail to converge or balance liquid even without an initialized water pool?
- Change from current parent case: keep geometry, inlet split, no-water-pool initialization, mesh, physics, and outlet gauge values fixed while changing only the pressure reference to `Operating Pressure = 0 Pa`, using inlet pressure `1140000 Pa` and both outlet pressure boundaries at `1120000 Pa`.
- Suggested budget: short steady diagnostic run first; extend only if early trends are physically plausible.
- Sanity check: residuals and phase mass-flow imbalance should trend toward stable values before performance metrics are interpreted.
- Success signal: liquid imbalance reduces toward a physically plausible steady balance and residual/monitor behavior becomes stable enough to justify continuing.
- Failure signal: parent case remains unstable, liquid imbalance worsens, or residuals improve while liquid drainage remains physically blocked or absent.
- Next branch:
  - If success: use the stabilized parent setup as the reference path before revisiting water-pool or split-inlet claims.
  - If failure: classify whether the failure is outlet boundary behavior, mesh/numerics, inlet allocation, or geometry.

### Run R2 | Outlet Boundary Sensitivity
- Primary question: is the parent convergence problem caused by brine outlet or steam outlet boundary behavior?
- Change from prior accepted control: adjust only outlet pressure/backflow/outlet treatment according to the Phase 0 diagnosis.
- Suggested budget: short steady diagnostic run, focused on liquid volume fraction and streamlines near steam outlet.
- Sanity check: outlet changes should improve monitor stability and phase mass balance without destroying the intended swirl structure.
- Success signal: parent case trends toward stable phase balance and interpretable outlet behavior.
- Failure signal: outlet behavior remains unstable or nonphysical after one controlled outlet change.
- Next branch:
  - If success: freeze outlet setup before retesting water-pool initialization.
  - If failure: move to mesh/numerics or steam-outlet geometry/intake sensitivity.

### Run R3 | Water-Pool Initialization Recheck
- Primary question: after the parent case has a defensible convergence path, does initialized lower water improve brine outlet behavior or only introduce inventory-depletion artifacts?
- Change from accepted parent control: add the lower water-pool initialization only.
- Suggested budget: short-to-medium steady diagnostic run, or transient if Phase 0/R1 indicates steady inventory depletion is unavoidable.
- Sanity check: water-pool initialization should not make liquid outflow exceed inlet liquid by orders of magnitude after the parent case has been stabilized.
- Success signal: brine outlet liquid removal becomes more realistic without extreme steam-outlet carryover or inventory depletion.
- Failure signal: patched water drains or is entrained into the steam outlet even after parent convergence controls.
- Next branch:
  - If success: continue toward baseline-like reference with documented initialization.
  - If failure: keep water-pool initialization as a failed/uncertain approach and use a different controlled reference strategy.

### Run R4 | Brine Outlet Pressure/Boundary Control
- Primary question: is brine outlet behavior forcing nonphysical liquid removal?
- Change from prior accepted control: adjust only brine outlet pressure or outlet boundary treatment.
- Suggested budget: short-to-medium steady run after R1/R2 classify the parent outlet behavior.
- Sanity check: brine outlet flow should support mass balance and water-level realism; it should not drain an artificial inventory faster than inlet liquid supply can justify.
- Success signal: brine outlet removes liquid without draining an initialized inventory or creating extreme mass imbalance.
- Failure signal: liquid split remains dominated by outlet boundary artifact.
- Next branch:
  - If success: freeze outlet setup and proceed to inlet-allocation testing.
  - If failure: document brine outlet as active limitation and use qualitative flow-field comparisons only.

## Post-Triage Model Upgrade Gate

### Purpose
Use this gate only after Phase 0 and the cheap control runs have made the parent `FFF-2` failure mode clearer. The goal is to decide whether the project should keep using the Purnanto-style separator baseline as-is, borrow a newer geothermal Fluent workflow, or reserve more complex annular-flow modelling for future work.

### Evidence Snapshot From CFD Wiki
| Source | How two-phase flow is modelled | Relevance to this project |
| --- | --- | --- |
| `Reported`: Purnanto, Zarrouk, and Cater 2013, `../../CFD_wiki/wiki/sources/purnanto-2013-cfd-geothermal-separator.md` | Legacy separator model: steady, incompressible, isothermal, no flashing; RNG `k-epsilon`; mixture/DPM wording is internally inconsistent, but the practical wiki interpretation is continuous-field solve followed by DPM carryover checking. | Closest separator-geometry reference, but reproducibility is limited by missing initialization fields, convergence targets, URFs, mesh quality metrics, and detailed DPM injection controls. |
| `Reported`: Mubarok et al. 2020, `../../CFD_wiki/wiki/sources/mubarok-2020-cfd-geothermal-flow-meters.md` | Geothermal two-phase Fluent model using `Mixture` multiphase model, SST `k-omega`, energy equation, steady/transient benchmarking, field validation, and Richardson-style mesh refinement. | Best newer geothermal Fluent workflow in the CFD wiki. It is a flow-meter paper rather than a separator paper, so copy its validation, mesh, and solver-discipline patterns rather than its geometry. |
| `Reported`: Skoog 2020, `../../CFD_wiki/wiki/sources/skoog-2020-annular-flow-three-field-cfd-thesis.md` | Three-field annular model with steam core, liquid wall film, and droplets using EWF + DPM + UDF entrainment/deposition coupling. | Useful if the inlet or wall region must be interpreted as annular film/droplet flow, but too complex and indirect to use before the parent separator case is stable. |
| `Reported`: Mondal and Sharma 2024, `../../CFD_wiki/wiki/sources/mondal-sharma-2024-air-water-annular-flow-cfd.md` | Fluent 19.2 transient DPM + Eulerian Wall Film + SST `k-omega`, with UDF entrainment correlations and entrainment-fraction validation. | Strong modern example for gas-core/wall-film/droplet entrainment, but it is air-water vertical-tube CFD rather than geothermal steam-brine separator CFD. |

### Project Interpretation
- `Inferred`: the Purnanto 2013 paper should remain the separator geometry and legacy baseline reference, but not the only source for modern Fluent practice.
- `Inferred`: if Phase 0/R1-R4 show that the current problem is mostly numerical, mesh, or steady-solver stability rather than inlet physics, the first physics/numerics upgrade should be a Mubarok-style `Mixture` + SST `k-omega` workflow with stronger mesh/output validation.
- `Inferred`: DPM should remain a post-convergence carryover sanity check until the continuous/mixture field has stable mass balance and interpretable outlet behavior.
- `Inferred`: EWF + DPM three-field modelling should be kept as future work for annular-film/droplet entrainment questions, not as the next fix for the current `FFF-2` instability.

### Decision Rules
- If Phase 0/R1-R4 identify a boundary-condition, pressure-reference, initialization, or local mesh-quality cause, fix that first and keep the current model stack for the next controlled comparison.
- If the parent case remains unstable after controlled boundary and mesh checks, consider one Mubarok-style model/numerics sensitivity before continuing split-inlet interpretation.
- If the stable reference still produces report-critical carryover uncertainty, run DPM after convergence before upgrading to more complex multiphase models.
- If report time is limited, present EWF/DPM three-field modelling as a justified future-work pathway rather than implementing it.

## Phase 2 | Purposeful Inlet-Regime Comparison

### Run R5 | Baseline-Like Reference With Frozen Outlets
- Primary question: what is the stable reference case for comparison?
- Change from accepted control: use the simplest stable inlet representation and frozen outlet settings.
- Validation target: compare against the best available analytical/real-world/literature target table before accepting the case.
- Success signal: repeatable pressure drop, phase distribution, and mass balance trend, with key metrics inside target range or with a documented reason for mismatch.
- Failure signal: no stable reference after outlet and initialization controls, or stable output that is clearly outside defensible target ranges.
- Next branch:
  - If success: compare split-inlet against this reference.
  - If failure: return to baseline assumptions, solver numerics, mesh diagnostics, or boundary-condition definitions before further design claims.

### Run R6 | Two-Zone Split-Inlet A/B Case
- Primary question: does wall-side liquid and inner-side steam improve separator-relevant flow behavior in the spiral-inlet geometry compared with the stable reference?
- Change from R5: inlet face split only; keep mesh family, solver settings, outlets, and initialization strategy as close as possible.
- Validation target: the split-inlet result should not only beat the internal reference; it must remain within the accepted pressure-drop/carryover/efficiency target logic from R5.
- Required comparison metrics:
  - pressure drop,
  - steam outlet liquid carryover proxy,
  - brine outlet liquid removal,
  - liquid volume fraction distribution,
  - swirl/vortex structure,
  - convergence stability.
- Success signal: split-inlet gives physically interpretable changes without introducing new mass-balance or outlet artifacts.
- Failure signal: phase allocation creates artificial jetting, blockage, outlet carryover, or target mismatch that cannot be separated from setup artifacts.

### Run R6b | DPM Carryover Sanity Check
- Primary question: does a droplet-tracking carryover estimate agree with the mixture-field carryover trend?
- Gate: only run after R5 or R6 has a stable continuous/mixture field.
- Change from selected stable case: add post-convergence DPM droplet injections using the Purnanto-style carryover workflow.
- Required outputs:
  - escaped particle fraction,
  - trapped particle fraction,
  - incomplete particle fraction,
  - droplet-size assumptions,
  - inferred outlet steam quality/carryover.
- Success signal: DPM escaped/trapped trend supports the mixture-field interpretation and does not have excessive incomplete tracks.
- Failure signal: many incomplete particles, strong sensitivity to droplet size, or DPM trend contradicts mixture carryover; treat carryover claim as uncertain.

## Phase 3 | Evidence-Building Runs

### Run R7 | Repeatability Check
- Primary question: is the selected case repeatable?
- Change from selected case: rerun with same setup and initialization.
- Success signal: same qualitative flow structure and similar outlet/pressure metrics.
- Failure signal: solution depends strongly on initialization noise or solver history.

### Run R8 | Mesh/Quality Sensitivity
- Primary question: are conclusions stable enough for report use?
- Change from selected case: local mesh repair or refinement in inlet, swirl, steam-outlet, and brine-outlet regions only.
- Validation target: follow the Mubarok-style structure by comparing output changes for pressure drop, carryover/efficiency proxy, mass imbalance, and phase distribution across mesh levels.
- Success signal: pressure drop, outlet trends, and phase distribution do not reverse.
- Failure signal: conclusion changes with mesh quality, so report claim must be downgraded.

### Run R9 | Optional Physics Sensitivity
- Primary question: does `Eulerian` materially change the conclusion after the `Mixture` case is stable?
- Change from selected stable case: multiphase model only.
- Gate: do this only after a stable `Mixture` case exists.
- Success signal: model comparison supports or bounds the `Mixture` conclusion.
- Failure signal: cost is too high or solution becomes unstable; keep `Eulerian` as future work.

## Downtime Work While Runs Are Solving
- Update `wiki/progress/experiments.md` immediately after each run finishes.
- Prepare post-processing screenshots and a one-page result table while Fluent is unavailable.
- Keep a run decision table with `run id`, `question`, `change`, `outcome`, and `next branch`.
- Build and update the validation target table with partner analytical data or literature/design estimates.
- Clean report figures only after the run has passed its decision gate.
- Coordinate with partner only at gate points: stable reference case, accepted split-inlet comparison, and final sensitivity evidence.

## Current Priority
Do Phase 0 on `FFF-2` first. In parallel, obtain validation target values from partner/analytical work. Then run R1 parent convergence control before revisiting water-pool initialization, steam-outlet geometry, or inlet-regime comparisons.
