# Physics Basis: Governing Equations and Modeling Levels

## Scope
- Physical question: which governing-physics layers are relevant to separator CFD, and what modeling levels become reasonable under different assumptions?
- Why this question matters for separator CFD: model choice should follow the physics question being asked, not habit or software availability alone.

## Evidence Snapshot
| Topic | Current best statement | Evidence label | Main source |
|---|---|---|---|
| Baseline geothermal workflow | Geothermal separator CFD in this wiki starts from steady RANS plus droplet tracking logic. | `Reported` | [purnanto-2013], p.3-8 |
| Geothermal bridge case | Geothermal-scale validation literature uses RNG `k-epsilon` plus DPM and, for structural loads, URANS. | `Reported` | [pointon-2009], p.945-947 |
| Method-discipline anchor | Chen reports transient pressure-based RSM + DPM with breakup, coalescence, and rough-wall interaction. | `Reported` | [chen-2025], p.8-10 |
| Wall-film precedent | Annular-flow work splits liquid into gas-core droplets and wall film. | `Reported` | [mondal-2024], p.2883-2890; [skoog-2020], p.7-12 |

## What Prior Research Reports
- `Reported`: Pointon 2009 explicitly identifies RANS of the Reynolds-averaged Navier-Stokes equations as the continuous-flow basis, with RNG `k-epsilon` plus swirl modification for main design work and URANS for structural-load extraction ([pointon-2009], p.945-947).
- `Reported`: Purnanto 2013 uses a pressure-based solver, RNG `k-epsilon`, and DPM logic after continuous-field convergence, with mixture-model language appearing alongside particle tracking ([purnanto-2013], p.3-6, p.8).
- `Reported`: Chen 2025 uses a transient pressure-based solver, Reynolds Stress Model, DPM, KHRT breakup, stochastic coalescence, and rough-wall interaction ([chen-2025], p.8-10).
- `Reported`: Mondal 2024 and Skoog 2020 treat the liquid field as at least two physically distinct parts when annular or film-dominated behavior matters: droplets in the gas core and a wall liquid film ([mondal-2024], p.2883-2890; [skoog-2020], p.7-12).

## What Prior Research Assumes
- `Assumed`: steady RANS is acceptable when the main objective is relative separator comparison rather than direct transient film-resolution.
- `Assumed`: simplified multiphase representation can still be useful when the main target is bulk carryover trend rather than resolved interfacial topology.
- `Assumed`: higher-order or more detailed models should be justified by a concrete unresolved mechanism, not by a generic desire for more physics.

## Cross-Paper Inferences
- `Inferred`: separator CFD in this domain sits on a ladder of physics questions:
  - bulk phase split and pressure loss;
  - droplet-size-dependent carryover;
  - wall-film deposition and re-entrainment;
  - unsteady structural loading or strongly anisotropic turbulence.
- `Inferred`: model complexity should rise only when the current physics question cannot be answered credibly by the lower rung.
- `Inferred`: Chen is most valuable here as a model-rationale example, not as proof that RSM + breakup + coalescence is always the right geothermal default.

## Unknowns and Weak Evidence
- `Missing`: a geothermal separator dataset that decisively proves where RNG `k-epsilon` fails and RSM becomes necessary.
- `Missing`: a field-validated geothermal wall-film dataset that clearly justifies EWF or three-field modeling as the default rather than a sensitivity path.
- `Missing`: a public geothermal case that cleanly compares mixture, DPM, VOF, and film-aware models under the same operating condition.

## Governing Physics
### Core continuous-field level
- Continuity:
  - mass conservation governs how much total flow enters and exits the separator.
- Momentum:
  - pressure gradient, inertia, gravity, viscous stress, and turbulence stress govern the resolved separator flow field.
- Turbulence closure:
  - RANS or RSM closes unresolved turbulent stresses, changing how anisotropic swirl and recirculation are represented.

### Phase-carryover level
- Phase-fraction transport or mixture closure:
  - useful when the question is bulk liquid fraction movement and outlet phase flux.
- Lagrangian particle force balance:
  - useful when the question is droplet escape or collection by size class.

### Film and re-entrainment level
- Wall-film conservation:
  - film mass can grow by deposition, shrink by drainage or entrainment, and exchange momentum with the gas core.
- Entrainment/deposition closure:
  - needed when droplets and film are both active parts of the physics question.

## Consequence for CFD Modeling
- Choose the simplest model family that still represents the mechanism under investigation.
- If the question is "how much bulk liquid reaches the steam outlet?" a multiphase phase-flux model may be enough.
- If the question is "which droplet sizes escape?" DPM becomes reasonable.
- If the question is "does wall-deposited liquid re-enter the gas core?" wall-film-aware or three-field logic becomes reasonable.
- If the question is "does anisotropic swirl change the flow field enough to alter the conclusion?" RSM sensitivity becomes reasonable.

## Reasonable CFD Representations to Test
| Model family | Best matched physics question | Strength | Main limitation |
|---|---|---|---|
| Steady RANS + phase flux | Bulk separator trend, pressure loss, outlet liquid fraction | Cheap and interpretable first pass | Limited droplet and film fidelity |
| Steady RANS + DPM | Droplet-size-dependent carryover | Good for mist-style sensitivity studies | Depends on PSD and wall-fate assumptions |
| URANS or transient multiphase | Unsteady outlet behavior or interface motion | Better for time-varying behavior | Higher cost and more setup uncertainty |
| RSM + DPM | Strongly swirling separator flows where anisotropic turbulence may matter | Better aligned with cyclone-flow anisotropy | Higher convergence cost |
| DPM + Eulerian Wall Film | Film deposition and re-entrainment | Represents two liquid pathways explicitly | Closure-heavy and calibration-sensitive |
| Three-field framework | Droplets, film, and gas core all materially matter | Richest mechanism split | Highest complexity and weakest geothermal validation base |

## What This Evidence Does Not Justify
- It does not justify treating the most complex available model as automatically the most credible.
- It does not justify saying that because Chen used RSM, geothermal work must also start from RSM.
- It does not justify saying that because Purnanto used a simpler representation, wall-film-aware models are unnecessary.
- It does not justify changing multiple modeling levels at once if the goal is to isolate one unresolved mechanism.

## Related Pages
- Sources:
  - [purnanto-2013-cfd-geothermal-separator](../sources/purnanto-2013-cfd-geothermal-separator.md)
  - [pointon-2009-geothermal-separator-sizing-cfd-validation](../sources/pointon-2009-geothermal-separator-sizing-cfd-validation.md)
  - [chen-2025-straight-through-cyclone-water-separator](../sources/chen-2025-straight-through-cyclone-water-separator.md)
  - [mondal-sharma-2024-air-water-annular-flow-cfd](../sources/mondal-sharma-2024-air-water-annular-flow-cfd.md)
  - [skoog-2020-annular-flow-three-field-cfd-thesis](../sources/skoog-2020-annular-flow-three-field-cfd-thesis.md)
- Concepts and entities:
  - [two-phase-flow-regime-vs-cfd-representation](../concepts/two-phase-flow-regime-vs-cfd-representation.md)
  - [turbulence-rng-k-epsilon](../entities/turbulence-rng-k-epsilon.md)
  - [turbulence-reynolds-stress-model](../entities/turbulence-reynolds-stress-model.md)
  - [multiphase-dpm-particle-tracking](../entities/multiphase-dpm-particle-tracking.md)
