# Read-Only Fluent Setup Difference Audit

- Server id: `1`
- Base case: `C:\Users\syok443\Documents\TwoPhaseInletV2(Purnanto)\Base Case Data Set\TwoPhaseInletV2(Purnanto).cas.h5`
- Candidate case: `C:\Users\syok443\Documents\TwoPhaseInletV2(Purnanto)\10a\TwoPhaseInletV2(Purnanto)-10a-ewf.cas.h5`
- Data files: none loaded; this is a case-setup comparison only.

## Difference Summary

- Total changed paths: `15`
- Paths in expected 10a/EWF area: `8`
- Paths requiring review: `7`

| Classification | Path | Base value | Candidate value |
|---|---|---|---|
| `expected-10a-area` | `models.discrete_phase.user_defined_functions.film_regime` | `"<missing>"` | `"none"` |
| `requires-review` | `models.discrete_phase.user_defined_functions.impingement_model` | `"<missing>"` | `"none"` |
| `expected-10a-area` | `models.discrete_phase.user_defined_functions.splashing_distribution` | `"<missing>"` | `"none"` |
| `expected-10a-area` | `boundary_conditions.wall.bottom.phase.mixture.wall_film` | `"<missing>"` | `{"eulerian_film_wall": false}` |
| `expected-10a-area` | `boundary_conditions.wall.bottom.phase.phase-1.wall_film` | `"<missing>"` | `{}` |
| `expected-10a-area` | `boundary_conditions.wall.bottom.phase.phase-2.wall_film` | `"<missing>"` | `{}` |
| `requires-review` | `boundary_conditions.wall.wall.phase.mixture.dpm.normal_coefficient.polynomial.coefficients` | `[1]` | `[1.0]` |
| `requires-review` | `boundary_conditions.wall.wall.phase.mixture.dpm.tangential_coefficient.polynomial.coefficients` | `[1]` | `[1.0]` |
| `expected-10a-area` | `boundary_conditions.wall.wall.phase.mixture.wall_film` | `"<missing>"` | `{"eulerian_film_wall": true, "film_condition_type": "film-wall-initial", "film_height": {"option": "value", "value": 0}, "flux_momentum": [{"option": "value", "value": 0}, {"option": "value", "value": 0}, {"option": "value", "value": 0}], "enable_film_source_terms": false, "enable_flow_momentum_coupling": false, "enable_dpm_wall_splash": true, "impingement_model": "stanton-rutland", "number_of_splashed_particles": 4}` |
| `expected-10a-area` | `boundary_conditions.wall.wall.phase.phase-1.wall_film` | `"<missing>"` | `{}` |
| `expected-10a-area` | `boundary_conditions.wall.wall.phase.phase-2.wall_film` | `"<missing>"` | `{}` |
| `requires-review` | `materials.inert_particle.water-liquid.dpm_surften` | `"<missing>"` | `{"option": "constant", "value": 0.0719404}` |
| `requires-review` | `materials.inert_particle.water-liquid.viscosity` | `"<missing>"` | `{"option": "constant", "value": 0.001003}` |
| `requires-review` | `materials.solid.aluminum.atomic_number` | `"<missing>"` | `{"option": "constant", "value": 13}` |
| `requires-review` | `materials.solid.steel.atomic_number` | `"<missing>"` | `{"option": "constant", "value": 26}` |

Interpretation: `expected-10a-area` identifies paths associated with EWF/film/splash controls. All `requires-review` paths must be checked against the 10a setup definition before treating the branch as clean.
