# Full-flow 1600 kJ/kg DPM replication source handoff

**Prepared:** 2026-10-12  
**Target:** repeat the accepted historical full-flow 1600 kJ/kg carrier and DPM study on M04, 946,967 cells  
**Inspection mode:** read-only; Fluent was not run, initialized, or modified

## Decision

| Question | Evidence-backed answer |
| --- | --- |
| Which historical condition is intended? | **Baseline/Bangma-target Case 4, full-flow 1600 kJ/kg** from `enthalpy_sweep_verified_20260721_v2`. |
| Carrier flows | **Phase 1 steam = 80.69 kg/s; phase 2 liquid = 116.92 kg/s; total = 197.61 kg/s.** |
| Is this the reduced-flow 1600 case? | **No.** Reduced-flow Case 1 used 60.52 kg/s steam and 87.69 kg/s liquid, total 148.21 kg/s. |
| Is this the July spiral-inlet family? | **No.** The spiral family used a different parent, diameters, speed, material identity, and boundary naming. Do not substitute it. |
| Historical result selected here | Accepted July verified-v2 Case 4: 1,500 verified carrier iterations, then one DPM update/report. |
| Can the currently archived Case 4 binary be assumed to be that endpoint? | **No.** The located archive pair belongs to the baseline family, but its adjacent result reports 2.005 kg/s escaped rather than the accepted 0.1817 kg/s. It is an audit candidate, not a certified parent. |

This selection follows the sequence recorded in the historical chat and the matching July log: the full-flow baseline run preceded the later spiral-inlet sweep. The PC archive guide also states that the July spiral sweep was not identified.

## Evidence status convention

| Label | Meaning |
| --- | --- |
| **Direct** | Read back or recorded by the accepted Case 4 manifest, log, report, or result CSV. |
| **Lineage** | Exact value from the recovered original one-inlet carrier setup inherited by the study family, but not fully exported from the accepted `baseline.cas.h5` endpoint. It must be checked against a source binary before parity is claimed. |
| **Candidate** | Related file or zone mapping that has not been proven identical to the accepted run. |
| **Missing** | No accepted-run evidence was found. Do not replace it with a Fluent default. |

## 1. Source identity and locations

### Accepted July run records

| Artifact | Historical Windows path | Current Mac location/status |
| --- | --- | --- |
| Base case loaded fresh | `C:\Users\qtra338\Documents\baseline.cas.h5` | Historical path from the manifest; current binary location **not verified**. |
| Pre-DPM case | `C:\Users\qtra338\Documents\enthalpy_sweep_verified_20260721_v2\case_4_1600_1500_flow.cas.h5` | Historical path only; binary absent from the Mac result mirror. |
| Pre-DPM data | `C:\Users\qtra338\Documents\enthalpy_sweep_verified_20260721_v2\case_4_1600_1500_flow.dat.h5` | Historical path only; binary absent from the Mac result mirror. |
| Post-DPM case | `C:\Users\qtra338\Documents\enthalpy_sweep_verified_20260721_v2\case_4_1600_1500.cas.h5` | Historical path only; binary absent from the Mac result mirror. |
| Post-DPM data | `C:\Users\qtra338\Documents\enthalpy_sweep_verified_20260721_v2\case_4_1600_1500.dat.h5` | Historical path only; binary absent from the Mac result mirror. |
| Accepted run manifest | Same folder, `case_4_1600_manifest.json` | `/Users/andy/Desktop/P4P/P4P_knowledgeWiki/PyAnsys/output/enthalpy_sweep_verified_20260721_v2/case_4_1600_manifest.json`; present. SHA-256 `65473b5ebc8e1b4ac9c287aa55ba94d78cfbf8854fc9126dcf303539ed8b8db6`. |
| Pre-DPM flow manifest | Same folder, `case_4_1600_flow_manifest.json` | Same Mac result folder; present. SHA-256 `2199935682a69fd4ea25ebb911a3767ed054775f34521a2580754ea6cafe7383`. |
| DPM report | Same folder, `case_4_1600_dpm_report.txt` | Same Mac result folder; present. SHA-256 `493d625917645c3a02261f69f55f0b3fe3f5ced9af2c7a1d946369720f7f869c`. |
| Injection results | Same folder, `case_4_1600_injection_results.csv` | Same Mac result folder; present. SHA-256 `0407cf4241ed3b9dfd618db80ccc95dfdc11d1d84b5d0e1136c54d07dc2ed55d`. |
| Residual history | Manifest says `case_4_1600_1500_residual_history.csv`; actual mirror file is `case_4_1600_1500iter_residual_history.csv` | Same Mac result folder; present. SHA-256 `f85d1a99f3530223c60e9d6a903d5bc62e4f018b1f433101363cad2a71bec881`. |
| Complete execution log | Not recorded as a Windows output path | `/Users/andy/Desktop/P4P/P4P_knowledgeWiki/PyAnsys/output/enthalpy_sweep_verified_20260721_v2/logs/case4_full_1500_15proc.log`; present. |

