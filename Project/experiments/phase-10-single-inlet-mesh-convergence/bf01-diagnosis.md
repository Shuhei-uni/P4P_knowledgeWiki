# BF01 — Why ON failed earlier

| Question | Evidence-backed answer |
| --- | --- |
| Immediate failure path | Earlier maximum-speed and turbulence-residual spikes in ON; epsilon grows sharply at N3560, then k AMG divergence/FPE at N3567 |
| Unique root cause | Not established. Local numerical coupling instability is a working mechanism; first failing cell/region was not saved |
| Was the initial solution reset? | No. Fourteen checked cell pressure/velocity/turbulence/phase-fraction arrays match the original N3000 data exactly |
| Restart effect | Steam-outlet mixture face velocities were reconstructed on reload; zero-update OFF reload reproduces the same changes |
| Does the existing comparison isolate the ON switch? | No. Original OFF is uninterrupted; ON is a saved-state restart. Reloaded OFF and initial ON have all 28 checked cell/face arrays exactly equal, but OFF has not been solved from that restart |
| Shared setup concern | Both runs retain liquid and fail phase closure; a body-force algorithm does not add a withdrawal path |
| Scope | Evidence collection and zero-update reload inspection only; no new solve selected; consequential interpretation remains for designated Astra/human review |

![Matched OFF/ON window](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/bodyforce-BF01-diagnosis/matched-window.png)

Raw N3000–N3560 comparison window, before the final overflow. Maximum speed and epsilon use log scales. Both full failure tails remain in [BF01 terminal evidence](bf01-results.md). Inventory change over steady iterations is not a physical filling rate.

| Matched evidence | OFF | ON | Meaning / limit |
| --- | --- | --- | --- |
| N3000 liquid inventory | 710.871 kg | 710.871 kg | Same loaded bulk state |
| Largest maximum-speed difference through N3400 | Reference | 0.144% | Early trajectories remain close |
| Largest inventory difference through N3400 | Reference | 0.0165% | ON did not resolve shared retained-liquid growth |
| N3470 maximum speed | 79.83 m/s | 2501.94 m/s | Large local maximum; region not identified |
| N3470 mean speed | 26.864 m/s | 26.878 m/s | Bulk mean stays close while the maximum spikes |
| N3560 liquid inventory | 975.624 kg | 974.957 kg | Shared inventory background remains similar |
| Native FPE coordinate | N3911 | N3567 | Different iteration paths; not a clean causal attribution |
| ON epsilon residual N3559 → N3560 | Not applicable | 0.25082 → 550.86 | Roughly 2196-fold growth preceding global blow-up |

## Field and restart audit

| Check | Result |
| --- | --- |
| Original N3000 vs initial ON data | 14 checked cell arrays exactly equal; 3 mixture face-velocity arrays differ |
| Region of face differences | Only steamoutlet: U 453 faces, V all 493 faces, W 385 faces |
| Largest face-component difference | U 32.28, V 38.21, W 25.22 m/s; flux totals unchanged |
| Zero-update OFF reload | Reproduces the same face changes while body force remains OFF |
| Reloaded OFF vs initial ON | All 28 checked arrays exactly equal; ON face differences cannot be assigned to the ON setter alone |
| Derived initial mean vorticity | Original 101.788837 → reloaded 101.714946 s⁻¹; an additional reload-sensitive quantity |
| Restore proof | Last valid ON N3005 pair reloaded, counter and complete recorded scientific state verified |
| New solved updates | 0. BF01 lifetime spend remains 567; campaign spend remains 22869–23559 |

## Mechanisms and discriminating evidence

| Candidate | Evidence | Status / missing test |
| --- | --- | --- |
| Pressure/velocity/turbulence numerical feedback | ON develops local maxima and epsilon growth before global failure; momentum URF 0.7 and k/epsilon 0.8 unchanged | Plausible immediate mechanism; no first-cell spatial proof |
| Reload changes the numerical trajectory | Boundary face reconstruction verified with zero-update OFF reload | Proven initial reconstruction; effect on later failure needs matched OFF restart solve |
| Liquid routing / retained mass | ON at N3460: liquid feed 116.92 kg/s, outlet only 25.81 kg/s; inventory continues to grow in both cases | Shared closure concern; does not by itself prove the unique divergence cause |
| Changed gravity or another unintended setting | Primary/expert alias roundtrip and strict other-state/reopen proofs | No observed settings drift; ON changes coupling, not the gravity vector |
| Operating-density setup error | Recorded Mixture uses mixture-averaged density | Fluent documents this option; lightest-phase recommendation is specifically for VOF |
| Single bad mesh cell | Same mesh identity in OFF/ON; whole baseline also failed | Cannot rule out local mesh interaction without early spatial evidence |

Fluent [§27.2.7](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_multiphase_setup.html) describes implicit body force as a correction to pressure/face-flow coupling and recommends it for Mixture with body forces. This recommendation is not proof that all other coupled equations will converge. [§37.3.3](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_uns_solve_pvel_1.html) identifies relaxation as a separate stability control.

Purnanto's [2013 paper](https://www.researchgate.net/publication/269519626_CFD_MODELLING_OF_TWO-PHASE_FLOW_INSIDE_GEOTHERMAL_STEAM-WATER_SEPARATORS), §2.3 p3, explicitly selects Mixture; §3.1 p5 excludes brine-pipe water flow and assumes a fixed water level. Its continuum bottom/sink implementation is not specified. The present growing inventory is not a verified reproduction of that fixed-level condition. A sole pressure outlet can mathematically discharge both phases; sealed bottom alone does not prove no steady solution exists.

| Proposed next control — not selected | Contract |
| --- | --- |
| Question | Does an OFF restart reproduce the earlier failure without the ON switch? |
| Parent / invariant | Same original M04 N3000 pair; identical read/reopen/report policy; all other science fixed |
| Single contrast | Both body-force flags OFF; compare to existing ON restart |
| Smallest useful horizon | 567 additional updates to N3567, including 5 smoke + 562 fixed updates |
| Budget | Separate proposed diagnostic; would raise campaign upper bound from 23559 to 24126; existing BF01 cap is not reset |
| Decision | Needs new scientific selection; no automatic unchanged retry or baseline rehabilitation |
| Later numerical probe | Lower turbulence/momentum relaxation only after selecting a separate controlled contrast; do not combine it with the restart control |

| Evidence | Owner |
| --- | --- |
| [Matched history summary](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/bodyforce-BF01-diagnosis/diagnosis.json) | PyAnsys machine evidence |
| [Initial arrays](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/bodyforce-BF01-diagnosis/initial-field-comparison.json) | Native HDF comparisons |
| [Face-zone mapping](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/bodyforce-BF01-diagnosis/face-field-comparison.json) | Only outlet faces change |
| [Zero-update OFF reload](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/bodyforce-BF01-diagnosis/zero-update-OFF-reopen.json) | Complete state/counter and ON restore proof |
| [Restart array comparison](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/bodyforce-BF01-diagnosis/restart-field-comparison.json) | Identical selected OFF-reload/ON arrays and native copy hashes |
