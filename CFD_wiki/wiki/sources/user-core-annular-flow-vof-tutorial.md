# Source: User Core-Annular-Flow VOF Fluent Tutorial

## Scope
- Source type: user-provided tutorial transcript summarized from a YouTube-style Fluent walkthrough.
- Primary use: generic Fluent VOF startup pattern for a sharp two-phase core-annular interface.
- Project use: informs a separator sensitivity branch where the inlet is intentionally pre-segregated into wall-side liquid and core-side steam.

## Applicability
- `Useful`: how to configure a basic transient VOF case with separate inlet zones, gravity, interface-focused numerics, and simple phase initialization.
- `Not directly reusable`: outlet type, geometry scale, wetting assumptions, turbulence choice, and timestep magnitude.
- `Reason`: the tutorial is a straight pipe core-annular example, not a swirling geothermal separator with a pressure-controlled steam outlet.

## Reported Tutorial Settings
| Topic | Tutorial setting | Transfer note |
|---|---|---|
| Fluent launch | `Double Precision` | reusable as a safe default for interface tracking |
| Solver family | `Pressure-Based`, `Transient` | reusable |
| Gravity | on, downward `-9.81 m/s2` in `y` | reusable if project axis convention matches |
| Multiphase | `VOF`, `2` phases | reusable |
| VOF option | `Implicit Body Forces` | reusable for gravity-dominated interface motion |
| Phase layout | one phase in inner-core inlet, the other in outer annulus inlet | physically analogous to the separator split-inlet idea |
| Surface tension | enabled | reusable only if the separator branch explicitly wants a resolved interface force |
| Wall adhesion | enabled | high-risk transfer because no project-specific contact angle basis exists |
| Turbulence | standard `k-epsilon` with enhanced wall treatment | analogy only; not a separator default |
| Coupling | `Coupled` | reusable as one transient VOF option |
| Spatial schemes | momentum/turbulence `Second Order Upwind` | reusable |
| Initialization | domain initialized with one bulk phase, secondary-phase fraction set to `0` | reusable as a startup pattern |
| Tutorial timestep | `0.001 s` | not directly reusable because project velocity scale is much higher |
| Outlet | `Outflow` | not reusable for the pressure-controlled separator branch |

## What This Tutorial Adds
- `Reported`: a practical Fluent pattern for running a sharp two-phase inlet split as a transient VOF problem.
- `Reported`: `Implicit Body Forces` and double precision are treated as important for interface stability in gravity-dominated cases.
- `Reported`: initialization matters; the tutorial does not start from a fully mixed domain.
- `Inferred`: the tutorial is most valuable here as a numerics/workflow exemplar, not as physics validation for geothermal separator performance.

## What Should Not Be Copied Blindly
- `Do not copy` the `Outflow` outlet to the geothermal separator branch. The project branch still needs a steam-side `Pressure Outlet`.
- `Do not copy` the tutorial timestep directly. The project inlet strip is much thinner and faster than the tutorial's `2 m/s` pipe case.
- `Do not copy` wall adhesion without a stated wetting assumption because contact angle can artificially lock or release the wall film.
- `Do not treat` the tutorial turbulence choice as stronger evidence than the geothermal separator baseline or the annular-flow literature already in the wiki.

## Project Transfer Rule
- Use this source to justify a `Transient VOF` sensitivity branch only when the goal is to check whether a sharp pre-segregated inlet interface survives into the separator more credibly than the steady `Mixture` branch.
- If the VOF branch still gives non-physical behavior, use that result as evidence that interface-only escalation is insufficient, not as a reason to keep tuning the same setup indefinitely.

## Related Pages
- Physics basis:
  - [separator-flow-physics](../physics-basis/separator-flow-physics.md)
  - [governing-equations-and-modeling-levels](../physics-basis/governing-equations-and-modeling-levels.md)
  - [uncertainties-and-assumption-register](../physics-basis/uncertainties-and-assumption-register.md)
- Synthesis:
  - [annular-flow-three-field-cfd-patterns](../synthesis/annular-flow-three-field-cfd-patterns.md)
- Setup lineage using this source:
  - [../../../Setups/past/archived/02b-vof-split-inlet-transient.md](../../../Setups/past/archived/02b-vof-split-inlet-transient.md)