The accepted execution log identifies Fluent 2024 R2, 15 parallel ranks, and a loaded tetrahedral mesh of 5,578,299 cells. Its boundary zones were `wall-fluid` (wall), `inlet` (mass-flow inlet), `steam_outlet` (pressure outlet), and `fluid_outlet` (wall).

### Runner and injection source

| Artifact | Current location | Qualification |
| --- | --- | --- |
| PyFluent runner | `/Users/andy/Desktop/P4P/P4P_knowledgeWiki/PyAnsys/scripts/setup/run_purnanto_enthalpy_sweep.py` | Present; SHA-256 `2b6e62d26587d5a4e930bc90ce8886b933e33f0b637f8ef973db677cf698b9c8`. It was modified after the 2026-07-23 accepted run, so it is the maintained descendant, **not proven byte-identical to the executed script**. |
| Original droplet table | `/Users/andy/Desktop/P4P/Code/harwell_results.csv` | Present; SHA-256 `688d12c73b755ba3bffa872bae0ff78e23561b7588f376e91c0e502ede427e9f`. |
| Preserved baseline Case 4 rows | `../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-M04/historical-baseline-harwell.csv` | Current shared copy. |
| Machine-readable Case 4 targets | `../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-M04/baseline-case4-injection-targets.json` | Current shared extraction. |
| Recovered original carrier export | `../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/original-case-setup-52660.json` | Present; exact recovered one-inlet setup lineage, SHA-256 `6571bbd71b617da865c61e935a639f4a0cdb8de437b8609b7426a9d3ef8f4c37`. Not a direct full export from accepted `baseline.cas.h5`. |

The exact command line used on 2026-07-23 was not preserved. The log establishes the executed order:

1. Read `baseline.cas.h5` fresh.
2. Set and read back the two phase mass flows.
3. Set and read back all nine DPM injections **before carrier initialization and iteration**.
4. Hybrid initialize.
5. Run 1,500 carrier iterations in verified 25-iteration blocks, without residual-based early stopping.
6. Save the pre-DPM case/data pair.
7. Execute `/solve/dpm-update` and collect DPM reports.
8. Save the post-DPM case/data pair.

### Current PC archive: related but not the accepted endpoint

Known archive root:

`C:/Users/qtra338/P4P/experiments/parallel-andy-studies/enthalpy-dpm-replication`

| File | Current status |
| --- | --- |
| `baseline/enthalpy_sweep/case_4_1600_1500.cas.h5` | Located by read-only native file index; 186,655,419 bytes. **Candidate only.** |
| `baseline/enthalpy_sweep/case_4_1600_1500.dat.h5` | Located by read-only native file index; 1,331,330,588 bytes. **Candidate only.** |
| Adjacent archive manifest/results | Older baseline run: approximately 2.005 kg/s escaped, 32.23 kg/s trapped, and 82.68 kg/s incomplete. This does not match accepted verified-v2 Case 4. |
| Archive guide | Says this archive is the baseline six-condition sweep and that the July spiral sweep was not identified. Preserved at `../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-M04/raw/archive-README.md`. |
| `case_4_1600_dpm_maxsteps_100000_stepfactor_10_*` | Later diagnostic. It must not be treated as the original accepted tracking configuration. |

