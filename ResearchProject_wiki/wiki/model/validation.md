# Validation

## Cross-Wiki Reusable Method Anchor
- `Reported`: the reusable CFD-side verification and validation scaffold now lives in [separator-cfd-verification-and-validation-workflow](../../../CFD_wiki/wiki/synthesis/separator-cfd-verification-and-validation-workflow.md).
- `Inferred`: use that page as the default method authority for:
  - setup verification;
  - mesh/numerics verification;
  - solution-acceptance gates;
  - external validation hierarchy;
  - uncertainty-retirement sequencing.
- `Inferred`: keep this project page focused on which validation anchor is active for the current separator branch, not on duplicating the full reusable workflow.
- `Inferred`: detailed project-owned verification reports, validation reports, target records, and sign-off now live under `../vnv/`.

## Project V&V Record Layer
- Index:
  - `../vnv/index.md`
- Policy:
  - `../vnv/policy.md`
- Claim classes:
  - `../vnv/claim-classes.md`
- Final sign-off:
  - `../vnv/signoff-log.md`

## Current Validation State
- Not ready for final validation; baseline convergence and a stable comparison case are not yet achieved.
- `Inferred`: the project still needs validation anchors before long design-comparison runs can be interpreted confidently.
- `Inferred`: current simulation data are not sufficient for validation because only `FFF-2` and `MWH-WP-2026-05-07-A` exceed `1000` iterations, and both remain diagnostic/non-converged rather than physically balanced.
- `Inferred`: the first validation blocker is the parent `FFF-2` convergence and liquid mass-balance issue, not the initialized-water-pool artifact, because `FFF-2` fails before water is patched into the lower vessel.

## Pre-Validation Requirements
1. Stable converged baseline solution.
2. Repeatability across at least two reruns with same settings.
3. Documented sensitivity on key uncertain assumptions.
4. External or analytical target ranges for pressure drop, outlet steam quality/liquid carryover, and expected separation behavior.

## Initial Validation Targets
- Compare modeled separator behavior trend against published expectations from literature.
- Compare outlet quality behavior patterns against reference correlations where applicable.
- Compare spiral-inlet CFD pressure drop against Lazalde-Crabtree-style analytical pressure-drop estimates only where the required geometry/flow inputs are transferable.
- Convert steam-outlet liquid carryover into an implied separator efficiency and compare against reported geothermal separator design ranges.

## Validation Anchor Hierarchy
Use the strongest available comparison first. If a higher-confidence source is unavailable, explicitly downgrade the claim.

1. `Reported` plant/test data for the same or similar separator.
   - Best use: pressure drop, outlet steam quality, brine outlet flow, inlet mass flow, operating pressure, and separator efficiency.
   - Claim strength if matched: strongest project evidence.
2. `Reported` analytical or design-correlation estimate.
   - Best use: expected separation efficiency range, allowable velocity/swirl behavior, pressure-drop order of magnitude, and outlet quality expectation.
   - Claim strength if matched: acceptable engineering sanity check, but not full validation.
3. `Reported` CFD/literature benchmark trend.
   - Best use: qualitative flow structure, vortex behavior, phase segregation, mesh/numerics plausibility.
   - Claim strength if matched: supports model direction, not absolute accuracy.
4. Internal A/B comparison only.
   - Best use: isolate whether a design change improves or worsens a metric under the same modelling assumptions.
   - Claim strength if matched: useful for sensitivity, not proof of real-world correctness.

## Minimum Gate Before Long Runs
Before launching a multi-hour production run, define:
- the external/analytical quantity it will be compared against,
- the acceptable error band or qualitative expectation,
- the metric to extract from Fluent,
- the decision if the result misses the target.
- the minimum iteration/monitor-stability evidence needed before the run can enter the report-facing result set.

## Simulation Evidence Use Rules
- `Usable for validation/design comparison`: sufficiently iterated, physically balanced, monitor-stable, and checked against external or analytical targets.
- `Usable for diagnostics`: sufficiently developed to show failure modes or qualitative flow behavior, but not converged or not mass-balanced.
- `Setup/debug history only`: low-iteration or incomplete runs that can explain setup evolution but cannot support performance claims.
- Current classification:
  - `FFF-2`: `Usable for diagnostics`.
  - `MWH-WP-2026-05-07-A`: `Usable for diagnostics`.
  - Earlier lower-iteration runs: `Setup/debug history only`.

