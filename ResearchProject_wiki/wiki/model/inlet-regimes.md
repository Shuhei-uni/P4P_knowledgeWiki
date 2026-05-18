# Inlet Regimes

## Objective
Track how inlet representation evolves from simplified baseline toward realistic regime-aware modelling.

## Current Baseline
- Legacy recreation currently assumes mist-like inlet for two-phase feed (based on historical modelling approach).

## Selected Next Inlet Test
- Replace the uniform/mist-like inlet assumption with a **two-zone split inlet**.
- Project intent:
  - outer-wall side of inlet = liquid water
  - inner/core side of inlet = steam
- Preferred implementation route:
  - split the inlet face in geometry/meshing,
  - import two named inlet zones into Fluent,
  - keep the rest of the baseline solver stack unchanged for the first A/B comparison.

## Planned Progression
1. Reproduce and converge baseline model.
2. Introduce one controlled inlet modification only: the two-zone split inlet.
3. Compare internal flow structure, phase distribution, pressure drop, and outlet behavior against the original inlet representation.
4. Only if needed, move later to smoother non-uniform inlet profiles or a UDF/profile approach.

## Current Uncertainties
- The exact physical meaning of `left` and `right` must be confirmed on the actual inlet-face orientation before the two zones are named.
- Preserving the same phase mass-flow totals with a 50/50 inlet-area split may create a very strong steam-side velocity jet because of the gas/liquid density difference.

## Confirmed Geometry Context
- User clarification on 2026-04-30: the active baseline geometry for this inlet-change workflow is the **spiral inlet**, not a tangential inlet.

## Evidence Links
- Technical baseline notes: `wiki/technical/sources/purnanto-etal-2013.md`
- Project objective: `wiki/project/objective-and-scope.md`
- Reusable CFD setup: `../../../CFD_wiki/wiki/setups/geothermal-boc-separator-two-zone-split-inlet.md`
- Practical project report: `../../../Setup report/split two-phase inlet setup report.md`