Before using the archive binary, inspect it read-only and compare settings, zone roles, injection objects, iteration state, and adjacent evidence to the accepted manifests. A filename match alone is insufficient.

### Family discrimination

| Attribute | Intended baseline Case 4 | Later spiral Case 4 |
| --- | --- | --- |
| Parent | `baseline.cas.h5` | `baseline_spiral_inlet.cas.h5` |
| Accepted result folder | `enthalpy_sweep_verified_20260721_v2` | `spiral_enthalpy_sweep_20260725` |
| Droplet diameters | 4.307 to 1,249.17 micrometres; table below | 5.621 to 1,630.195 micrometres |
| Injection speed | 34.221202 m/s face-normal | 26.865069 m/s face-normal |
| Particle material | `water-liquid-dpm` | Recorded as `liquid-water` |
| Reported trapped boundary | `fluid_outlet`, zone 8, which was a wall in the baseline log | Different spiral boundary topology |
| Archive status | Baseline family found, accepted endpoint still unresolved | July spiral sweep explicitly not identified |

## 2. Carrier settings

### Direct accepted-run settings

| Item | Exact accepted-run evidence |
| --- | --- |
| Software | Ansys Fluent 2024 R2. |
| Carrier phase assignment | `phase-1` = steam/gas; `phase-2` = liquid water. |
| Inlet | `inlet`, mass-flow inlet, direction normal to boundary, absolute reference frame. |
| Steam flow | `phase-1 = 80.69 kg/s`. |
| Liquid flow | `phase-2 = 116.92 kg/s`. |
| Total flow | `197.61 kg/s`. |
| Inlet pressure field | 1,140,000 Pa stored as `supersonic_gauge_pressure`. With operating pressure 0 Pa in the lineage export, gauge and absolute numeric values coincide; verify the accepted binary before relying on that convention. |
| Inlet turbulence | Intensity and hydraulic diameter; intensity `0.02152499951888` = 2.1525%; diameter `0.7240000000000001 m`. |
| Inlet DPM fate | Escape. |
| Initialization | Hybrid initialization; the log says constant pressure was used because boundary pressure information was unavailable to the initializer. |
| Iteration horizon | 1,500 carrier iterations, verified from the residual monitor x-axis. All residual convergence-stop flags were false. |
| Accepted mesh topology | 5,578,299 tetrahedral cells; one cell zone; five face zones. |
| Accepted boundary types | `wall-fluid`: wall; `inlet`: mass-flow inlet; `steam_outlet`: pressure outlet; `fluid_outlet`: wall. |

### Exact recovered carrier lineage requiring source-case confirmation

These values are from `original-case-setup-52660.json`. They are the most complete exact export of the original one-inlet Purnanto carrier setup and are consistent with the documented setup lineage, but the accepted July Case 4 manifest has `physics_readback: null`. Therefore they are **not direct proof of every setting in the accepted 5.58-million-cell `baseline.cas.h5`**.

