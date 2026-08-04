# Replication of Purnanto's Enthalpy-Dependent Steam-Separation Results

## Document Purpose
This document is an evidence brief for the project's mid-year technical report. It records the motivation, literature basis, numerical method, interim results, limitations, and remaining work for reproducing the steam-quality analysis of Purnanto, Zarrouk, and Cater (2013). Operational details are retained in the appendices for reproducibility but are not the main focus.

The study is an interim replication exercise, not yet a completed validation. Its purpose is to establish a traceable CFD baseline before evaluating changes to the geothermal separator inlet or geometry.

## Executive Summary
Purnanto et al. (2013) investigated geothermal steam-water separation using a steady continuous-phase CFD solution followed by Discrete Phase Model (DPM) droplet tracking. The present project is reproducing six of the paper's operating conditions using Ansys Fluent and PyFluent. For each condition, the reported steam and liquid mass flows are applied, a Harwell-based nine-bin droplet distribution is generated, the carrier flow is advanced for 1500 iterations, and the droplet fates are classified as escaped, trapped, or incomplete.

All six baseline cases and all six spiral-inlet cases have now completed the automated workflow. The baseline/Bangma-target qualities range from `99.6718%` to `99.8507%`; the spiral-inlet qualities range from `99.9668%` to `99.9795%`. Each case contains 1500-iteration monitor evidence, nine injection-level result rows, and a passing DPM fate-mass audit. These results establish a functioning and traceable comparison method, but they are not validation results. Carrier-flow residuals do not demonstrate convergence, incomplete trajectories remain substantial, and the exact geometry, inherited DPM controls, and steam-quality convention are not fully verified.

## Role in the Research Project
The broader project aims to improve the CFD representation of a vertical bottom-outlet cyclone separator, particularly the treatment of the two-phase inlet. A credible reference model is required before alternative inlet distributions or geometry changes can be assessed. This replication contributes by:

- establishing a literature-based operating matrix;
- reconstructing a traceable droplet-size distribution from Purnanto's published material;
- automating identical setup, solution, DPM, and export steps across all conditions;
- separating iteration completion from numerical convergence;
- producing injection-level liquid-carryover data for later comparison; and
- identifying unresolved model-form and particle-tracking uncertainties.

## Research Question and Objectives
The replication addresses the following question:

> Can the current Fluent reconstruction reproduce the enthalpy-dependent outlet steam-quality trend reported by Purnanto et al. when the paper's phase mass flows and a documented Harwell-derived droplet distribution are applied consistently?

The specific objectives are to:

1. reproduce the six reported operating conditions;
2. calculate condition-specific droplet diameters and injection velocities;
3. run a consistent 1500-iteration carrier-flow calculation for each condition;
4. quantify escaped, trapped, and incomplete liquid for every injection;
5. calculate outlet steam quality from escaped liquid mass flow;
6. compare the completed six-point trend with the digitized Purnanto results; and
7. document deviations that arise from missing paper details or numerical limitations.

## Literature Basis
Purnanto et al. modelled geothermal steam-water separators using steady, incompressible, isothermal CFD and used DPM particle tracking to estimate liquid carryover and steam quality ([purnanto-2013], p.5-9). The paper provides phase mass flows for the enthalpy conditions and uses the Harwell correlation to estimate droplet size ([purnanto-2013], p.3-5).

The paper does not provide all information needed for exact reproduction. In particular, it states that nine droplet injections were used but does not list their exact diameters, mass allocation, parcel mapping, or all tracking controls ([purnanto-2013], p.8). These missing details require a documented reconstruction and prevent the present work from being described as exact replication.

### Evidence labels
- `Reported`: stated in Purnanto et al. (2013).
- `Observed`: read from Fluent, run logs, manifests, or exported results.
- `Calculated`: obtained directly from reported inputs and stated equations.
- `Inferred`: a reconstruction choice required because the paper is incomplete.
- `Provisional`: an interim result affected by unresolved convergence or interpretation.

## Methodology

