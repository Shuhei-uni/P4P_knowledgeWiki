# Physics Basis: Droplets, Carryover, and Re-Entrainment

## Scope
- Physical question: what is actually known about droplets entering geothermal separators, and what mechanisms can still send liquid into the steam outlet?
- Why this question matters for separator CFD: droplet assumptions often dominate carryover predictions more than solver settings do, yet the inlet droplet field is one of the least measured parts of the problem.

## Evidence Snapshot
| Topic | Current best statement | Evidence label | Main source |
|---|---|---|---|
| Baseline geothermal CFD droplet size | Purnanto uses a uniform `10 um` average droplet size at the inlet. | `Reported` | [purnanto-2013], p.5 |
| Harwell relation | `x_med = 1.42 x_sa` is used to infer a broader droplet envelope from the Sauter mean. | `Reported` | [purnanto-2013], p.3-4 |
| Inferred Harwell envelope | If `10 um` is `x_sa`, then a useful bracket is about `4.26 um` to `41.18 um`. | `Inferred` | [purnanto-2013], p.3-4 |
| Measured geothermal inlet PSD | No complete conventional geothermal separator-inlet PSD has been found in the maintained evidence set. | `Missing` | [geothermal-separator-inlet-droplets-and-carryover](../synthesis/geothermal-separator-inlet-droplets-and-carryover.md) |
| Wall-film mechanism | Entrainment and re-entrainment become more important as liquid loading and velocity rise. | `Reported` | [geothermal-separator-inlet-droplets-and-carryover](../synthesis/geothermal-separator-inlet-droplets-and-carryover.md) |
| Three-field modeling precedent | Wall film and gas-core droplets can be represented as separate liquid pathways. | `Reported` | [mondal-2024], p.2881-2890; [skoog-2020], p.7-12 |

## What Prior Research Reports
- `Reported`: Purnanto 2013 treats the separator inlet as mist flow with gas as the continuous phase and droplets as the dispersed phase, using a `10 um` average droplet size and Harwell-based droplet reasoning ([purnanto-2013], p.3-5).
- `Reported`: Purnanto states that predicting or measuring the real upstream droplet-size distribution is almost impossible in that study context, which is why Harwell-style assumptions are used ([purnanto-2013], p.3-4).
- `Reported`: Pointon 2009 describes droplets injected over the entrance section from an upper-limit log-normal distribution, with wall contact below the entry and at the baffle treated as adherent collection ([pointon-2009], p.946).
- `Reported`: Chen 2025 provides a more explicit DPM inlet distribution, using Rosin-Rammler droplets from `6 um` to `25 um` with a `15 um` main diameter, but in an air-water separator rather than a geothermal steam-brine system ([chen-2025], p.10).
- `Reported`: annular-flow literature represented in this wiki separates gas-core droplets from wall film and explicitly tracks entrainment and deposition, showing that wall-side liquid and free droplets can require different closures ([mondal-2024], p.2883-2890; [skoog-2020], p.7-12).

## What Prior Research Assumes
- `Assumed`: a simplified inlet droplet distribution is acceptable as a first engineering approximation when field droplet measurements do not exist.
- `Assumed`: droplets reaching certain collector or wall regions are often counted as separated, even though permanent attachment is not always experimentally verified.
- `Assumed`: wall-deposited liquid may be treated as permanently removed in simpler separator studies unless re-entrainment is the explicit research target.

## Cross-Paper Inferences
- `Inferred`: there are two different liquid-carryover questions that should not be merged:
  - can free droplets escape with the steam core?
  - can liquid that first hits the wall return to the core as re-entrained film or droplets?
- `Inferred`: Purnanto-style DPM is a credible first-pass method for droplet carryover ranking when the main uncertainty is inlet droplet size, but it is structurally optimistic if wall impact is treated as permanent collection.
- `Inferred`: Chen is useful as a discipline anchor because it reports a full droplet-distribution structure, while geothermal papers are more useful for domain relevance even when their inlet PSD is less explicit.

