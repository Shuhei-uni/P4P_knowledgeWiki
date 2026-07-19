# Synthesis: Separator CFD Verification and Validation Workflow

## Scope
Reusable verification and validation (`V&V`) workflow for separator CFD in this repo, with emphasis on Fluent geothermal separator work that may later use mixture, DPM, or film-aware extensions.

This page separates:
- `Verification`: show that the CFD setup is numerically and procedurally trustworthy for the stated equations and assumptions.
- `Validation`: show that the CFD outputs agree with external evidence strongly enough for the intended claim.

## Sources Covered
- [purnanto-2013-cfd-geothermal-separator](../sources/purnanto-2013-cfd-geothermal-separator.md)
- [pointon-2009-geothermal-separator-sizing-cfd-validation](../sources/pointon-2009-geothermal-separator-sizing-cfd-validation.md)
- [mubarok-2020-cfd-geothermal-flow-meters](../sources/mubarok-2020-cfd-geothermal-flow-meters.md)
- [chen-2025-straight-through-cyclone-water-separator](../sources/chen-2025-straight-through-cyclone-water-separator.md)
- [mondal-sharma-2024-air-water-annular-flow-cfd](../sources/mondal-sharma-2024-air-water-annular-flow-cfd.md)
- [mesh-quality-and-resolution-patterns](mesh-quality-and-resolution-patterns.md)
- [fluent-separator-efficiency-methods](fluent-separator-efficiency-methods.md)
- [uncertainties-and-assumption-register](../physics-basis/uncertainties-and-assumption-register.md)

## Cross-Paper Pattern
- `Reported`: geothermal separator papers alone do not provide a complete modern validation package; Purnanto explicitly says further experimental calibration/validation is needed ([purnanto-2013], p.7, p.9).
- `Reported`: Pointon 2009 is the strongest geothermal separator validation anchor in the current local source set because it compares CFD separator efficiency against a design-method prediction and uses CFD to compare scrolled versus tangential entry behavior ([pointon-2009], p.946-948).
- `Reported`: Mubarok 2020 is the strongest geothermal numerical-verification exemplar because it uses six meshes with Richardson extrapolation and reports key-output errors mostly within `+-5%` against field data ([mubarok-2020], p.7-9, p.14).
- `Reported`: Chen 2025 is the strongest experiment-backed separator-method exemplar in the repo because it combines grid independence, residual target, dry-case pressure comparison, and wet-case efficiency comparison in one workflow ([chen-2025], p.10-15).
- `Reported`: Mondal 2024 shows that for film-droplet problems, validation may need comparison against experimental or correlation envelopes rather than one exact separator-efficiency number; many entrainment-fraction predictions were within about `+-30%` of reference data ([mondal-2024], p.2886-2890).

## What To Verify Before Claiming Anything

### Level V0: Problem Definition
Before solving, declare:
1. the quantity of interest;
2. the comparison target;
3. the acceptable error band or qualitative trend rule;
4. the evidence needed before the result is allowed into a report.

`Inferred`: if these are undefined before the run, the run is still exploration, not validation.

Minimum examples:
- pressure drop `Delta P`
- steam-outlet liquid carryover
- outlet dryness / steam quality
- DPM escaped/trapped/incomplete fractions
- geometry-ranking trend

### Level V1: Setup Verification
Check the case definition before long runs:
1. geometry variant and boundary-zone names are correct;
2. units and operating pressure convention are correct;
3. inlet total mass flow, phase split, pressure, and enthalpy package match the intended case;
4. gravity direction and reference frame are correct;
5. the same setup rerun gives materially the same early-monitor behavior.

Why this matters:
- `Reported`: Purnanto's interpretation depends on a two-stage workflow and droplet-size assumptions that are easy to misapply if the setup intent is not frozen first ([purnanto-2013], p.3-6, p.8).

### Level V2: Numerical Verification
Numerical verification should retire the main numerical failure modes before physics claims are made.