| Category | Recovered exact setting | Evidence status |
| --- | --- | --- |
| Solver | Pressure-based; steady; absolute velocity formulation | Lineage |
| Multiphase | Mixture model; two carrier phases | Lineage |
| Energy | Off | Lineage |
| Turbulence | RNG k-epsilon; standard wall functions; RNG differential-viscosity model enabled; swirl-dominated flow enabled | Lineage |
| Phase 1 material | `water-vapor-at-psep`; density `5.7974339 kg/m^3`; dynamic viscosity `1.52062e-05 Pa s` | Lineage |
| Phase 2 material | `water-liquid-at-psep`; density `881.21088 kg/m^3`; dynamic viscosity `0.000145544 Pa s` | Lineage |
| Gravity | Enabled, vector `(0, -9.81, 0) m/s^2` | Lineage |
| Operating pressure | `0 Pa`; operating density method `mixture-averaged` | Lineage |
| Outlet pressure | `1,120,000 Pa` in recovered original one-outlet setup; backflow direction normal, pressure specification total, turbulence intensity 2.1525%, hydraulic diameter 0.724 m, phase-2 backflow volume fraction 0 | Lineage; accepted baseline has separate `steam_outlet` and wall `fluid_outlet`, so audit required |
| Walls | Recovered `bottom` and `wall-fluid`: stationary, no-slip, roughness height 0, roughness constant 0.5; DPM reflect with normal and tangential restitution coefficients 1 | Lineage; accepted zone mapping differs |
| Pressure-velocity coupling | SIMPLE | Lineage |
| Gradient | Green-Gauss node-based | Lineage |
| Pressure interpolation | PRESTO! | Lineage |
| Momentum | Second-order upwind | Lineage |
| Turbulent kinetic energy | Second-order upwind | Lineage |
| Turbulent dissipation rate | Second-order upwind | Lineage |
| Volume fraction | QUICK | Lineage |
| Pseudo-time | Off | Lineage |
| High-order term relaxation | Off | Lineage |
| Pressure URF | 0.3 | Lineage |
| Momentum URF | 0.7 | Lineage |
| Density URF | 1.0 | Lineage |
| Body-force URF | 1.0 | Lineage |
| Drift/slip velocity URF | 0.1 | Lineage |
| Volume-fraction URF | `0.40000000596` | Lineage |
| Turbulent kinetic energy URF | 0.8 | Lineage |
| Turbulent dissipation URF | 0.8 | Lineage |
| Turbulent viscosity URF | 1.0 | Lineage |
| Implicit body force | False in both the multiphase and expert setting fields | Lineage |
| Residual criteria | Continuity `1e-4`; x/y/z velocity, k, epsilon, and volume fraction `1e-3` | Lineage; accepted run disabled convergence-based stopping |

### M04 topology is not a name-for-name match

The selected target mesh is currently recorded as:

`C:/Users/qtra338/P4P/experiments/phase 10/Separator-purnanto-single-947k.msh.h5`

with 946,967 cells. The M04 mesh family contains names including `inlet`, `steamoutlet`, `bottom`, `wall`, `vessel-wall-wall-separator-purnanto`, and inlet-wall zones. The historical accepted baseline instead used `inlet`, `steam_outlet`, `fluid_outlet`, and `wall-fluid`.

The following are only **candidate physical-role mappings** and must be verified geometrically before mutation:

| Historical role | M04 candidate | Required check |
| --- | --- | --- |
| `inlet` injection and carrier inlet | `inlet` | Confirm face orientation and area; face-normal positive magnitude must point into the vessel. |
| `steam_outlet` pressure outlet and DPM escape | `steamoutlet` | Confirm this is the top steam outlet. |
| `fluid_outlet` wall with DPM trap | `bottom` | Confirm the historical closed lower-liquid boundary is physically represented by this surface. Do not convert a pressure outlet or assume a trap fate. |
| `wall-fluid` carrier wall | Vessel and inlet wall zones | Confirm every wall fate and restitution setting individually. |

The current Phase 10 carrier-only case has no active injections and is not, by itself, proof of the historical DPM configuration.

## 3. DPM configuration

### Directly verified injection definitions

All nine accepted injections were set before carrier initialization and iteration. Each was a uniform-diameter surface injection on `inlet`, in the global/absolute frame, with inert particle type and material `water-liquid-dpm`. Position randomization was disabled. Velocity used the **face-normal option with positive magnitude 34.221202 m/s**. The source CSV's `z_velocity_ms = -34.221202` records the historical Cartesian direction; it was not entered as a negative magnitude when face-normal mode was active.

| Fluent name | Diameter, m | Diameter, mm | Represented liquid mass flow, kg/s | Surface | Speed/mode |
| --- | ---: | ---: | ---: | --- | --- |
| `injection-0` | `4.307482e-06` | 0.004307 | 0.189995 | `inlet` | 34.221202 m/s, face-normal |
| `injection-1` | `2.153741e-05` | 0.021537 | 0.780441 | `inlet` | 34.221202 m/s, face-normal |
| `injection-2` | `4.307482e-05` | 0.043075 | 0.970436 | `inlet` | 34.221202 m/s, face-normal |
| `injection-3` | `8.614965e-05` | 0.086150 | 1.952564 | `inlet` | 34.221202 m/s, face-normal |
| `injection-4` | `1.292245e-04` | 0.129224 | 1.952564 | `inlet` | 34.221202 m/s, face-normal |
| `injection-5` | `2.670639e-04` | 0.267064 | 23.384000 | `inlet` | 34.221202 m/s, face-normal |
| `injection-6` | `4.307482e-04` | 0.430748 | 29.230000 | `inlet` | 34.221202 m/s, face-normal |
| `injection-7` | `6.461224e-04` | 0.646122 | 29.230000 | `inlet` | 34.221202 m/s, face-normal |
| `injection-8` | `1.249170e-03` | 1.249170 | 29.230000 | `inlet` | 34.221202 m/s, face-normal |
| **Total** |  |  | **116.920000** |  |  |