### Operating conditions
The six paper conditions are reproduced using the phase mass flows in Table 2. Cases 7 and 8 in the local working file are excluded because they are not part of the target six-condition sweep.

| Case | Nominal condition | Liquid flow (kg/s) | Steam flow (kg/s) | DPM face-normal speed (m/s) |
|---:|---|---:|---:|---:|
| 1 | `1600 kJ/kg, total flow reduced by 25%` | 87.69 | 60.52 | 25.6670 |
| 2 | `1440 kJ/kg` | 132.76 | 64.85 | 27.5033 |
| 3 | `1520 kJ/kg` | 124.84 | 72.77 | 30.8623 |
| 4 | `1600 kJ/kg` | 116.92 | 80.69 | 34.2212 |
| 5 | `1680 kJ/kg` | 109.00 | 88.61 | 37.5801 |
| 6 | `1760 kJ/kg` | 101.09 | 96.52 | 40.9348 |

The phase mass flows are `Reported` values from Purnanto's Table 2 ([purnanto-2013], p.5). The normal speeds are `Calculated` from the local Harwell input generator.

The term **enthalpy condition** requires care. The current model is isothermal and has the energy equation disabled. Enthalpy is therefore not imposed as a thermal boundary condition. Instead, each paper enthalpy identifies a corresponding steam-liquid mass-flow split. This reproduces the paper's operating matrix without claiming to solve flashing or thermal-energy transport.

### Fluent model
The current baseline uses Ansys Fluent 2024 R2 with a steady pressure-based solver, the Mixture multiphase model, steam as the primary phase, liquid water as the secondary phase, RNG `k-epsilon` turbulence, and gravity enabled (`Observed`). Hybrid initialization is applied to each case. Further setup details are recorded in the [Purnanto live setup reference](purnanto-live-setup-reference.md).

The audited HDF5 reference that anchors the automated baseline records the following principal settings:

| Parameter | Value | Evidence |
|---|---:|---|
| Mesh cells | 2,964,593 | `Observed` |
| Mesh nodes | 572,556 | `Observed` |
| Minimum orthogonal quality | 0.277635 | `Observed` |
| Maximum aspect ratio | 12.8899 | `Observed` |
| Solver | Steady, pressure-based | `Observed` |
| Multiphase model | Mixture | `Observed` |
| Turbulence model | RNG `k-epsilon` | `Observed` |
| Energy equation | Disabled | `Observed` |
| Gravity | `(0, -9.81, 0) m/s2` | `Observed` |
| Inlet / outlet types | Mass-flow inlet / pressure outlet | `Observed` |
| Outlet pressure | 1.12 MPa | `Observed` |
| Initialization | Hybrid Initialization | `Reported` and implemented |

The baseline is the closest available reconstruction, but exact geometry parity with the separator variant used for Purnanto's plotted results has not yet been independently demonstrated. Geometry identity remains a validation risk.

### Droplet-size calculation
Purnanto uses the Harwell correlation to estimate the Sauter mean diameter:

```text
x_sa = 1.91 D_t (Re^0.1 / We^0.6) (rho_g / rho_l)^0.6
x_med = 1.42 x_sa

Re = rho_g v_t D_t / mu_g
We = rho_g v_t^2 D_t / sigma
v_t = m_g / (rho_g A_inlet)
```

Here, `D_t` is the inlet characteristic diameter, `v_t` is steam velocity, `rho_g` and `rho_l` are gas and liquid densities, `mu_g` is gas dynamic viscosity, and `sigma` is surface tension. The implementation uses the Purnanto fluid-property values at the stated separator pressure and calculates a different dimensional distribution for each operating condition (`Calculated`).

