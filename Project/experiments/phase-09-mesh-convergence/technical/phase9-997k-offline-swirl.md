# Offline swirl calculation — Phase 9 997k N8080

| Item | Verified value / definition |
| --- | --- |
| Source | Selected OneDrive `997k-initial-bulk-N8080.cas.h5` and `.dat.h5`; both hashes match the selection manifest |
| Mesh | 997,604 cells; separator zone 974,673 cells; virtual collector zone excluded from section cuts |
| State | Selected initial bulk-development N8080; no qualified steady-state or physical-validation claim |
| Axis and sign | Global +Y through x = z = 0; angular-momentum component `z*u_x - x*u_z` |
| Fluxes | `Gtheta = integral(rho*u_y*(z*u_x-x*u_z) dA)`; `Gy = integral(rho*u_y^2 dA)`; `S = Gtheta/(Rref*Gy)` |
| Mixture | Saved mixture density and velocities |
| Phases | Saved phase velocity and density, weighted by saved volume fraction |
| Normalisations | Outer radius 1.067 m; hydraulic radius from actual section `A/P`, including all solid boundary perimeters |
| Integration | Closed polygon cut geometry with exact area and first moments; saved cell fields held constant within each cut cell |

## Section values

| Height y (m) | Area (m²) | Mixture S, outer radius | Vapour S, outer radius | Liquid S, outer radius | Mixture S, hydraulic radius |
| --- | --- | --- | --- | --- | --- |
| 0.30 | 3.16559 | 0.6805 | 0.0787 | 1.0908 | 2.0572 |
| 0.90 | 3.16540 | 0.6795 | 0.2959 | 0.9521 | 2.0541 |
| 1.50 | 3.16481 | 1.0852 | 0.9136 | 1.6357 | 3.2812 |
| 3.00 | 3.16503 | -1.5161 | -1.5316 | -0.9711 | -4.5843 |
| 4.00 | 3.16532 | -1.0890 | -1.0910 | -0.9888 | -3.2923 |
| 5.00 | 3.16497 | -1.4212 | -1.4173 | -1.9641 | -4.2969 |

The inlet spans y = 1.704–2.428 m. The three lower sections are below the inlet; y = 3–5 m samples the upper vessel. Hydraulic radius is about 0.353 m for these sections. Signs reflect the combination of axial transport direction and angular momentum; a sign change alone does not prove reversal of tangential rotation.

![Swirl profile](../../../../PyAnsys/output/swirl-997k/20261009/swirl-profile.png)

## Counterflow below the inlet

| Height y (m) | Upward-flow mixture S | Downward-flow mixture S | Downward fraction of axial momentum flux | Absolute angular transport ratio |
| --- | --- | --- | --- | --- |
| 0.30 | -2.2900 | 1.3489 | 81.6% | 1.5217 |
| 0.90 | -1.0925 | 1.0830 | 81.5% | 1.0848 |
| 1.50 | -0.9488 | 2.0850 | 67.0% | 1.7105 |

Opposing transport contributions partly cancel in the signed section integral. The absolute transport ratio is a cancellation diagnostic, not the signed swirl number. Upper-region downward-flow ratios are omitted from the plot where that flow carries less than 1% of axial momentum; they remain in the machine record.

## Saved inlet quantities

| Inlet | Mass flow (kg/s) | Area-weighted X velocity (m/s) | Angular-momentum influx about +Y (N·m) |
| --- | --- | --- | --- |
| liquidinlet | 116.92 | 27.13361 | -4652.465 |
| steaminlet | 80.69 | 26.80262 | -2388.741 |

Total incoming angular-momentum flux: **-7041.206 N·m**. This uses saved boundary mass flux and velocity rather than the nominal common speed in the pasted estimate. It is an angular-momentum influx through the side inlets, not an internal swirl number.

## Verification and limits

| Check | Result |
| --- | --- |
| Source identity | Both SHA256 hashes match selected N8080 manifest |
| Cell-field mapping | Each required array spans IDs 1–997604 |
| Phase mapping | Case material records identify vapour and liquid; volume fractions sum to one and reconstruct saved mixture density within 1e-9 kg/m³ |
| Cut geometry | All cell loops close; summed cell areas match an independent boundary-only polygon cut within 1e-7 m² |
| Polygon implementation | Square, nested hole, concave L and disconnected-island checks passed |
| Section location sensitivity | Mixture S at y ±0.02 m differs by at most about 4.1% at 1.50 m, 0.6% at 0.90 m and 2.1% at 0.30 m |

The computed magnitudes support a strong-swirl diagnostic for the mixture in this saved state. The vapour result is weaker in the lower vessel, so one mixture number does not describe both phases. This supports investigating turbulence-model sensitivity; it does not prove that RSM improves accuracy. The [Fluent 2025 R2 guide](https://ansyshelp.ansys.com/public/views/secured/corp/v252/en/flu_ug/flu_ug_uns_sec_models_swirl.html) specifies a hydraulic radius and recommends RSM for highly swirling flow. Preserve the normalisation when making that comparison.

The extraction uses cell-constant offline integration. It has not been compared with Fluent-native interpolated plane reports and does not provide a mesh-error estimate. Wall film, DPM momentum, pressure terms and turbulent stresses are excluded. The RNG swirl-factor model constant remains separate from these calculated swirl numbers.

## Reproduction

- [Extractor](../../../../PyAnsys/scripts/analysis/calculate_saved_997k_swirl.py)
- [Machine summary and exact paths](../../../../PyAnsys/output/swirl-997k/20261009/summary.json)
- [Section table](../../../../PyAnsys/output/swirl-997k/20261009/sections.csv)

Run locally: `PyAnsys/.venv/bin/python PyAnsys/scripts/analysis/calculate_saved_997k_swirl.py`. Source case/data remain unchanged.