The represented DPM liquid total equals the full Eulerian phase-2 inlet flow. This historical workflow used DPM as a post-processed droplet-routing calculation after solving the carrier field; it did not establish a physically conservative Eulerian/DPM mass partition.

### Per-injection particle physics readback

| Setting | Accepted-run readback |
| --- | --- |
| Particle type | Inert |
| Material | `water-liquid-dpm` |
| Injection type | Surface |
| Diameter distribution | Uniform; diameter listed above |
| Reference frame | Global |
| Drag law | Spherical |
| Turbulent dispersion | False at the injection physics level |
| Particle rotation | False |
| Rough-wall treatment | False |
| Law 1 | Inert heating |
| Laws 2-10 | Inactive |

### Global tracking and boundary controls

| Item | Evidence-backed status |
| --- | --- |
| Carrier-particle coupling | The study was intended and described as one-way/post-carrier DPM. The accepted manifest does not contain a global coupling readback, so the exact switch state is **missing** and must be audited in a source case. |
| Stochastic tracking | Injection-level turbulent dispersion is directly false. The complete global stochastic-tracking panel was not exported; do not infer additional switches. |
| Maximum tracking steps | **Missing for the accepted verified-v2 run.** An older archive diagnostic observed 100,000, but that belongs to a later `dpm_maxsteps_100000_stepfactor_10` test and is not transferable. |
| Step-length factor | **Missing for the accepted verified-v2 run.** Older baseline diagnostics used factors 5 and then 10; neither is proven to be the accepted run's original value. |
| High-resolution tracking | **Missing.** A historical attempt to set/read it did not produce accepted readback. |
| Number of tries / accuracy controls | **Missing.** |
| DPM update sequence | One `/solve/dpm-update` after the 1,500 carrier iterations. |
| `inlet` particle fate | Escape; direct accepted inlet readback. |
| `steam_outlet` particle fate | Escape; direct accepted report, zone 7. |
| `fluid_outlet` particle fate | Trap; direct accepted report, zone 8; carrier log identifies this zone as a wall. |
| `wall-fluid` particle fate | **Not directly preserved in accepted artifacts.** Recovered carrier lineage used reflect with unit normal/tangential restitution, but source-case audit is required. |
| Other M04 wall fates | **Missing until mapped and explicitly read back.** Do not copy a default across all walls. |

There is no complete accepted-run DPM settings export. The injection CSV and manifest fully determine the nine injection objects, but not every global tracking control or every wall fate. Those missing fields are hard preflight items, not permission to use defaults.

## 4. Accepted original results and limitations

### Carrier residual endpoint

| Residual at iteration 1,500 | Value |
| --- | ---: |
| Continuity | 0.2225296536719666 |
| x-velocity | `2.102728962838448e-05` |
| y-velocity | `2.644855681573683e-05` |
| z-velocity | `2.168404325855329e-05` |
| k | 0.001019249442567281 |
| epsilon | 0.005885342871642469 |
| Phase-2 volume fraction | 0.001080153361726167 |

At the final iteration the log also reported turbulent-viscosity limiting in 803 cells and reversed flow on 799 pressure-outlet faces. The fixed 1,500-iteration horizon completed, but the continuity residual was high and the run was not demonstrated to be converged.

### DPM fate totals

| Fate | Parcels/streams | Mass flow, kg/s | Fraction of 116.92 kg/s injected DPM |
| --- | ---: | ---: | ---: |
| Escaped through `steam_outlet` | 8,318 | 0.1817 | 0.155405% |
| Trapped at `fluid_outlet` | 36,268 | 63.24 | 54.0883% |
| Incomplete | 33,714 | 53.50 | 45.7578% |
| **Reported total** | **78,300** | **116.9217** | **100.001454%** |