| Harwell input | Value | Evidence |
|---|---:|---|
| Steam density, `rho_g` | 5.73 kg/m3 | `Reported`, Purnanto Table 1 |
| Liquid density, `rho_l` | 881.77 kg/m3 | `Reported`, Purnanto Table 1 |
| Steam dynamic viscosity, `mu_g` | `15.188e-6 kg/(m s)` | `Reported`, Purnanto Table 1 |
| Surface tension, `sigma` | 0.0411 N/m | `Reported`, Purnanto Table 1 |
| Inlet characteristic diameter, `D_t` | 0.724 m | `Observed` implementation input |
| Inlet flow area, `A_inlet` | 0.4115 m2 | `Observed` implementation input |

### Droplet-distribution provenance
The active droplet distribution was produced through the following traceable chain:

1. Purnanto's Figure 5 reproduces a standard pipeline droplet-size distribution attributed to Hoffmann (2007). The paper states `x_med = 1.42 x_sa`, approximately `5%` of liquid is at or below `0.3 x_med`, and the distribution reaches `100%` by `2.9 x_med` (`Reported`; [purnanto-2013], p.3-4).
2. The cumulative Figure 5 curve was digitized into [Digitized_Figure5_(Purnanto 2013)).csv](<../../../../Code/Digitized_Figure5_(Purnanto%202013)).csv>) (`Observed` local source artifact).
3. [droplet_distribution.py](../../../../Code/droplet_distribution.py) defines nine representative normalized diameters: `0.01`, `0.05`, `0.10`, `0.20`, `0.30`, `0.62`, `1.00`, `1.50`, and `2.90 x_med`. Their cumulative liquid-mass levels are `0.001625`, `0.0083`, `0.0166`, `0.0333`, `0.05`, `0.25`, `0.50`, `0.75`, and `1.00`. Consecutive differences define the injection mass fractions (`Inferred`).
4. [harwell_calculation.py](../../../../Code/harwell_calculation.py) calculates `x_sa`, `x_med`, each dimensional diameter, each injection mass flow, and the inlet-normal injection speed for every condition (`Calculated`).
5. The generated [harwell_results.csv](../../../../Code/harwell_results.csv) is read directly by the PyFluent sweep (`Observed`).

The exact nine bins are not published by Purnanto. The present distribution is a reproducible reconstruction informed by Purnanto's Figure 5 and stated limits, not a verbatim recovery of the original injection table. Digitization and bin selection are consequently sources of uncertainty. [distribution_fitting.py](../../../../Code/distribution_fitting.py) preserves the earlier curve-fitting work; the production simulations use the fixed distribution in `droplet_distribution.py`.

### DPM implementation
Nine existing Fluent injections are updated before the carrier-flow calculation. Each injection uses its condition-specific diameter, liquid mass flow, and positive face-normal speed. The releases use the inlet surface and the `water-liquid-dpm` material.

| DPM setting | Implemented value |
|---|---|
| Injection type | Surface injection |
| Injection surface | `inlet` |
| Direction | Normal to Face |
| Particle material | `water-liquid-dpm` |
| Carrier-phase interaction | Intended one-way; not preserved in the completed baseline-sweep manifests |
| Maximum tracking steps | Inherited from baseline; not preserved in the sweep manifests |
| Step-length factor | Inherited from baseline; not preserved in the sweep manifests |
| Fate reporting | Per-injection and per-zone |

The nine injection mass flows are checked to ensure that they sum to the liquid inlet flow for the relevant condition. DPM reports retain escaped, trapped, and incomplete mass separately. The accepted results use Fluent's labeled `Final` DPM mass-flow column; particle-count weighting is not used. Incomplete particles are not automatically counted as either escaped or captured.

### Solution and data-processing sequence
For each condition, the automation:

1. loads the same baseline case;
2. applies the reported steam and liquid mass flows;
3. updates and reads back all nine DPM injections;
4. hybrid-initializes the carrier flow;
5. advances the carrier solution for 1500 verified iterations;
6. saves a pre-DPM case/data pair;
7. tracks all DPM injections and exports per-zone fate reports; and
8. saves a post-DPM case/data pair and machine-readable manifest.

