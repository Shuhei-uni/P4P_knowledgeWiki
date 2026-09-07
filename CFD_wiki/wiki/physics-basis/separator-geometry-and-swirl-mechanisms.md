# Physics Basis: Separator Geometry and Swirl Mechanisms

## Scope
- Physical question: how do inlet shape and separator geometry change the swirl field that drives separation?
- Why this question matters for separator CFD: many separator choices that look geometric are actually flow-physics choices about where angular momentum is created, dissipated, and recovered.

## Evidence Snapshot
| Topic | Current best statement | Evidence label | Main source |
|---|---|---|---|
| Modern separator preference | Spiral or scrolled-entry BOC designs are favored in later geothermal practice. | `Reported` | [zarrouk-purnanto-2014], p.253; [pointon-2009], p.946-947 |
| Entry effect | Scrolled entry produced fewer escaping fine droplets than simple tangential entry in a geothermal-scale validation case. | `Reported` | [pointon-2009], p.946-947 |
| Swirl-tradeoff warning | Stronger swirl is not always better over the full operating range. | `Reported` | [chen-2025], p.11-13, p.17-18 |
| Practical inlet band | Common BOC inlet velocities are described around `30-40 m/s`. | `Reported` | [zarrouk-purnanto-2014], p.253 |

## What Prior Research Reports
- `Reported`: Zarrouk and Purnanto 2014 describe the effect of inlet nozzle design on BOC separator performance and emphasize the design importance of smooth entry and controlled tangential momentum ([zarrouk-purnanto-2014], p.248-253).
- `Reported`: Pointon 2009 found that scrolled entry outperformed simple tangential entry in CFD, with closer agreement to design predictions and stronger tangential velocity distribution over the cross-section ([pointon-2009], p.946-947).
- `Reported`: Purnanto 2013 compares Bangma, Lazalde-Crabtree, and spiral-inlet geometries specifically because geometry alters internal velocity and pressure structure, which then changes outlet steam quality trend ([purnanto-2013], p.7-9).
- `Reported`: Chen 2025 shows that swirl-generator angle changes internal flow field and separation performance, but not in a simple monotonic way ([chen-2025], p.11-18).

## What Prior Research Assumes
- `Assumed`: smoother entry that generates more coherent circumferential motion is generally preferable to abrupt entry that creates local dissipation and uneven swirl.
- `Assumed`: geometric changes are often interpreted through their effect on tangential velocity distribution, not only through global pressure drop.

## Cross-Paper Inferences
- `Inferred`: geometry should be judged not just by whether it creates swirl, but by whether it creates useful swirl in the right part of the vessel and sustains it long enough for liquid migration and drainage.
- `Inferred`: the geometry question therefore has at least three sub-questions:
  - how much tangential momentum is generated;
  - how uniformly it fills the separator cross-section;
  - how much of it is lost to turbulence, recirculation, and re-entrainment.
- `Inferred`: the right separator geometry is operating-window dependent, which is why a geometry that looks best at one flow rate may not stay best across the full range.

## Unknowns and Weak Evidence
- `Missing`: a public geothermal dataset that directly compares several inlet geometries with matched droplet PSD, film behavior, pressure loss, and chemistry carryover under the same operating range.
- `Missing`: a universal criterion for when inlet smoothing, scroll length, or swirl angle becomes excessive for geothermal separator carryover control.

## Governing Physics
- Geometry changes the inflow angular momentum entering the separator.
- Angular momentum then couples to radial pressure distribution, which controls outward liquid migration and core formation.
- At the same time, added curvature and stronger swirl can increase turbulence production, secondary recirculation, and pressure loss.
- Good separator geometry is therefore a balance between centrifugal separation benefit and turbulence/re-entrainment penalty.

## Consequence for CFD Modeling
- Geometry studies should compare more than one output. Pressure drop alone is not enough, and steam dryness alone is not enough.
- The physically relevant outputs are at least:
  - tangential velocity distribution,
  - core pressure depression,
  - liquid accumulation or film regions,
  - steam-outlet liquid carryover.
- If geometry comparison is the main goal, the CFD model should keep non-geometric assumptions as frozen as possible so geometry remains the main changed variable.

## Reasonable CFD Representations to Test
| Candidate representation | What physical question it can answer | Main warning |
|---|---|---|
| Lower-cost RANS geometry comparison | Which inlet family creates the most plausible swirl and carryover trend? | May miss fine differences driven by anisotropic turbulence or transient film behavior. |
| RANS + DPM geometry comparison | Does geometry change droplet escape by size class? | Depends strongly on inlet PSD assumptions. |
| RSM-based comparison | Does a stronger-anisotropy model materially change which geometry looks best? | Higher cost should be justified by an actual model-choice uncertainty. |

## What This Evidence Does Not Justify
- It does not justify claiming that spiral or scrolled entry is always best in every geothermal operating range.
- It does not justify transferring Chen's swirl-angle optimum directly into geothermal separator design.
- It does not justify changing geometry and turbulence or droplet assumptions at the same time when the real goal is to isolate geometry behavior.

## Related Pages
- Sources:
  - [pointon-2009-geothermal-separator-sizing-cfd-validation](../sources/pointon-2009-geothermal-separator-sizing-cfd-validation.md)
  - [purnanto-2013-cfd-geothermal-separator](../sources/purnanto-2013-cfd-geothermal-separator.md)
  - [zarrouk-purnanto-2014-geothermal-separator-design-overview](../sources/zarrouk-purnanto-2014-geothermal-separator-design-overview.md)
  - [chen-2025-straight-through-cyclone-water-separator](../sources/chen-2025-straight-through-cyclone-water-separator.md)
- Synthesis:
  - [geothermal-separator-design-and-cfd-patterns](../synthesis/geothermal-separator-design-and-cfd-patterns.md)
- Entities:
  - [geometry-vertical-boc-cyclone-separator](../entities/geometry-vertical-boc-cyclone-separator.md)
  - [geometry-tangential-inlet-cyclone-separator](../entities/geometry-tangential-inlet-cyclone-separator.md)