## Current Sanity-Check Anchors
- `Reported`: spiral-inlet BOC separators sit within the wider vertical BOC evidence base, where properly designed separators commonly target around `99.5-99.99%` efficiency; use this as a high-level carryover sanity band, not proof of model validity.
- `Reported`: effective inlet velocity for BOC design is commonly around `30-40 m/s`, with breakdown warning near `42 m/s`; apply this to the spiral-inlet case as a sanity check only where the inlet definition is comparable.
- `Reported`: Purnanto 2013 compared CFD outlet steam quality against Lazalde-Crabtree empirical estimates and Webre separator trend data; for this project, use the spiral-inlet result as the closest separator-specific validation pattern and other geometries only as context.
- `Reported`: Mubarok 2020 validated geothermal CFD by comparing pressure drop, enthalpy, and mass flow against field data and reporting relative errors; use that as the reporting template if partner/field data become available.
- `Reported`: Pointon et al. 2009 provides a geothermal HP separator CFD anchor at `11.7 barA`, `1875 t/h`, `3.3 m` vessel diameter, and about `19-20 kPa` pressure drop, with scrolled entry slightly outperforming tangential entry (`99.96%` vs `99.93%`) and closely matching a Lazalde-Crabtree-based design prediction (`99.955%`). Use this as geothermal-specific trend support for the current spiral/scrolled-inlet preference and as an order-of-magnitude check for pressure drop and outlet dryness, not as a full one-to-one validation target because the exact geometry and Fluent controls are incomplete.
- `Reported`: Chen et al. 2025 is not geothermal, but it is currently the strongest experiment-backed separator CFD method anchor in the repo. Their transient Fluent `RSM + DPM` model matched dry-case inlet pressure within `0.01-2.13%` and wet-case separation efficiency within `4.1%`, with reported droplet PSD and grid-independence evidence. Use this as support for one later `RSM-DPM` sensitivity case if the cheaper geothermal baseline remains ambiguous after convergence and phase-flux checks; do not use Chen's air-water operating values as direct geothermal targets.

## Useful Calculation Checks
- Separator efficiency from steam-line brine carryover:
  - `eta_s = m_s / (m_s + m_b) * 100`
  - `eta_s = (m_w - m_b) / m_w * 100`
- Lazalde-Crabtree empirical efficiency structure, used only where applicable to the spiral-inlet case:
  - `eta_eff = eta_m * eta_A`
- Pressure drop:
  - `Delta P = (NH * u^2 * rho_v) / 2`
  - `NH = 16 * Ao / De^2`
  - `u = QVS / Ao`
- Phase split from enthalpy:
  - `x = (h - h_f) / h_fg`
  - `m_g = x * m`
  - `m_f = (1 - x) * m`

## DPM Carryover Validation Option
- Use only after a stable continuous/mixture solution exists.
- Inject droplets and classify outcomes as `trapped`, `escaped`, and `incomplete`, following the separator CFD validation pattern in Purnanto 2013.
- Treat DPM as a carryover sanity check rather than final truth if incomplete tracks are high or droplet-size assumptions dominate the result.

## Current Missing Validation Inputs
- `Missing Info`: analytical pressure-drop estimate for the active geometry and flow conditions.
- `Missing Info`: expected steam outlet quality or allowable liquid carryover range.
- `Missing Info`: brine outlet liquid flow expectation.
- `Missing Info`: separator efficiency target or design benchmark for this operating point.
- `Missing Info`: whether partner's validation/parameter-sweep comparison has already produced usable target values.

## Practical Near-Term Validation Plan
1. Fix or classify the `FFF-2` parent convergence and phase mass-balance problem.
2. Ask partner for the analytical/parameter-sweep outputs in a table with input conditions, predicted pressure drop, steam quality/carryover, brine flow, and any efficiency metric.
3. Calculate quick sanity values for the stabilized parent spiral-inlet case: inlet velocity position relative to the applicable `30-40 m/s` BOC band, implied separator efficiency from carryover if interpretable, and pressure-drop estimate if geometry terms are available.
4. Build a validation target table before the next production run.
5. Use the next Fluent run first as a sanity-check run against target ranges, not as a design-optimisation run.
6. Only compare split-inlet vs baseline after the baseline-like case is within a defensible target band or the mismatch is clearly explained.
7. If no analytical or real-world target exists for a metric, label that metric as `trend-only` in the report.

## Claim Rules
- If a run only matches internal expectations, claim: "model trend is internally consistent."
- If a run matches analytical/design-correlation ranges, claim: "model is directionally supported by engineering estimates."
- If a run matches real-world/test data, claim: "model is validated against available operating evidence."
- If a run fails target checks, do not tune multiple parameters at once to force agreement; identify which assumption is most likely responsible and run one control case.
