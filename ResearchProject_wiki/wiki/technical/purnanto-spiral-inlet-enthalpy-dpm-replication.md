# Purnanto Spiral-Inlet Enthalpy and DPM Replication

## Purpose

Interpret the completed spiral-inlet six-condition sweep as project evidence and
compare it with Purnanto's digitized spiral-inlet `Simulation` series.

The concrete case definition is maintained in
[setup 08c](../../../Setup%20report/08c-purnanto-spiral-inlet-enthalpy-dpm-sweep.md).
Reusable paper setup evidence remains in the CFD wiki rather than being
duplicated here.

Evidence labels:

- `Reported`: stated by Purnanto et al. (2013).
- `Observed`: present in logs, manifests, residual CSVs, and DPM reports.
- `Inferred`: reconstructed Harwell bins, digitized graph values, or steam-quality convention.
- `Missing`: required evidence not preserved.
- `Provisional`: result affected by unresolved convergence or interpretation.

## Project Role

The spiral sweep provides a paper-linked reference before project-specific inlet
or separator modifications are judged. It is a sibling comparison to the
baseline/Bangma-target sweep, not a pure geometry-only sensitivity:

- inlet area changes from `0.4115 m2` to `0.524176 m2`;
- gas velocity changes;
- Harwell diameters and injection speeds change; and
- outlet and trapped-zone identities differ.

## Completed Evidence

All six cases contain:

- monitor evidence through 1500 iterations;
- a standalone residual-history CSV from iteration `1` to `1500`;
- nine pre-DPM and nine post-DPM injection readbacks;
- nine injection-level fate rows;
- direct escaped, trapped, and incomplete `Final` mass flows; and
- a passing `0.2%` fate-mass reconciliation.

| Case | Velocity (m/s) | Escaped (kg/s) | Trapped (kg/s) | Incomplete (kg/s) | Quality (%) |
|---:|---:|---:|---:|---:|---:|
| 1 | 20.1496 | 0.01941 | 85.60 | 2.068 | 99.9679 |
| 2 | 21.5913 | 0.02088 | 129.40 | 3.307 | 99.9678 |
| 3 | 24.2282 | 0.02416 | 121.70 | 3.120 | 99.9668 |
| 4 | 26.8651 | 0.01655 | 113.00 | 3.907 | 99.9795 |
| 5 | 29.5020 | 0.01896 | 103.70 | 5.235 | 99.9786 |
| 6 | 32.1355 | 0.02667 | 94.38 | 6.680 | 99.9724 |

Steam quality is `Inferred` as steam inlet flow divided by steam inlet flow plus
escaped liquid. It does not assign incomplete particles to either outlet fate.

## Purnanto Comparison

| Case | Digitized quality (%) | Project quality (%) | Difference (percentage points) |
|---:|---:|---:|---:|
| 1 | 99.9880 | 99.9679 | -0.0201 |
| 2 | 99.9880 | 99.9678 | -0.0202 |
| 3 | 99.9876 | 99.9668 | -0.0208 |
| 4 | 99.8297 | 99.9795 | +0.1498 |
| 5 | 99.9929 | 99.9786 | -0.0143 |
| 6 | 99.9977 | 99.9724 | -0.0253 |

Five cases are close on the compressed quality scale. Case 4 does not reproduce
the paper's low simulation point and is the main trend discrepancy. Small
percentage-point differences should not be understated: the corresponding
escaped-liquid differences can be materially larger because all qualities are
near `100%`.

Digitized values are `Inferred`. The extraction uses the plotted axis
calibration and color segmentation; the original numerical series was not
available.

## Interpretation

Compared with the baseline/Bangma-target branch, the spiral case reports much
less incomplete mass and approximately one order of magnitude less escaped
liquid. This is consistent with better separation in the available spiral
model, but it cannot yet be attributed to geometry alone because velocity,
Harwell diameters, injection material name, mesh, and boundary-zone treatment
also differ.

The final continuity residuals remain approximately `0.145-0.229`. Completing
the fixed budget therefore does not demonstrate convergence.

## Remaining Uncertainty

- `Missing`: exact CAD/mesh lineage relative to Purnanto's original spiral geometry.
- `Missing`: preserved maximum steps, step-length factor, high-resolution tracking, and every DPM wall condition.
- `Missing`: direct steam-outlet flow used in the quality denominator.
- `Inferred`: exact nine-bin distribution and mass allocation.
- `Provisional`: comparison until integral monitors and geometry parity are checked.

## Evidence Files

- Combined case summary:
  `../../../PyAnsys/output/spiral_enthalpy_sweep_20260725/all_enthalpy_case_summary.csv`
- Injection results:
  `../../../PyAnsys/output/spiral_enthalpy_sweep_20260725/all_enthalpy_injection_results.csv`
- Plot data:
  `../../../PyAnsys/output/spiral_enthalpy_sweep_20260725/plots/spiral_inlet_output_steam_quality_plot_data.csv`
- Digitized reference:
  `../../../PyAnsys/output/graph_digitization/spiral_inlet_reference_digitized_points.csv`
- Setup record:
  `../../../Setup report/08c-purnanto-spiral-inlet-enthalpy-dpm-sweep.md`