Required checks:
1. mesh-quality audit;
2. mesh-sensitivity or mesh-independence test;
3. solver/numerics sensitivity where outputs are unstable;
4. DPM tracking sensitivity if DPM is used.

Recommended minimum mesh workflow:
1. run Fluent mesh check and record cell count plus worst quality metrics;
2. build at least three meshes: coarse, medium, fine;
3. compare the outputs that matter, not only residuals;
4. accept the production mesh only when key outputs change by a small chosen tolerance.

Useful output set:
- `Delta P`
- `m_liq,steam_out`
- outlet dryness / steam quality
- mass imbalance
- DPM incomplete fraction
- selected local monitor such as core pressure or tangential velocity

Paper anchors:
- `Reported`: Mubarok used six meshes with Richardson extrapolation and chose the production mesh when extrapolated errors for key outputs were each below `1%` ([mubarok-2020], p.7-8).
- `Reported`: Chen compared `0.42M`, `4.0M`, and `7.26M` cells and accepted the `4.0M` mesh after small pressure-loss and efficiency deltas versus the finer mesh ([chen-2025], p.10-11).
- `Reported`: Mondal accepted the middle mesh when outlet entrainment fraction changed little relative to the finest mesh ([mondal-2024], p.2886-2887).
- `Reported`: Purnanto states that incomplete DPM tracks likely required further mesh refinement and that increasing maximum tracking steps alone did not resolve the ambiguity cleanly ([purnanto-2013], p.8).

### Level V3: Solution Acceptance Gate
A run is not numerically accepted just because it finished.

Minimum acceptance gate:
1. residuals flatten or drop to the chosen threshold;
2. physical monitors flatten enough for the claim being made;
3. mass imbalance is small relative to the carryover or separation signal;
4. backflow or oscillation behavior is explained if present;
5. repeated reruns do not materially change the conclusion.

Paper anchors:
- `Reported`: Chen required all scaled residuals below `1e-4` before accepting a solved state ([chen-2025], p.10).
- `Reported`: Purnanto reports plausible field trends but still concludes that experimental calibration/validation is needed, so residual-only acceptance is not enough for separator-performance claims ([purnanto-2013], p.7-9).

### Level V4: Validation Against External Evidence
Use the strongest available anchor first.

Validation hierarchy:
1. same-geometry plant, rig, or field data;
2. same-geometry analytical/design-correlation target;
3. closest geothermal literature trend anchor;
4. analogy benchmark for method discipline only.

Interpretation:
- `Reported`: Pointon is the best current geothermal separator trend anchor for scrolled-entry superiority and efficiency/dryness order of magnitude ([pointon-2009], p.946-947).
- `Reported`: Mubarok is the best geothermal field-data validation exemplar in the current local set ([mubarok-2020], p.8-9, p.14).
- `Reported`: Chen is the best separator-method validation exemplar but should transfer workflow discipline, not air-water operating values ([chen-2025], p.14-18).
- `Reported`: Mondal is best used when film-droplet entrainment and deposition are the target behavior rather than bulk geothermal separator efficiency ([mondal-2024], p.2888-2890).

Automation rule:
- `Inferred`: validation comparison can be substantially automated, but validation judgment remains human-reviewed because the script cannot decide whether the chosen external anchor is truly claim-appropriate.
- `Inferred`: if there is no predefined validation target file or equivalent declared target manifest before the run, automation must not output `Externally validated`; it may only allow `Debug only`, `Numerically verified`, or `Trend supported` depending on the evidence present.

### Level V5: Uncertainty Retirement
After a baseline is numerically accepted and externally compared, vary one major uncertainty at a time.

Priority order for this repo:
1. inlet regime representation;
2. pressure / enthalpy package;
3. droplet-size distribution and DPM step limits;
4. wall-fate interpretation or wall-film model;
5. turbulence-model choice.