The implementation is contained in [run_purnanto_enthalpy_sweep.py](../../../PyAnsys/scripts/setup/run_purnanto_enthalpy_sweep.py). Recovery runs use [continue_purnanto_current_case.py](../../../PyAnsys/scripts/setup/continue_purnanto_current_case.py).

### Steam-quality calculation
The current project metric is:

```text
steam quality (%) = steam mass flow
                    / (steam mass flow + escaped liquid mass flow) * 100
```

The steam term currently uses the inlet steam mass flow from Purnanto's operating matrix. This is an `Inferred` convention. Before final reporting, it must be compared with the Fluent steam-outlet flow and with the exact interpretation used to construct the paper's steam-quality figure.

### Quality assurance
A condition is accepted as technically complete only if:

- inlet phase mass-flow readbacks match the target condition;
- all nine injections match the intended surface, material, diameter, mass flow, and speed;
- injection mass flow sums to the condition's liquid flow;
- residual-history iteration numbers demonstrate completion of 1500 iterations;
- pre-DPM and post-DPM case/data files exist;
- exactly nine injection-level result rows are exported;
- escaped, trapped, and incomplete fates are retained; and
- the summed DPM fate mass agrees with injected mass within `0.2%`.

The Fluent `number-of-iterations` setting is not used as proof of completed iteration history because it records the most recent run request. Residual-history iteration numbers and saved manifests provide the completion evidence.

## Completed Sweep Results

**Evidence audit: 29 July 2026**

| Case | Verified iterations | Escaped liquid (kg/s) | Trapped liquid (kg/s) | Incomplete liquid (kg/s) | Provisional quality (%) |
|---:|---:|---:|---:|---:|---:|
| 1: `1600 kJ/kg, -25% flow` | 1500 | 0.1367 | 51.49 | 36.06 | 99.7746 |
| 2: `1440 kJ/kg` | 1500 | 0.2136 | 74.53 | 58.01 | 99.6718 |
| 3: `1520 kJ/kg` | 1500 | 0.1967 | 69.55 | 55.09 | 99.7304 |
| 4: `1600 kJ/kg` | 1500 | 0.1817 | 63.24 | 53.50 | 99.7753 |
| 5: `1680 kJ/kg` | 1500 | 0.1648 | 56.81 | 52.02 | 99.8144 |
| 6: `1760 kJ/kg` | 1500 | 0.1443 | 51.37 | 49.58 | 99.8507 |

The combined file contains `54` injection rows. All six cases pass the per-injection `0.2%` fate-mass tolerance. Cases 2-6 preserve standalone residual histories from iteration `1` to `1500`. Case 1 preserves block-by-block monitor advancement to iteration `1500` in its manifest, but no standalone residual-history CSV was mirrored locally.

The incomplete mass remains much larger than the escaped mass in every case. The high calculated steam quality therefore describes confirmed escaped liquid only; it does not resolve the physical fate of incomplete trajectories.

### Comparison with digitized Purnanto results

The project cases were paired with the six red `Simulation` points in the digitized Bangma graph.

| Case | Project velocity (m/s) | Digitized velocity (m/s) | Digitized quality (%) | Project quality (%) | Difference (percentage points) |
|---:|---:|---:|---:|---:|---:|
| 1 | 25.6670 | 25.5449 | 99.9915 | 99.7746 | -0.2169 |
| 2 | 27.5033 | 27.4737 | 99.7748 | 99.6718 | -0.1030 |
| 3 | 30.8623 | 30.7394 | 99.8121 | 99.7304 | -0.0817 |
| 4 | 34.2212 | 34.0722 | 99.8322 | 99.7753 | -0.0569 |
| 5 | 37.5801 | 37.3986 | 99.8637 | 99.8144 | -0.0493 |
| 6 | 40.9348 | 41.0000 | 99.8882 | 99.8507 | -0.0375 |

All project points are below the digitized simulation series. The discrepancy generally narrows with increasing enthalpy/velocity. Case 1 remains the largest mismatch and does not reproduce the paper's near-`100%` reduced-flow point.

### Spiral-inlet sibling sweep

