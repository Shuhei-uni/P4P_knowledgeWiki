# Preliminary Results Report — Setup 010V2a

## Setup link and evidence

- Setup definition: [010V2a — EWF splash sensitivity](../../active/010V2a-ewf-splash.md)
- Parent setup: [010V2 — EWF deposition and film-inventory control](../../active/010V2-ewf-deposition-film-inventory.md)
- Run identity: live Fluent session on server `1`, captured `2026-07-22`; the active case/data pair was already loaded. The expected branch filenames are `010V2a-ewf-splash.cas.h5` and `010V2a-ewf-splash.dat.h5`, but their full remote paths were not captured by this read-only pass.
- Fluent version: `Ansys Fluent 2024 R2`
- Evidence class: preliminary EWF splash diagnostic; **not converged and not mass-balanced**.

## 1. Run scope

This is the splash-only child of `010V2`. The intended controlled change is EWF particle splashing; edge separation and particle stripping remain out of scope. The post-simulation checks inspected the already-loaded session without loading case/data or advancing the solution.

The readback confirms two mixture phases, global DPM interaction with the continuous phase `Off`, and DPM maximum particle steps `10000`. The standard post-analysis collector does not capture EWF film-state fields, so it did **not** independently confirm the live global splash switch, wall-level DPM Wall Splash switch, impingement model, or splashed-particle count.

Machine artifacts:

- [carrier-flux check](../../../PyAnsys/output/post_simulation_analysis/010V2a-ewf-splash-1963-flux-check.json)
- [residual check](../../../PyAnsys/output/post_simulation_analysis/010V2a-ewf-splash-1963-residual-check.json)
- [residual plot](../../../PyAnsys/output/post_simulation_analysis/010V2a-ewf-splash-1963-residual-check.png)
- [DPM Particle Tracks Summary](../../../PyAnsys/output/post_simulation_analysis/010V2a-ewf-splash-1963-retry-dpm-summary.txt)

## 2. Numerical results

### Phase flux and scoped interpretation

| Quantity | Value |
|---|---:|
| Liquid inlet | `111.074 kg/s` |
| Vapour inlet | `80.690 kg/s` |
| Vapour at steam outlet | `81.4218 kg/s` |
| Liquid at steam outlet | `0 kg/s` in the extracted phase report |
| Total inlet | `191.764 kg/s` |
| Reported steam-outlet total | `81.4218 kg/s` |
| Derived imbalance | `110.3422 kg/s` (`57.54 %` of inlet) |

The result contains no active lower liquid-drain/brine-outlet contribution in the extracted flux report. The large apparent imbalance is therefore consistent with liquid being retained in the modelled separator/film domain, but it is **not** a closed liquid balance and must not be converted into separator efficiency, steam-purity, or splash-performance evidence.

### Liquid-holdup assumption

`User-specified / Assumed`: for this no-brine-outlet diagnostic, liquid that does not leave through the steam outlet is allowed to remain in the separator while the EWF/splash mechanism is inspected. The project accepts that approximation for the present diagnostic only.

`Reported context`: Purnanto's CFD baseline assumed a constant water level just above the brine outlet and excluded explicit brine-bottom flow dynamics ([purnanto-2013], p.5; [Purnanto baseline](../../../CFD_wiki/wiki/setups/geothermal-boc-separator-fluent-2013-baseline.md)). It does **not** prove that the present retained liquid is physically steady. A later drain/holdup closure is required before a whole-separator claim.

### DPM and splash status

The retried live DPM Particle Tracks Summary completed for all six original-particle injections after allowing Fluent at least three minutes to finish. These are original-particle fates, not EWF splash-event counts.

| Diameter | Tracked | Escaped | Trapped | Incomplete | Unclassified difference* |
|---:|---:|---:|---:|---:|---:|
| `5.63 µm` | 2170 | 2162 | 0 | 7 | 1 |
| `28.14 µm` | 2170 | 2158 | 2 | 4 | 6 |
| `56.27 µm` | 2174 | 2007 | 5 | 4 | 158 |
| `112.54 µm` | 2174 | 1510 | 20 | 3 | 641 |
| `168.81 µm` | 2174 | 1008 | 33 | 3 | 1130 |
| `348.88 µm` | 2170 | 435 | 54 | 0 | 1681 |

