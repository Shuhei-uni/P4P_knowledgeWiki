# Physics Basis: Separator Flow Physics

## Scope
- Physical question: what flow mechanisms are believed to separate steam and liquid inside geothermal cyclone separators?
- Why this question matters for separator CFD: if the dominant separator physics are wrong, a solver can appear numerically stable while representing the wrong carryover mechanism.

## Evidence Snapshot
| Topic | Current best statement | Evidence label | Main source |
|---|---|---|---|
| Separator family | Vertical BOC cyclone separators are a dominant geothermal design family. | `Reported` | [zarrouk-purnanto-2014], p.238-241, p.253 |
| Main mechanism | Separation is driven mainly by swirl-induced centrifugal action rather than gravity alone. | `Reported` | [zarrouk-purnanto-2014], p.238-241; [rivas-cruz-2015], p.881-883 |
| Internal diagnostics | Velocity profile, pressure distribution, and outlet steam quality are useful proxies for separator behavior. | `Reported` | [purnanto-2013], p.7-9; [zarrouk-purnanto-2014], p.248-249 |
| Core pressure | The separator core runs at lower pressure than the outer region in cyclone operation. | `Reported` | [purnanto-2013], p.8 |
| Flow-path sensitivity | Entry design changes tangential velocity distribution and therefore droplet fate. | `Reported` | [pointon-2009], p.946-947; [chen-2025], p.11-13 |

## What Prior Research Reports
- `Reported`: geothermal separator reviews describe vertical cyclone separators as centrifugal devices that create a rotating vapor-dominant core and drive liquid toward the wall and lower collection regions ([zarrouk-purnanto-2014], p.238-241; [rivas-cruz-2015], p.881-883).
- `Reported`: Purnanto 2013 used CFD to compare separator internal velocity profile, pressure distribution, and outlet steam quality across inlet designs, treating those fields as meaningful performance indicators ([purnanto-2013], p.7-9).
- `Reported`: Pointon 2009 found that a scrolled entry produced stronger tangential velocity distribution and fewer escaping `3 um` droplets than a simpler tangential entry in a geothermal-scale separator validation study ([pointon-2009], p.946-947).
- `Reported`: Chen 2025 found that stronger swirl was not monotonically better; separation followed a rise-fall-rise trend because centrifugal transport, turbulence, and re-entrainment competed across the operating range ([chen-2025], p.11-13, p.17-18).

## What Prior Research Assumes
- `Assumed`: in practical separator design literature, good separation is often treated as the result of sufficiently strong swirl plus adequate drainage/collection geometry, even when direct internal droplet measurements are unavailable.
- `Assumed`: many separator studies infer internal separator quality from outlet behavior rather than from complete in-vessel film and droplet measurements.

## Cross-Paper Inferences
- `Inferred`: the internal separator problem is not just "generate as much swirl as possible." The physically useful target is swirl strong enough to push liquid outward and downward, but not so aggressive that turbulence, breakup, or re-entrainment undo the gain.
- `Inferred`: pressure and velocity fields are not merely visualization outputs; they are the main evidence for whether the CFD model is reproducing the expected core-low-pressure / wall-high-pressure separator structure.
- `Inferred`: separator CFD is therefore best treated as a flow-mechanism argument first and an efficiency-number generator second.

## Unknowns and Weak Evidence
- `Missing`: direct field-resolved measurements of geothermal separator internal droplet concentration, wall-film thickness, and re-entrainment rates.
- `Missing`: a broadly reusable geothermal dataset that simultaneously reports internal velocity field, pressure field, droplet-size distribution, and outlet chemistry for the same separator.
- `Missing`: a clean threshold defining when stronger swirl starts to hurt geothermal separator performance through breakup or film re-entrainment.

## Governing Physics
- Continuity requires total mass entering the separator to leave through steam, brine, deposition, or storage terms.
- Momentum balance in swirling flow contains pressure-gradient, inertia, viscous, gravity, and turbulence-stress effects. In separator interpretation, the important qualitative result is that rotational motion supports an inward pressure drop and outward liquid migration.
- For cyclone-like flow, angular-momentum distribution matters because entry geometry controls how much of the inlet momentum becomes useful circumferential motion rather than local recirculation or dissipation.
- Gravity remains relevant after swirl has moved liquid toward the wall because the separator still needs a credible route for collected liquid to leave the steam-dominant flow path.

## Consequence for CFD Modeling
- A separator model should be able to represent swirl, core-pressure depression, outer-wall liquid migration, and outlet split behavior before its efficiency number is trusted.
- If the main question is "does the geometry create the right rotating flow structure?" a lower-cost RANS separator model may be acceptable as a first pass.
- If the main question is "does deposited liquid stay collected or return to the gas core?" a wall-film or more detailed transient representation becomes more justified.

## Reasonable CFD Representations to Test
| Candidate representation | What physical question it can answer | Main warning |
|---|---|---|
| Steady RANS + phase-flux check | Does the geometry produce plausible core pressure, swirl field, and bulk carryover trend? | May miss transient re-entrainment and interface behavior. |
| RANS + DPM | Do droplets of different sizes tend to escape or collect under the resolved flow field? | Assumes droplet fate can be treated on top of an already adequate continuous field. |
| Transient multiphase or wall-film-aware model | Does collected liquid remain separated, or does it re-enter the core? | Higher cost and more assumptions about interfacial closures. |
| RSM-based separator model | Is anisotropic swirl physics important enough that eddy-viscosity RANS may bias the separator mechanism? | Higher convergence cost does not guarantee better geothermal prediction without validation. |

## What This Evidence Does Not Justify
- It does not justify assuming that any increase in swirl automatically improves separator efficiency.
- It does not justify treating outlet steam quality alone as proof that internal liquid handling is physically right.
- It does not justify copying air-water separator operating values directly into geothermal steam-brine CFD.
- It does not justify ignoring drainage, wall-film, or re-entrainment questions once bulk swirl structure looks plausible.

## Related Pages
- Sources:
  - [purnanto-2013-cfd-geothermal-separator](../sources/purnanto-2013-cfd-geothermal-separator.md)
  - [zarrouk-purnanto-2014-geothermal-separator-design-overview](../sources/zarrouk-purnanto-2014-geothermal-separator-design-overview.md)
  - [rivas-cruz-2015-geothermal-separator-state-of-art-review](../sources/rivas-cruz-2015-geothermal-separator-state-of-art-review.md)
  - [pointon-2009-geothermal-separator-sizing-cfd-validation](../sources/pointon-2009-geothermal-separator-sizing-cfd-validation.md)
  - [chen-2025-straight-through-cyclone-water-separator](../sources/chen-2025-straight-through-cyclone-water-separator.md)
- Synthesis:
  - [geothermal-separator-design-and-cfd-patterns](../synthesis/geothermal-separator-design-and-cfd-patterns.md)
- Entities:
  - [geometry-vertical-boc-cyclone-separator](../entities/geometry-vertical-boc-cyclone-separator.md)
