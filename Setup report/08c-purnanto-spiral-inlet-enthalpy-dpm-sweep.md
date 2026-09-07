# Purnanto Spiral-Inlet Enthalpy and DPM Sweep

## 1. Purpose

Record the completed six-condition enthalpy and DPM sweep using the available
spiral-inlet Fluent baseline. This is a sibling of setup `08b` under
[08-purnanto-one-inlet-massflow-recreation.md](08-purnanto-one-inlet-massflow-recreation.md).

The branch applies Purnanto's operating matrix and particle method to the
spiral-inlet geometry. It is not a geometry-only sensitivity because the inlet
area also changes velocity, Harwell diameter, and injection speed.

Evidence labels are `Reported`, `Observed`, `Inferred`, and `Missing`.

## 2. Setup Identity

| Item | Value |
|---|---|
| Parent | setup `08` |
| Fluent baseline | `C:\Users\qtra338\Documents\baseline_spiral_inlet.cas.h5` |
| Paired baseline data inspected | `baseline_spiral_inlet.dat.h5` |
| Fluent release | `2024 R2` (`Observed`) |
| Inlet | `inlet`, one mixed `Mass-Flow Inlet` |
| Escaped DPM zone | `outlet` (`Observed`) |
| Trapped DPM zone | `bottom` (`Observed`) |
| Output directory | `C:\Users\qtra338\Documents\spiral_enthalpy_sweep_20260725` |
| Local evidence mirror | `../PyAnsys/output/spiral_enthalpy_sweep_20260725/` |

The relationship between this exact baseline CAD/mesh and the geometry described
in `ResearchProject_wiki/wiki/technical/v2-purnanto-spiral-inlet-geometry.md`
remains `Missing`.

## 3. Operating Matrix

| Case | Condition | Liquid (kg/s) | Steam (kg/s) | Injection speed magnitude (m/s) |
|---:|---|---:|---:|---:|
| 1 | `1600 kJ/kg, -25% flow` | 87.69 | 60.52 | 20.149634 |
| 2 | `1440 kJ/kg` | 132.76 | 64.85 | 21.591272 |
| 3 | `1520 kJ/kg` | 124.84 | 72.77 | 24.228170 |
| 4 | `1600 kJ/kg` | 116.92 | 80.69 | 26.865069 |
| 5 | `1680 kJ/kg` | 109.00 | 88.61 | 29.501968 |
| 6 | `1760 kJ/kg` | 101.09 | 96.52 | 32.135537 |

Harwell reconstruction uses `A = 0.724^2 = 0.524176 m2` and the reported
Purnanto fluid properties.

## 4. DPM Definition

| Setting | Applied value |
|---|---|
| Injection names | `5`, `28`, `56`, `112`, `168`, `348`, `562`, `844`, `1631` micron labels |
| Particle type | `inert` |
| Particle material | `liquid-water` |
| Injection type | `surface` |
| Surface | `inlet` |
| Velocity | Normal to Face with positive magnitude |
| Diameter and flow source | `Code/spiral_harwell_results.csv` |
| Position randomization | disabled |
| DPM interaction | disabled in the inspected baseline (`Observed`) |

Every final manifest preserves nine pre-DPM and nine post-DPM injection
readbacks. The DPM report identifies `outlet` as escaped and `bottom` as trapped.

`Missing`: maximum tracking steps, step-length factor, high-resolution tracking,
and all wall DPM conditions were not preserved in the sweep manifests.

## 5. Run Sequence

The same ten-stage sequence as setup `08b` was used: fresh baseline load,
boundary/injection inspection, phase-flow application, injection application,
hybrid initialization, 1500 monitor-verified iterations, pre-DPM save, DPM
update and per-injection reports, mass reconciliation, and post-DPM save.

All six standalone residual CSVs contain iterations `1` through `1500`.

## 6. Completed Results

| Case | Escaped (kg/s) | Trapped (kg/s) | Incomplete (kg/s) | Quality (%) |
|---:|---:|---:|---:|---:|
| 1 | 0.01941 | 85.60 | 2.068 | 99.9679 |
| 2 | 0.02088 | 129.40 | 3.307 | 99.9678 |
| 3 | 0.02416 | 121.70 | 3.120 | 99.9668 |
| 4 | 0.01655 | 113.00 | 3.907 | 99.9795 |
| 5 | 0.01896 | 103.70 | 5.235 | 99.9786 |
| 6 | 0.02667 | 94.38 | 6.680 | 99.9724 |

All six cases contain nine injection rows, all escaped values come from the
Fluent DPM `Final` mass-flow column, and every per-injection fate-mass audit
passed the `0.2%` tolerance.

## 7. Published-Graph Comparison

Against the digitized Purnanto spiral `Simulation` series, project minus
digitized quality is:

| Case | Difference (percentage points) |
|---:|---:|
| 1 | -0.0201 |
| 2 | -0.0202 |
| 3 | -0.0208 |
| 4 | +0.1498 |
| 5 | -0.0143 |
| 6 | -0.0253 |

Case 4 is the clear trend mismatch because the digitized paper simulation point
is approximately `99.8297%`, while the current result is `99.9795%`.

Digitization values are `Inferred` and should retain calibration/extraction
uncertainty. The exact steam-quality convention behind the paper remains
unconfirmed.

## 8. Evidence Limits

- The residual histories prove the requested iteration count, not convergence.
- Final continuity residuals are approximately `0.145-0.229`.
- Incomplete mass is smaller than in setup `08b` but remains unresolved.
- The exact CAD/mesh lineage and paper geometry parity remain unproven.
- Particle count is not used as a mass-flow substitute.
- Another run must use the hardened preflight to verify phase materials,
  one-way DPM, inherited tracking controls, and report generation before solve.

## 9. Reproducibility Links

- Wrapper: `../PyAnsys/scripts/setup/run_purnanto_spiral_enthalpy_sweep.py`
- Shared sweep engine: `../PyAnsys/scripts/setup/run_purnanto_enthalpy_sweep.py`
- Injection CSV: `../../Code/spiral_harwell_results.csv`
- Combined results: `../PyAnsys/output/spiral_enthalpy_sweep_20260725/all_enthalpy_injection_results.csv`
- Case summaries: `../PyAnsys/output/spiral_enthalpy_sweep_20260725/all_enthalpy_case_summary.csv`
- Plot data: `../PyAnsys/output/spiral_enthalpy_sweep_20260725/plots/spiral_inlet_output_steam_quality_plot_data.csv`