\* `Unclassified difference = tracked - escaped - trapped - incomplete`. It is not assigned a physical fate because the compact Fluent Summary does not identify the omitted category or categories. Do not treat it as zero, escaped, trapped, absorbed, or splashed mass.

The displayed escape count decreases sharply with diameter, but this is only a diagnostic trend. Neither represented escaped mass nor a closed per-injection fate balance is available from this compact summary, and the carrier/film solution remains unsteady.

`User-specified / Assumed`: incomplete particles are treated as a long-residence, separator-retained population that may later escape by entrainment. Keep that population separate; it must not be silently counted as either completed escape or completed collection. Purnanto likewise retained incomplete tracks as an ambiguous category and used an explicit, non-rigorous assumption for its collection estimate rather than proving their eventual fate ([Purnanto efficiency workflow](../../../CFD_wiki/wiki/synthesis/fluent-separator-efficiency-methods.md)).

## 3. Residuals and solution state

The residual monitor contains `963` samples through iteration `1963`.

| Residual | Final value | Final-100 range | Assessment |
|---|---:|---:|---|
| Continuity | `2.290e-3` | `2.228e-3`–`2.608e-3` | not converged |
| X velocity | `1.178e-4` | `1.154e-4`–`1.316e-4` | low/stable |
| Y velocity | `1.160e-4` | `1.123e-4`–`1.341e-4` | low/stable |
| Z velocity | `1.399e-4` | `1.343e-4`–`1.618e-4` | low/stable |
| Liquid volume fraction | `1.343e-3` | `1.298e-3`–`1.413e-3` | bounded but above a strict convergence target |
| Turbulent kinetic energy `k` | `2.130e-1` | `1.115e-2`–`3.889e-1` | strongly oscillatory |
| Dissipation `epsilon` | `4.759e-1` | `1.323e-2`–`5.526e-1` | strongly oscillatory |

Iteration count alone is not adequate here. The bouncy `k` and `epsilon` histories, non-negligible continuity residual, and unclosed liquid inventory mean the field may still be evolving. This run is unsuitable for comparing splash intensity or film transport against the clean `010V2` parent.

## 4. EWF evidence still required

The generic post-simulation workflow does not currently export the EWF quantities needed to diagnose this branch. Before another analysis or claim, capture histories and final wall-zone reports for:

- film Courant number, film mass/inventory, maximum and area-weighted film thickness;
- film DPM mass source, absorbed DPM mass, film outflow mass, and film velocity/drainage direction;
- splashed parcel count and represented splashed mass, distinct from original-injection DPM fates;
- film stripped mass and film separated mass, which should be inactive unless an unintended interaction is enabled;
- global Particle Splashing, wall-level DPM Wall Splash, number of splashed particles, impingement model, and film-edge outlet state.

The target closure is: original injected DPM mass = completed direct escape + film absorption/source + film inventory change + film outflow + represented splashed/secondary-particle mass + explicitly unresolved mass. It is only a bookkeeping target until each term is actually extracted.

## 5. Conclusion and next action

**Outcome: needs follow-up.** Keep `010V2a` active and diagnostic. The fast progression to roughly `1963` iterations is useful for locating the instability, but it is not sufficient for a splash result.

1. Do not use the zero reported steam-outlet liquid flux as a separation-efficiency result while the lower liquid inventory remains unclosed.
2. Add the EWF field monitors above, then continue only to a documented transient averaging window if film CFL, film mass, and source histories remain bounded.
3. Preserve this DPM Summary, then obtain a fate report that identifies the unclassified difference and represented mass before treating DPM escape as a mass-based result.
4. Compare only against an equally monitored, stable `010V2` no-splash control before attributing a difference to particle splashing.