`Inferred`: this follows the existing uncertainty register rule that model escalation should be driven by unresolved uncertainty, not by solver prestige.

## Robust Minimal Workflow
Use this when the project has not yet reached report-quality validation.

1. Freeze one baseline geometry and one operating point.
2. Define one comparison target before running and store it in a declared target record if automation will classify claims.
3. Run a coarse / medium / fine mesh check on the same metric set.
4. Repeat the accepted mesh once to confirm repeatability.
5. Record residuals, mass imbalance, and at least one physical monitor.
6. Compare against the strongest available external anchor.
7. If DPM is used, report `injected`, `escaped`, `trapped`, and `incomplete`.
8. If incomplete DPM tracks are high, do not collapse to one efficiency number yet.
9. Run one uncertainty sensitivity at a time.
10. Classify the final claim strength explicitly.

## Automation Boundary
For repo automation, separate:
- `Verification automation`: run setup checks, monitor extraction, mesh/sensitivity comparisons, mass-balance checks, and DPM-fate summaries.
- `Validation comparison automation`: compare outputs against a predefined target table, YAML file, or equivalent machine-readable manifest.
- `Validation judgment`: human review of whether the target itself is defensible for the claim being written.

Recommended automation output:

```text
Setup passed: yes
Mesh sensitivity passed: yes
Residual/monitor gate passed: yes
Mass balance passed: yes
External comparison available: trend only
Maximum claim class: Trend supported
Not externally validated
```

`Inferred`: the most useful automation product is a maximum allowable claim class, not a blanket pass/fail verdict.

## Claim Classes
Use these labels when writing results:

| Claim class | Meaning | Minimum evidence |
|---|---|---|
| `Debug only` | setup/mechanism check only | setup runs without external comparison |
| `Numerically verified` | numerically stable enough for internal comparison | mesh check + monitor acceptance + repeatability |
| `Trend supported` | agrees with analytical or literature trend | verified baseline + external trend/correlation comparison |
| `Externally validated` | agrees with measured or benchmark data strongly enough for report-facing validation language | verified baseline + predefined validation target record + direct field/experiment comparison + human-reviewed target appropriateness |

## Separator-Specific Output Pack
For separator work in this repo, keep the following together:
1. phase-flux mass balance;
2. `Delta P`;
3. outlet dryness / steam quality;
4. steam-outlet liquid carryover;
5. DPM escaped/trapped/incomplete counts if DPM is active;
6. the exact uncertainty or sensitivity that the run was meant to test.

Why this matters:
- `Reported`: Purnanto's separator-efficiency interpretation can be distorted by incomplete tracks ([purnanto-2013], p.8).
- `Reported`: Pointon's separator comparison is strongest when efficiency, dryness, and geometry-entry trend are all read together ([pointon-2009], p.946-947).
- `Reported`: Chen's workflow validates pressure behavior and wet efficiency together, not one metric in isolation ([chen-2025], p.14-15).

## Failure Signals
Stop calling the workflow validated if any of these remain unresolved:
1. the chosen metric changes materially with mesh;
2. mass imbalance is similar in size to the carryover signal;
3. DPM incomplete tracks dominate the result;
4. the case matches one external metric only after several parameters changed together;
5. the chosen external anchor is only analogy-level but the write-up sounds like same-system validation.

## Reuse Recommendation
- `reuses`: reuse this page as the default V&V scaffold for separator CFD in both Fluent manual work and PyAnsys automation.
- `supports`: use [mesh-quality-and-resolution-patterns](mesh-quality-and-resolution-patterns.md) for the mesh branch of the workflow.
- `supports`: use [fluent-separator-efficiency-methods](fluent-separator-efficiency-methods.md) for the DPM and efficiency-reporting branch of the workflow.
- `supports`: use [uncertainties-and-assumption-register](../physics-basis/uncertainties-and-assumption-register.md) to decide which sensitivity belongs next.