A separate completed spiral-inlet branch applies the same phase-flow matrix with spiral-area Harwell inputs. Its qualities are `99.9679%`, `99.9678%`, `99.9668%`, `99.9795%`, `99.9786%`, and `99.9724%`. Five cases are within approximately `0.014-0.025` percentage points below the digitized spiral simulation values. Case 4 is approximately `0.150` percentage points above the digitized value and is the principal spiral trend mismatch.

The spiral comparison is documented separately in
[purnanto-spiral-inlet-enthalpy-dpm-replication.md](purnanto-spiral-inlet-enthalpy-dpm-replication.md)
and setup report
[08c-purnanto-spiral-inlet-enthalpy-dpm-sweep.md](../../../Setup%20report/08c-purnanto-spiral-inlet-enthalpy-dpm-sweep.md).

### Interpretation

The automation preserved the target operating matrix, generated nine injection results per case, identified escaped and trapped zones, and reconciled reported fate mass. The baseline sweep's final continuity residuals are approximately `0.193-0.343` for Cases 2-6; Case 1 was previously reported near `0.283`. The spiral sweep's final continuity residuals are approximately `0.145-0.229`. These values do not establish convergence.

The output is therefore suitable as a reproducible replication dataset and discrepancy map, but not as a validated prediction of separator performance.

## Limitations and Uncertainty

### Carrier-flow convergence
Completing 1500 iterations satisfies the project replication protocol but does not prove convergence. The 1500-iteration budget is not treated as a reported paper value. Residual histories and physical outlet monitors must be assessed, and cases should be extended if mass flow, pressure drop, or other integral quantities continue to change.

### Incomplete particle trajectories
Purnanto also reported a large number of incomplete particle trajectories and identified particle tracking and mesh refinement as limitations of the published DPM calculation ([purnanto-2013], p.8). The substantial incomplete fraction in the present simulations is therefore not unique to this implementation and may represent partial reproduction of a known feature of the reference method.

However, incomplete trajectories still cannot be treated as either captured or escaped without evidence. The paper does not provide enough case-by-case mass allocation and tracking detail to establish quantitative parity with the present `41-44%` incomplete liquid fractions. Their physical locations in the current geometry have also not been demonstrated. A leading hypothesis is that particles terminate near the transition between the cylindrical wall and upper dome, but particle tracks or residence-location exports are required before this can be claimed.

### Droplet-distribution reconstruction
Purnanto does not publish the exact nine injection diameters or mass allocation. Results may therefore depend on the inferred bin locations and lower-tail split. A final sensitivity study should compare the active distribution with at least one alternative binning or fitted cumulative distribution.

### Geometry parity
The active baseline is based on the available Purnanto-style Fluent model, but the exact separator geometry associated with the target paper plot must still be confirmed. Any mismatch could affect swirl strength, residence time, and droplet capture.

### Steam-quality convention
The current formula uses reported inlet steam flow rather than a directly exported steam-outlet mass flow. This convention must be audited before final publication-quality comparison.

### Model scope
The intended steady, isothermal, one-way DPM method does not resolve flashing, droplet breakup or coalescence, wall-film transport, or two-way momentum coupling. The completed baseline manifests did not preserve the inherited DPM interaction readback, so one-way coupling remains an unverified setup assumption for that historical result set. Future runs now fail preflight unless phase materials and one-way DPM are read back explicitly.

## Mid-Year Conclusions
The work has established functioning and auditable baseline and spiral-inlet methods for reproducing Purnanto's enthalpy-condition sweep. The operating matrix, droplet derivation, iteration evidence, and injection-level fate exports are traceable from source data to final CSV output. All twelve completed cases passed their DPM mass-balance checks.

The study has not validated either separator model. The principal findings are that fixed iteration count is insufficient evidence of convergence, incomplete particle tracking dominates the baseline uncertainty, and the two geometries show distinct mismatches against the digitized paper trends. These findings define the next phase more clearly than the provisional quality values alone.