## Unknowns and Weak Evidence
- `Missing`: measured droplet number concentration and size distribution at a conventional geothermal separator inlet.
- `Missing`: mineral-particle or corrosion-particle size and loading at the same inlet location for most geothermal cases.
- `Missing`: robust geothermal data showing how much wall-deposited liquid later re-enters the steam core under real operating conditions.
- `Missing`: a widely reusable mapping from DPM parcel counts to real droplet mass for the Purnanto nine-injection workflow.

## Governing Physics
- Droplet transport depends on force balance between drag, inertia, gravity, pressure-gradient effects, and, where relevant, turbulence-induced dispersion.
- Separator carryover is therefore size-sensitive because smaller droplets follow the gas core more easily while larger droplets have more radial slip toward the wall.
- If a liquid wall film forms, additional mass conservation is needed for film accumulation, entrainment from film to gas core, and deposition from droplets back to film.
- Re-entrainment matters because a separator can appear efficient in a simple wall-trap interpretation while still sending film-generated droplets into the steam outlet.

## Consequence for CFD Modeling
- A first-pass CFD representation should state whether it is answering a free-droplet question, a bulk phase-carryover question, or a wall-film re-entrainment question.
- If the only known inlet droplet basis is Harwell/Purnanto-style inference, then a sensitivity sweep over plausible droplet sizes is more defensible than one fixed "true" PSD claim.
- If the separator walls are assumed to permanently collect droplets, that should be documented as a physics assumption rather than hidden inside a DPM boundary choice.

## Reasonable CFD Representations to Test
| Candidate representation | What physical question it can answer | Main warning |
|---|---|---|
| Phase-flux multiphase model | What bulk liquid mass reaches the steam outlet? | Does not resolve droplet-size-dependent carryover well. |
| Post-convergence DPM sweep | Which droplet sizes are likely to escape under the resolved flow field? | Strongly depends on inlet PSD and wall-fate assumptions. |
| DPM + Eulerian Wall Film | Does wall deposition remain separated, or does it re-enter the core? | Needs more closures and better calibration. |
| Three-field annular-style framework | Are gas-core droplets, wall film, and interconversion all important to the physics question? | Likely overkill unless re-entrainment is a dominant suspected mechanism. |

## What This Evidence Does Not Justify
- It does not justify claiming that `10 um` is the real geothermal inlet PSD.
- It does not justify treating every wall hit as permanent separation without an explicit wall-film assumption.
- It does not justify copying Chen's droplet distribution into geothermal CFD as if it were geothermal data.
- It does not justify ignoring chemistry-based carryover evidence when solid or dissolved contaminants may be more informative than droplet tracks alone.

## Related Pages
- Synthesis:
  - [geothermal-separator-inlet-droplets-and-carryover](../synthesis/geothermal-separator-inlet-droplets-and-carryover.md)
  - [fluent-separator-efficiency-methods](../synthesis/fluent-separator-efficiency-methods.md)
  - [annular-flow-three-field-cfd-patterns](../synthesis/annular-flow-three-field-cfd-patterns.md)
- Sources:
  - [purnanto-2013-cfd-geothermal-separator](../sources/purnanto-2013-cfd-geothermal-separator.md)
  - [pointon-2009-geothermal-separator-sizing-cfd-validation](../sources/pointon-2009-geothermal-separator-sizing-cfd-validation.md)
  - [chen-2025-straight-through-cyclone-water-separator](../sources/chen-2025-straight-through-cyclone-water-separator.md)
  - [mondal-sharma-2024-air-water-annular-flow-cfd](../sources/mondal-sharma-2024-air-water-annular-flow-cfd.md)
  - [skoog-2020-annular-flow-three-field-cfd-thesis](../sources/skoog-2020-annular-flow-three-field-cfd-thesis.md)
- Entities:
  - [multiphase-dpm-particle-tracking](../entities/multiphase-dpm-particle-tracking.md)
