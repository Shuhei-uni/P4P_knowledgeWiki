# Synthesis: Fluent Separator Efficiency Methods

## Scope
Reusable methods for estimating geothermal steam-water separator efficiency in ANSYS Fluent, starting from the Purnanto 2013 baseline and extending to more defensible post-processing and validation workflows.

## Sources Covered
- [purnanto-2013-cfd-geothermal-separator](../sources/purnanto-2013-cfd-geothermal-separator.md)
- [chen-2025-straight-through-cyclone-water-separator](../sources/chen-2025-straight-through-cyclone-water-separator.md)
- [geothermal-boc-separator-fluent-2013-baseline](../setups/geothermal-boc-separator-fluent-2013-baseline.md)
- [multiphase-dpm-particle-tracking](../entities/multiphase-dpm-particle-tracking.md)
- [zarrouk-purnanto-2014-geothermal-separator-design-overview](../sources/zarrouk-purnanto-2014-geothermal-separator-design-overview.md)
- [rivas-cruz-2015-geothermal-separator-state-of-art-review](../sources/rivas-cruz-2015-geothermal-separator-state-of-art-review.md)
- [mondal-sharma-2024-air-water-annular-flow-cfd](../sources/mondal-sharma-2024-air-water-annular-flow-cfd.md)
- [skoog-2020-annular-flow-three-field-cfd-thesis](../sources/skoog-2020-annular-flow-three-field-cfd-thesis.md)
- External web evidence:
  - [Zarrouk and Purnanto 2015 design overview](https://doi.org/10.1016/j.geothermics.2014.05.009)
  - [Mondal and Sharma 2024 annular-flow DPM+EWF](https://doi.org/10.1016/j.net.2024.05.022)
  - [Sihombing et al. 2018 separator-method efficiency](https://pangea.stanford.edu/ERE/pdf/IGAstandard/SGW/2018/Sihombing.pdf)
  - [Mills and Lovelock 2020 steam purity modelling](https://www.worldgeothermal.org/pdf/IGAstandard/NZGW/2020/103.pdf)
  - [Utikar et al. 2010 cyclone CFD review](https://www.intechopen.com/chapters/6738)
  - [Ramirez Valverde et al. 2010 Fluent particle-wall boundary study](https://doi.org/10.4028/www.scientific.net/MSF.660-661.158)
  - [Ansys Fluent DPM boundary conditions](https://ansyshelp.ansys.com/public/Views/Secured/corp/v251/en/flu_ug/flu_ug_sec_discrete_bc.html)
  - [Ansys Fluent DPM postprocessing](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_ug/flu_ug_sec_discrete_post.html)
  - [Ansys Fluent Eulerian Wall Film boundary/source conditions](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_ug/flu_ug_ewf_sec_bound.html)

## Chen 2025 Experiment-Backed RSM-DPM Anchor
Chen 2025 gives a stronger validation pattern than the geothermal separator papers currently in this wiki, even though the application is aircraft water separation rather than geothermal steam-brine separation.

What is directly reusable:
- `Reported`: transient pressure-based Fluent with RSM turbulence and DPM droplets, plus KHRT breakup, stochastic coalescence, and rough-wall interaction ([chen-2025], p.8-10).
- `Reported`: a concrete inlet droplet distribution for DPM: Rosin-Rammler, distribution index `4.5`, main diameter `15 um`, min `6 um`, max `25 um` ([chen-2025], p.10).
- `Reported`: a three-mesh check with selected production mesh `4,000,181` cells and residual target `1e-4` ([chen-2025], p.10-11).
- `Reported`: validation against experiment with dry-case inlet-pressure error `0.01-2.13%` and representative wet-case efficiency deviation `4.1%` ([chen-2025], p.14-15).

What is only analogy-level support:
- `Reported`: higher operating pressure reduced pressure loss and improved separator efficiency in their air-water device ([chen-2025], p.15-18).
- `Reported`: stronger swirl was not uniformly better across the whole flow range; efficiency followed a `rise-fall-rise` trend because centrifugal separation, turbulence, and re-entrainment competed ([chen-2025], p.11-13, p.17-18).

Project transfer rule:
- `Inferred`: use Chen 2025 as the benchmark for whether an RSM-DPM upgrade is worth the cost after a cheaper geothermal baseline is stable.
- `Inferred`: do not import Chen's operating values directly into geothermal CFD; import the validation discipline, droplet-distribution structure, and swirl-tradeoff warning instead.

## Purnanto 2013 Efficiency Workflow
1. `Reported`: solve the continuous separator flow first. Purnanto used Fluent, pressure-based RANS with RNG k-epsilon, incompressible/isothermal assumptions, no flashing, mass-flow inlet, pressure outlet, and Hybrid Initialization ([purnanto-2013], p.5-6).
2. `Reported`: after the continuous solution converged, inject liquid droplets and track them with Fluent DPM. The paper states that particle tracking is required to predict separator efficiency and that DPM integrates particle force balance in a Lagrangian frame ([purnanto-2013], p.3-4).
3. `Reported`: estimate droplet sizes with the Harwell method because upstream separator-inlet droplet-size distribution was considered almost impossible to predict or measure in that study. Purnanto reports a `10 um` average droplet setup and gives the Harwell relation `x_med = 1.42 x_sa` ([purnanto-2013], p.3-5).
4. `Inferred`: for a reproduction, treat the `10 um` value as the baseline Sauter mean unless better local inlet data exists. This gives `x_med = 14.2 um`, a lower marker near `4.26 um`, and an upper marker near `41.18 um`; these are not directly listed as Purnanto's nine actual DPM diameters.
5. `Reported`: inject a large number of particles at the inlet surface. Purnanto states that particle sizes were calculated using Harwell, uniformly distributed at the inlet surface, and injected nine times with a different droplet diameter each time ([purnanto-2013], p.8).
6. `Reported`: use the same number of injected particles for each injection cycle, but assign different represented mass flows to those cycles. This means a simple particle count is not enough if the size bins represent different liquid mass ([purnanto-2013], p.8).
7. `Reported`: classify each DPM track as `trapped`, `escaped`, or `incomplete`. In Purnanto's separator interpretation, trapped droplets are separated, escaped droplets are carried to the steam outlet, and incomplete droplets exceeded the tracking step limit ([purnanto-2013], p.8).
8. `Reported`: set maximum Euler tracking steps to `1e5`; Purnanto tested `1e6`, but incomplete tracks did not reduce significantly. The paper states that further mesh refinement was likely needed to distinguish physical from numerical behavior ([purnanto-2013], p.8).
9. `Reported`: Purnanto assumed incomplete droplets were all separated to cope with the ambiguity. The paper explicitly says this is not rigorous, but it gave collection-efficiency estimates close to the empirical Lazalde-Crabtree method ([purnanto-2013], p.8).

## Purnanto Calculation Form
`Reported but ambiguous`: Purnanto says separation efficiency is obtained by the ratio of fine droplets escaped from the steam outlet to total liquid droplets at the inlet ([purnanto-2013], p.3). That literal ratio is a carryover fraction, not a collection efficiency. Use the interpretation below to avoid reversing the result.

### Count-Based Carryover
Use this only as a diagnostic:

`f_escape,count = N_escaped / N_injected`

`eta_count = 1 - f_escape,count`

### Mass-Weighted DPM Efficiency
Use this as the minimum defensible Purnanto-style Fluent calculation:

`m_liq,escaped = sum_i m_liq,i * (N_escaped,i / N_injected,i)`

`m_liq,trapped = sum_i m_liq,i * (N_trapped,i / N_injected,i)`

`eta_DPM = m_liq,trapped / m_liq,in = 1 - (m_liq,escaped / m_liq,in)`

where `i` is each droplet-size injection bin and `m_liq,i` is the real liquid mass represented by that bin.

### Incomplete-Track Brackets
Do not report one efficiency value if `N_incomplete` is large. Report brackets:

`optimistic eta`: treat incomplete as trapped. This matches Purnanto's assumption.

`pessimistic eta`: treat incomplete as escaped.

`clean eta`: exclude incomplete only if the incomplete fraction is small and separately reported.

## Fluent Post-Processing Checklist
1. Define DPM boundary fates intentionally: steam outlet = `escape`, brine exit or liquid collection region = `trap` or an equivalent collection criterion, separator walls = case-dependent `reflect`, `trap`, wall-film, or UDF logic.
2. Run particle tracking after a stable continuous field; for two-way coupling, verify that DPM source updates do not disturb mass and momentum convergence.
3. For each diameter bin, export or record `trapped`, `escaped`, and `incomplete` counts plus the represented injection mass flow.
4. Compute mass-weighted efficiency by bin, not only total particle count.
5. Record `N_incomplete/N_injected`; if it is not small, run mesh, tracking-step, and time-step/trajectory sensitivity before trusting efficiency.
6. Independently report continuous-phase mass balance at every inlet and outlet.

## More Accurate or More Defensible Methods

### Method A: Mass-Weighted DPM Grade Efficiency
- `Best use`: droplet or particle carryover where droplets are dilute enough for Eulerian-Lagrangian tracking.
- `Efficiency`: calculate grade efficiency by diameter bin, then integrate over the inlet droplet-size distribution.
- `Why better than Purnanto count ratio`: handles different mass represented by each droplet diameter and exposes whether small droplets dominate carryover.
- `Main risk`: wall interaction and incomplete-track treatment can dominate the answer; cyclone CFD literature defines collection efficiency by separated fraction and commonly treats efficiency by particle-size interval, while Fluent cyclone work also warns that simple wall boundary conditions can limit collection-efficiency prediction.

### Method B: Eulerian Phase-Flux Efficiency
- `Best use`: separator CFD where liquid and steam are solved as phases and the main question is bulk brine carryover through the steam outlet.
- `Efficiency`: `eta_phase = 1 - (m_liq,steam_out / m_liq,in)`.
- `Outlet dryness`: `x_out = m_vapor,steam_out / (m_vapor,steam_out + m_liq,steam_out)`.
- `Why better than DPM alone`: directly uses outlet phase mass fluxes and gives a mass-balance closure check.
- `Main risk`: mixture/Eulerian methods may smear droplets, films, and interface separation, so they can miss size-dependent droplet carryover.

### Method C: Transient VOF or Eulerian Multiphase With Interface Resolution
- `Best use`: water pool, brine outlet, large liquid slugging, visible interface instability, or transient carryover.
- `Efficiency`: surface-integrate phase mass fluxes at steam and brine outlets after transient averaging.
- `Why better`: resolves bulk liquid interfaces and unsteady carryover mechanisms better than steady DPM.
- `Main risk`: high mesh/time cost and still not enough for sub-grid mist droplets unless paired with DPM or a droplet closure.

### Method D: DPM + Eulerian Wall Film Three-Field Model
- `Best use`: cases where wall film deposition and re-entrainment may control carryover.
- `Efficiency`: combine outlet droplet flow, outlet wall-film flow, deposition rate, entrainment rate, and phase-flux balance.
- `Why better`: recent Fluent annular-flow work uses DPM for gas-core droplets and Eulerian Wall Film for wall liquid, with entrainment/deposition UDFs and experimental entrainment-fraction comparison ([mondal-2024], p.2881-2890).
- `Main risk`: not a plug-in geothermal separator method. It needs transient setup, entrainment/deposition closure choice, and calibration.

### Method E: Field Chemistry or Tracer Validation
- `Best use`: validating any Fluent-predicted separator efficiency.
- `Efficiency`: use chloride, sodium, or injected tracer carryover in steam and brine samples. Sihombing et al. describe geothermal separator efficiency from brine carryover chemistry and state that chloride/sodium signatures are used to measure carryover and efficiency.
- `Why better`: measures actual brine carryover, including effects CFD may miss.
- `Main risk`: sampling and stabilization errors; Mills and Lovelock note that steam purity models depend on separator efficiency, CDP/scrubber efficiencies, chloride/sodium tracer reliability, and drain-pot sampling design.

## Recommended Workflow for This Project
1. `Minimum`: report `eta_phase`, outlet dryness, and total mass imbalance from Fluent phase fluxes.
2. `Add Purnanto comparison`: run DPM droplets at `3-5 um`, `10 um`, `14.2 um`, and `40-41 um`, plus any measured/project-specific PSD if obtained.
3. `Report brackets`: for each DPM run, publish escaped/trapped/incomplete counts and optimistic/pessimistic efficiency bounds.
4. `Improve accuracy`: switch from count-based to mass-weighted DPM grade efficiency across droplet-size bins.
5. `If wall film matters`: test transient DPM + Eulerian Wall Film or VOF/Eulerian multiphase with outlet phase-flux averaging.
6. `Validate`: compare CFD carryover with chloride/sodium/tracer-based separator efficiency or drain-pot chemistry where field data exists.

## Detailed Recommended Report

### Objective
The recommended efficiency workflow should answer three different questions instead of compressing everything into one number:

1. `Whole-separator liquid removal`: how much inlet liquid leaves through the brine route instead of the steam outlet?
2. `Droplet-size carryover`: which droplet sizes escape through the steam outlet?
3. `Re-entrainment risk`: does liquid that first deposits on the wall become a film and later re-enter the steam core?

This separation matters because a separator can have good bulk liquid removal while still allowing fine mist or re-entrained film droplets into the steam outlet.

### Tier 1: Phase-Flux Efficiency Baseline
Purpose: produce the most stable separator-wide efficiency number from Fluent mass-flow reports.

Run state:
- Use the selected multiphase representation for the separator body.
- Use the same geometry, inlet mass flow, pressure outlet, and water/brine outlet settings as the target case.
- Run until residuals and physical monitors are stable.

Post-processing:
- Use `Reports > Fluxes... > Mass Flow Rate`.
- Compute phase-resolved mass flow through:
  - inlet,
  - steam outlet,
  - brine outlet,
  - any drain or auxiliary outlet.
- Record total mass imbalance.

Equations:

`eta_phase = 1 - (m_liq,steam_out / m_liq,in)`

`x_steam_out = m_vapor,steam_out / (m_vapor,steam_out + m_liq,steam_out)`

`mass_imbalance = abs(m_in - m_out) / m_in`

Acceptance target:
- `mass_imbalance` should be small enough that the missing mass is much smaller than the carryover being reported.
- If `m_liq,steam_out` changes strongly with mesh or outlet backflow treatment, do not treat `eta_phase` as final.

### Tier 2: DPM Droplet-Size Sweep
Purpose: quantify mist carryover by droplet size and make the Purnanto comparison explicit.

Time-limited baseline:

If there is only time for three particle injections, run `5 um`, `10 um`, and `40-41 um` first. This covers a fine mist lower marker, the Purnanto-style baseline, and a larger droplet check. Add `14.2 um` later when building the fuller Harwell-inferred sweep or a mass-weighted grade-efficiency curve.

Recommended first sweep:

| Diameter | Reason |
|---:|---|
| `3-5 um` | Fine droplet lower envelope from the Harwell-inferred range; likely hardest to separate. |
| `10 um` | Purnanto reported baseline average droplet size. |
| `14.2 um` | Harwell-inferred median if `10 um` is treated as Sauter mean diameter. |
| `40-41 um` | Harwell-inferred upper marker; useful for checking whether larger droplets separate cleanly. |

Optional expanded sweep:
- Use logarithmic spacing, for example `2, 3, 5, 10, 15, 20, 30, 40, 60 um`.
- Use the expanded sweep only after the first four-point sweep shows that efficiency changes materially with diameter.

Fluent setup:
- Use DPM particle tracking after the continuous field is converged, matching Purnanto's workflow.
- Steam outlet DPM boundary: `escape`.
- Brine collection boundary or bottom collection region: `trap` or equivalent captured criterion.
- Separator walls: start with the physically intended wall behavior; do not silently use `trap` everywhere unless the case assumes every wall impact is permanent collection.
- Record DPM fate categories: `escaped`, `trapped`, `incomplete`.

Mass-weighting:
- If each droplet-size injection represents the same real liquid mass, average by represented mass.
- If each injection uses the same particle count but different represented mass, follow Purnanto's statement and compute with each bin's represented mass flow.
- Do not report simple particle-count efficiency as the main efficiency unless all injections represent equal real mass and equal physical probability.

Equations:

`f_escape,i = N_escaped,i / N_injected,i`

`eta_i = 1 - f_escape,i`

`eta_mass_weighted = 1 - [sum_i(m_liq,i * f_escape,i) / sum_i(m_liq,i)]`

Incomplete-track brackets:

`eta_optimistic,i = 1 - [N_escaped,i / N_injected,i]`

`eta_pessimistic,i = 1 - [(N_escaped,i + N_incomplete,i) / N_injected,i]`

Acceptance target:
- The optimistic and pessimistic DPM efficiencies should be close enough that the conclusion does not depend on incomplete tracks.
- If they are far apart, fix tracking/mesh first instead of picking Purnanto's optimistic assumption.

### Tier 3: Coupled Wall-Film Re-Entrainment Test
Purpose: test whether wall deposition is really permanent separation or whether wall liquid can re-enter the steam path.

When to run:
- DPM tracks hit separator walls heavily before escaping.
- Liquid film, splash, roll-wave, or re-entrainment is physically plausible.
- Bulk phase-flux efficiency looks good but DPM or field chemistry suggests carryover.
- Geometry changes alter wall impingement more than phase-flux separation.

Model direction:
- Use transient calculation.
- Enable DPM for gas-core droplets.
- Enable Eulerian Wall Film on relevant walls.
- Use DPM-wall-film coupling so droplets can deposit into a wall film instead of being counted as permanently trapped.
- Track film mass, film thickness, deposition rate, and entrainment/release behavior.

Post-processing:
- Report film mass inventory over time.
- Report liquid leaving the steam outlet as:
  - resolved liquid phase flux,
  - escaped DPM droplet mass,
  - any wall-film contribution crossing into outlet or re-injected into the gas core.
- Time-average after the film inventory reaches a quasi-steady range.

Equations:

`m_liq,steam_total = m_liq,phase_flux + m_DPM,escaped + m_film_or_reentrained_out`

`eta_film_aware = 1 - (m_liq,steam_total / m_liq,in)`

Acceptance target:
- Film mass inventory should not drift indefinitely during the averaging window.
- Deposition and entrainment/release rates should be physically interpretable.
- If the wall-film model changes efficiency materially, the simpler DPM trap-wall result should be treated as optimistic.

### Tier 4: Field or Experiment Validation
Purpose: check whether the Fluent efficiency predicts actual brine carryover.

Validation options:
- Chloride or sodium carryover in steam condensate/drain-pot samples.
- Tracer carryover test if field sampling is available.
- Steam quality/purity measurements downstream of separator or demister.

Validation equation form:

`m_brine_carryover = tracer_mass_flow_in_steam / tracer_concentration_in_brine`

`eta_field = 1 - (m_brine_carryover / m_brine_in)`

Use field validation as the deciding evidence if CFD and chemistry disagree, then inspect whether CFD is missing wall-film re-entrainment, droplet breakup, upstream atomisation, or outlet sampling effects.

## Recommended Run Matrix

| Run ID | Purpose | Model | Output to trust |
|---|---|---|---|
| `E0` | Baseline mass balance | Existing multiphase setup | `eta_phase`, `x_steam_out`, mass imbalance |
| `D1-3um` | Fine mist lower bound | DPM after converged flow | escaped/trapped/incomplete, `eta_i` |
| `D2-10um` | Purnanto baseline | DPM after converged flow | escaped/trapped/incomplete, `eta_i` |
| `D3-14um` | Harwell inferred median | DPM after converged flow | escaped/trapped/incomplete, `eta_i` |
| `D4-41um` | Larger droplet check | DPM after converged flow | escaped/trapped/incomplete, `eta_i` |
| `D5-combined` | Mass-weighted PSD result | DPM bins integrated by represented mass | `eta_mass_weighted` |
| `F1` | Wall-film test | transient DPM + Eulerian Wall Film | `eta_film_aware`, film inventory, re-entrainment rate |
| `V1` | External validation | chemistry/tracer/field data | `eta_field` |

## Results Table Template

| Run | Diameter/bin | `m_liq,in` | `m_liq,steam_out` | Escaped | Trapped | Incomplete | `eta_low` | `eta_high` | Notes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `E0` | phase flux |  |  | n/a | n/a | n/a |  |  | mass-balance baseline |
| `D1` | `3-5 um` |  |  |  |  |  |  |  | fine mist |
| `D2` | `10 um` |  |  |  |  |  |  |  | Purnanto baseline |
| `D3` | `14.2 um` |  |  |  |  |  |  |  | inferred median |
| `D4` | `40-41 um` |  |  |  |  |  |  |  | inferred upper marker |
| `F1` | film-aware |  |  |  |  |  |  |  | transient averaged |

## Decision Rules
- If `eta_phase` is poor, fix bulk separation geometry or boundary conditions before optimizing droplet tracking.
- If `eta_phase` is high but small DPM droplets escape, report that the separator removes bulk liquid but not fine mist.
- If DPM incomplete tracks dominate, the run is not efficiency-ready.
- If wall-film re-entrainment increases outlet liquid, use the film-aware efficiency for the report and treat simple trapped-wall DPM as optimistic.
- If chemistry/tracer validation exists, calibrate the CFD method to that evidence before comparing design variants.

## Failure Signals
- `N_incomplete/N_injected` is large enough that optimistic and pessimistic DPM efficiencies differ materially.
- `eta_DPM` and `eta_phase` disagree by more than the expected uncertainty.
- Outlet liquid mass is mesh-dependent or changes after extending DPM tracking steps.
- Steam outlet backflow or pressure-outlet recirculation changes escaped particle fate.
- Wall boundary choices change efficiency more than geometry changes.

## Reuse Recommendation
Use Purnanto's method only as a baseline comparison, not as the final efficiency method. The current best-practice hierarchy is:

1. Mass-balance checked phase-flux efficiency for the whole separator.
2. Mass-weighted DPM grade efficiency for droplet-size carryover.
3. Transient film/droplet modelling when re-entrainment is a suspected mechanism.
4. Chloride/sodium/tracer validation whenever field or experiment data is available.

## Quick Guidance Link
- For click-by-click Fluent setup of the time-limited DPM baseline, use [fluent-general-click-by-click](../guidance/fluent-general-click-by-click.md), section `11) Baseline DPM Particle-Tracking Setup`.

## Related Physics Basis
- [separator-flow-physics](../physics-basis/separator-flow-physics.md)
- [droplets-carryover-and-re-entrainment](../physics-basis/droplets-carryover-and-re-entrainment.md)
- [governing-equations-and-modeling-levels](../physics-basis/governing-equations-and-modeling-levels.md)
- [uncertainties-and-assumption-register](../physics-basis/uncertainties-and-assumption-register.md)