The 0.0017 kg/s excess over the prescribed injection total is report rounding; the runner's per-injection reconciliation passed its 0.2% tolerance.

| Injection | Escaped, kg/s | Trapped, kg/s | Incomplete, kg/s |
| --- | ---: | ---: | ---: |
| `injection-0` | 0.1817 | 0.00832 | 0.00002184 |
| `injection-1` | 0 | 0.3682 | 0.4123 |
| `injection-2` | 0 | 0.4680 | 0.5024 |
| `injection-3` | 0 | 0.9662 | 0.9864 |
| `injection-4` | 0 | 0.9839 | 0.9687 |
| `injection-5` | 0 | 12.18 | 11.20 |
| `injection-6` | 0 | 15.60 | 13.63 |
| `injection-7` | 0 | 15.95 | 13.28 |
| `injection-8` | 0 | 16.72 | 12.51 |

### Historical steam-quality calculation

The script treated only DPM liquid confirmed as escaped through the steam outlet as outlet moisture:

`steam quality = 100 * steam flow / (steam flow + escaped DPM liquid)`

`= 100 * 80.69 / (80.69 + 0.1817)`

`= 99.7753231353%`

This is a DPM carryover-derived metric, not a demonstrated thermodynamic equilibrium steam quality. The 53.50 kg/s incomplete DPM mass was kept separate and not assigned to either escaped or trapped. Because incomplete mass is 45.76% of the injected DPM, the quality result is strongly limited by tracking completion.

### Scientific limitations that must accompany any comparison

| Limitation | Consequence |
| --- | --- |
| Continuity residual remained about 0.223 | The carrier solution was not numerically converged by residual evidence. |
| No accepted carrier inlet/outlet mass-flow closure export | Carrier conservation cannot be claimed from the July artifacts. |
| No accepted liquid-inventory history | A bounded or steady liquid inventory was not demonstrated. |
| `fluid_outlet` was a trapping wall, not a resolved liquid outlet | The historical physics intentionally accumulated/routed liquid without a physical brine discharge. |
| 45.76% of DPM mass was incomplete | DPM carryover is not fully resolved; escaped mass is a lower-confidence routing result. |
| DPM mass duplicates the full Eulerian liquid inlet in a post-carrier calculation | The historical setup is a replication target, not a conservative coupled phase-partition model. |
| Fixed 1,500 iterations | Horizon completion is execution evidence, not convergence. |
| Different source and target meshes/topologies | M04 agreement or disagreement cannot be attributed to mesh alone until boundary roles and all inherited settings are matched and read back. |

## Replication preflight for the next chat

Do not start M04 until the following read-only questions are closed:

| Gate | Required evidence |
| --- | --- |
| Accepted parent identity | Locate the verified-v2 binary pair, or prove an archive candidate is equivalent using hashes/settings/iteration and DPM readback. |
| Direct accepted carrier export | Read back models, phase materials/properties, all BCs, walls, operating conditions, methods, controls, and initialization without solving. Reconcile against the lineage table above. |
| Complete DPM export | Read back global coupling, stochastic controls, max steps, step-length factor, accuracy/high-resolution controls, every injection, and every boundary fate. |
| M04 role map | Geometrically map each historical boundary role to M04 and record area, normal orientation, carrier type, and DPM fate. |
| Injection direction | Confirm that positive face-normal 34.221202 m/s points into the M04 vessel. |
| Material availability | Confirm `water-liquid-dpm` exists with the intended properties; do not substitute the spiral `liquid-water` identity. |
| Iteration semantics | Fresh hybrid initialization, 1,500 verified carrier updates, pre-DPM save, then one DPM update/report, unless a new predeclared numerical stop prevents the run. |
| Comparison evidence | Preserve residual histories, carrier phase flux closure, liquid inventory/window change, all DPM fates, and saved/reopened settings. Report the M04 result separately from the historically unqualified reference. |

Until those gates close, the exact nine injection definitions and the full-flow operating point are ready, but **exact historical settings parity is not yet established**.