## Remaining Work
1. Run a non-mutating reload audit of representative final case/data pairs using the hardened phase-material, DPM-coupling, injection, and boundary checks.
2. Review physical outlet-flow and pressure-drop monitors; extend only cases whose integral outputs are still changing.
3. Localize incomplete particle trajectories, particularly near the cylinder-to-dome transition.
4. Audit steam quality using Fluent steam-outlet flow and confirm the paper's calculation convention.
5. Confirm the exact geometry/CAD lineage of both completed baselines.
6. Test sensitivity to the reconstructed droplet-bin distribution and inherited tracking controls.
7. Re-run only after maximum steps, step-length factor, high-resolution tracking, DPM wall fates, and inward face-normal direction are captured in a preflight manifest.
8. Separate discrepancies into geometry, carrier-flow, injection-distribution, and particle-tracking contributions.

## Reproducibility Appendix

### File locations
- Consolidated automation and mesh-convergence handoff: [PURNANTO_ENTHALPY_DPM_AUTOMATION_RUNBOOK.md](../../../PyAnsys/docs/PURNANTO_ENTHALPY_DPM_AUTOMATION_RUNBOOK.md)
- Baseline on Windows: `C:\Users\qtra338\Documents\baseline.cas.h5`
- Fluent output on Windows: `C:\Users\qtra338\Documents\enthalpy_sweep_verified_20260721_v2`
- Mirrored local results: [enthalpy_sweep_verified_20260721_v2](../../../PyAnsys/output/enthalpy_sweep_verified_20260721_v2/)
- Sweep script: [run_purnanto_enthalpy_sweep.py](../../../PyAnsys/scripts/setup/run_purnanto_enthalpy_sweep.py)
- Status tool: [check_sweep_status.py](../../../PyAnsys/scripts/connection/check_sweep_status.py)

### Remote-execution note
PyFluent runs on the Mac as the controller for Fluent on the Windows workstation. VPN or Wi-Fi loss can interrupt the gRPC control stream even while Fluent retains the latest solved state. Iteration chunks, checkpoints, residual-history evidence, and separate pre-DPM saves were introduced to make recovery auditable. This is an execution constraint rather than a physical-model result.

### Recovery record for the snapshot
- Case 1 was recovered and then verified to iteration 1500 using residual-history evidence.
- Case 2 was recovered at iteration 1375 and advanced for the remaining 125 iterations.
- Case 3 was recovered from the retained carrier-flow state, verified at iteration 1500, and completed through a zero-iteration DPM recovery on 23 July 2026.

## Sources and Supporting Files
- Purnanto, M. H., Zarrouk, S. J., and Cater, J. E. (2013). *CFD Modelling of Two-Phase Flow inside Geothermal Steam-Water Separators*. IPENZ Transactions, Vol. 40.
- [Purnanto et al. source extraction](../../../CFD_wiki/wiki/sources/purnanto-2013-cfd-geothermal-separator.md) (`[purnanto-2013]`).
- [Local Purnanto paper PDF](<../../../../Literature/Purnanto%20et%20al.%20(2013),%20CFD%20Modelling%20of%20Two-Phase%20Flow%20inside%20Geothermal%20Steam-Water%20Separators.pdf>).
- [Digitized Purnanto Figure 5 data](<../../../../Code/Digitized_Figure5_(Purnanto%202013)).csv>).
- [Active droplet distribution](../../../../Code/droplet_distribution.py).
- [Harwell input generator](../../../../Code/harwell_calculation.py).
- [Generated Fluent injection table](../../../../Code/harwell_results.csv).
- [Purnanto setup report](../../../Setup%20report/08-purnanto-one-inlet-massflow-recreation.md).
- [Completed baseline sweep setup](../../../Setup%20report/08b-purnanto-baseline-enthalpy-dpm-sweep.md).
- [Completed spiral sweep setup](../../../Setup%20report/08c-purnanto-spiral-inlet-enthalpy-dpm-sweep.md).
- [Purnanto live setup reference](purnanto-live-setup-reference.md).
