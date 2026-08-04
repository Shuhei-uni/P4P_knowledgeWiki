# Purnanto Baseline Enthalpy and DPM Sweep

## 1. Purpose

Record the completed six-condition Purnanto enthalpy sweep using the available
Purnanto baseline case and Bangma-target Harwell inputs.

This is a child of
[08-purnanto-one-inlet-massflow-recreation.md](08-purnanto-one-inlet-massflow-recreation.md).
It is a completed calculation branch, not proof that the carrier solutions
converged or that the baseline geometry is an exact Bangma model.

Evidence labels:

- `Reported`: from Purnanto et al. (2013).
- `Observed`: present in controller logs, manifests, residual exports, or DPM reports.
- `Inferred`: reconstructed from reported equations/figures or used as a comparison convention.
- `Missing`: required evidence was not preserved.

## 2. Setup Identity

| Item | Value |
|---|---|
| Parent | setup `08` |
| Fluent baseline | `C:\Users\qtra338\Documents\baseline.cas.h5` |
| Fluent release | `2024 R2` (`Observed`) |
| Geometry label | Purnanto baseline / Bangma-target operating reconstruction |
| Exact geometry identity | `Missing`; not visually proven |
| Inlet | `inlet`, one mixed `Mass-Flow Inlet` |
| Escaped DPM zone | `steam_outlet` (`Observed`) |
| Trapped DPM zone | `fluid_outlet` (`Observed`) |
| Output directory | `C:\Users\qtra338\Documents\enthalpy_sweep_verified_20260721_v2` |
| Local evidence mirror | `../PyAnsys/output/enthalpy_sweep_verified_20260721_v2/` |

The `0.4115 m2` Harwell inlet area and comparison against the digitized Bangma
graph establish the target comparison, not exact geometry provenance.

## 3. Operating Matrix

| Case | Condition | Liquid (kg/s) | Steam (kg/s) | Injection speed magnitude (m/s) |
|---:|---|---:|---:|---:|
| 1 | `1600 kJ/kg, -25% flow` | 87.69 | 60.52 | 25.666961 |
| 2 | `1440 kJ/kg` | 132.76 | 64.85 | 27.503345 |
| 3 | `1520 kJ/kg` | 124.84 | 72.77 | 30.862273 |
| 4 | `1600 kJ/kg` | 116.92 | 80.69 | 34.221202 |
| 5 | `1680 kJ/kg` | 109.00 | 88.61 | 37.580130 |
| 6 | `1760 kJ/kg` | 101.09 | 96.52 | 40.934817 |

The phase mass flows are `Reported` from Table 2 of Purnanto et al. (2013).
The velocities and droplet diameters are `Inferred` using the Harwell equation,
paper properties, and `0.4115 m2` inlet area.

## 4. DPM Definition

| Setting | Applied value |
|---|---|
| Existing injections | `injection-0` through `injection-8` |
| Particle type | `inert` |
| Particle material | `water-liquid-dpm` |
| Injection type | `surface` |
| Surface | `inlet` |
| Velocity | Normal to Face with positive magnitude |
| Diameter and flow source | `Code/harwell_results.csv` |
| Position randomization | disabled |
| Number of bins | 9 |

The CSV retains a negative `z_velocity_ms` column from the earlier Cartesian
definition. Normal-to-face mode uses `abs(z_velocity_ms)` because Fluent expects
a magnitude and obtains direction from the face normal.

The nine mass fractions and representative `x/x_med` values are an `Inferred`
reconstruction of the digitized Purnanto/Hoffmann distribution. The paper does
not publish the exact nine injection diameters or mass allocation.

## 5. Run Sequence

For every case the controller:

1. loaded the baseline case fresh;
2. checked the expected inlet, outlet, and nine injection names;
3. applied and read back both phase mass flows;
4. applied and read back all injection type, material, surface, flow, velocity, and diameter values;
5. hybrid-initialized the carrier field;
6. advanced 1500 iterations with monitor x-axis verification;
7. saved a pre-DPM case/data pair;
8. enabled per-injection reporting, ran DPM tracking, and exported aggregate and injection reports;
9. reconciled escaped, trapped, and incomplete mass against injected mass; and
10. saved a post-DPM case/data pair.

The injections were configured before carrier-flow iteration, as required for
this automation campaign. They were intended to remain one-way and therefore
not affect the carrier solve.

`Missing`: the completed sweep manifests did not preserve the inherited DPM
interaction readback, maximum tracking steps, step-length factor, high-resolution
tracking state, or every wall DPM boundary condition. Those values must not be
claimed as verified for this completed branch.

## 6. Completed Results

Steam quality uses the project comparison convention:

```text
quality = steam inlet flow / (steam inlet flow + escaped liquid flow)
```

This convention is `Inferred`; the exact convention behind the published plot
has not been independently confirmed.

| Case | Iterations evidenced | Escaped (kg/s) | Trapped (kg/s) | Incomplete (kg/s) | Quality (%) |
|---:|---:|---:|---:|---:|---:|
| 1 | 1500 | 0.1367 | 51.49 | 36.06 | 99.7746 |
| 2 | 1500 | 0.2136 | 74.53 | 58.01 | 99.6718 |
| 3 | 1500 | 0.1967 | 69.55 | 55.09 | 99.7304 |
| 4 | 1500 | 0.1817 | 63.24 | 53.50 | 99.7753 |
| 5 | 1500 | 0.1648 | 56.81 | 52.02 | 99.8144 |
| 6 | 1500 | 0.1443 | 51.37 | 49.58 | 99.8507 |

All six cases contain nine injection-result rows and passed the `0.2%`
per-injection fate-mass tolerance.

Cases 2-6 preserve standalone residual histories through iteration 1500.
Case 1 preserves block-by-block monitor advancement through iteration 1500 in
its manifest, but its standalone residual-history CSV was not mirrored locally.

## 7. Evidence Limits

- Completing 1500 iterations is not convergence evidence. Final continuity
  residuals remain high.
- Incomplete particle mass is substantial and cannot be reassigned to escaped
  or trapped fate without additional evidence.
- Cases 1-3 predate full pre/post-DPM injection-state storage in the manifest;
  their logs record nine readback validations, but the complete state dictionaries
  were not retained.
- Fluent DPM reports contain `Initial`, `Final`, and `Change` mass-flow columns.
  The parser uses `Final`; both were equal for these inert isothermal reports.
- Count-weighted escaped mass is not used in the accepted results.
- The exact geometry identity, inlet face-normal vector, inherited DPM coupling,
  and inherited tracking controls require a fresh inspection before another run.

## 8. Reproducibility Links

- Sweep script: `../PyAnsys/scripts/setup/run_purnanto_enthalpy_sweep.py`
- Input generator: `../../Code/harwell_calculation.py`
- Fixed distribution: `../../Code/droplet_distribution.py`
- Injection CSV: `../../Code/harwell_results.csv`
- Combined results: `../PyAnsys/output/enthalpy_sweep_verified_20260721_v2/all_enthalpy_injection_results.csv`
- Case summaries: `../PyAnsys/output/enthalpy_sweep_verified_20260721_v2/all_enthalpy_case_summary.csv`

