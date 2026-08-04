# Split-Inlet Carrier-Field Mesh-Convergence Study: Technical Handoff

**Study ID:** `split_inlet_mesh_convergence_20260801`  
**Snapshot:** 3 August 2026, approximately 13:10 NZST  
**Repository:** `/Users/andy/Desktop/P4P/P4P_knowledgeWiki`  
**Evidence status:** preflight `accepted`; six meshes completed as `diagnostic / unresolved`; seventh mesh running  
**Intended reader:** project partner or a new Codex task continuing the work

## Technical summary

This is the carrier-field mesh-resolution study for the post-replication spiral/split-inlet geothermal separator. It is not another Purnanto enthalpy sweep and it does not run DPM or Eulerian Wall Film. Seven tetrahedral meshes have been preflighted in Fluent 2024 R2 with the same geometry roles, physics, boundary conditions, numerical methods, initialization procedure, processor count, monitor definitions, and setup fingerprint. Only mesh resolution changes.

At this snapshot, `mesh-300k`, `mesh-600k`, `mesh-900k`, `mesh-1600k`, `mesh-1900k`, and `mesh-2000k` have completed their formal 3000-iteration endpoints and saved case/data checkpoints. `mesh-2300k` has 1250/3000 iterations recorded; the controller output was later observed near iteration 1382. Recorded study progress is 19,250/21,000 iterations (91.7%).

The study does **not yet demonstrate mesh independence**. Steam-outlet vapor flow is exceptionally stable between completed meshes, but pressure drop, outlet velocity, and domain-averaged velocity remain iteration-dependent. The completed meshes have final-500 pressure-drop drift of 2.46-9.65%, compared with the proposed 0.5% iteration-independence criterion. Fine-grid pressure drop is close between 1900k and 2000k (0.51% difference), but that adjacent-grid change is smaller than the within-run pressure drift, so it cannot yet be interpreted as physical mesh independence. Continuity residuals remain high (approximately 0.05-0.25 at the completed endpoints), although momentum, turbulence, and volume-fraction residuals are much lower.

The project owner has confirmed that the nearly 100% liquid imbalance is an expected consequence of the chosen closed-bottom geometry: `bottom` is intentionally a wall and `steamoutlet` is the only outlet. Therefore liquid balance is not being used as a rejection gate for this geometry. Nevertheless, steam quality and Eulerian liquid carryover remain trend-only metrics, and the continuing pressure/velocity drift must still be resolved or explicitly accepted as a quasi-steady limitation.

## Study scope and decisions already made

### Included

- Steady carrier-field calculation using the Fluent Mixture model.
- Two Eulerian phases: vapor primary and liquid secondary.
- Reference operating condition corresponding approximately to Purnanto Case 4 at `1600 kJ/kg`.
- Liquid inlet flow `116.92 kg/s` and steam inlet flow `80.69 kg/s`.
- Seven systematically ordered mesh files.
- Fresh hybrid initialization for every new formal mesh.
- Exactly 3000 formal iterations per mesh, executed in 250-iteration blocks.
- Initialized, 1000-, 2000-, and 3000-iteration case/data checkpoints.
- Residual, physical-monitor, mass-balance, surface, mesh-quality, transcript, readback, and manifest evidence.

### Excluded

- No DPM injection update, tracking, or particle-fate calculation.
- No two-way DPM interaction.
- No Eulerian Wall Film.
- No enthalpy sweep, flow-rate sweep, or DPM sensitivity calculation.
- No geometry or boundary-condition change between meshes.
- No claim that reaching 3000 iterations alone establishes convergence.

### Geometry-specific interpretation agreed with the owner

`bottom` is a stationary no-slip wall, not an outlet. The geometry therefore has no dedicated liquid discharge. The owner considers the resulting liquid imbalance an intentional limitation of the model rather than an implementation error. Reports must preserve that statement and must not silently change `bottom` into an outlet. Carrier liquid flow at `steamoutlet` and computed steam quality can be compared as trends, but they must not be presented as validated separator efficiency.

## Authoritative execution baseline

The authoritative setup actually executed in this study is the combination of:

```text
C:\Users\qtra338\Documents\Mesh study\partial_solution_diagnostic_20260801.cas.h5
C:\Users\qtra338\Documents\Mesh study\Source\mesh_study_settings.set
```

The partial solution was preserved as diagnostic evidence. Formal mesh runs did not continue that field; each new mesh was initialized afresh. The settings file is the setup-07a execution authority. Its complete Fluent readback is preserved independently for every mesh. The accepted critical-settings fingerprint is:

```text
424a9bf02bbd78060dee3a2874103e5149aa4aa555a09e2add69da4d2a0158c5
```

The historical setup-07 archive case `FFF.1-2.cas.h5` remains useful lineage evidence for the split-inlet geometry, but it is **not** the numerical authority for this production study. That archive had conflicting live numerics and active DPM. Likewise, setup 08c is a sibling one-inlet spiral/DPM study, not the branch being converged here.

The current repository setup page, [`07a-split-inlet-carrier-mesh-convergence.md`](../../../Setup%20report/07a-split-inlet-carrier-mesh-convergence.md), still contains the older planned/blocked wording and three-mesh proposal. It must be updated after the active run and final analysis finish. A future Codex must treat the machine-readable evidence in this output directory as the current execution truth.

## Verified geometry and zone contract

All seven meshes contain one fluid cell zone and the required face zones:

| Role | Fluent zone | Required type | Verified state |
|---|---|---|---|
| Liquid inlet strip | `liquidinlet` | mass-flow inlet | accepted |
| Steam inlet core | `steaminlet` | mass-flow inlet | accepted |
| Steam outlet | `steamoutlet` | pressure outlet | accepted |
| Closed separator bottom | `bottom` | wall | accepted |
| Separator walls | `wall-fluid` | wall | accepted |
| Fluid volume | `fluid` | fluid cell zone | accepted |

The split-inlet representation is supported by stable areas and centroids across the mesh ladder:

- `liquidinlet` area: `0.004889896 m²` on every mesh.
- `steaminlet` area: `0.5192861 m²` on every mesh.
- Both inlet centroids have `x = -3.1108417 m` and `y = -4.395 m`.
- Liquid and steam centroid `z` coordinates are `-1.4575183 m` and `-1.0955183 m`, respectively, proving they are distinct parts of the inlet face.
- Fluid-domain volume varies only from `22.65670` to `22.65891 m³` across the ladder.
- `steamoutlet` area varies from `0.6007393` to `0.6023680 m²`; this small discretization-related change should remain visible in the uncertainty discussion.

The settings import prints messages such as `No zone with name wall ... skipped`. These are benign references to an unused generic zone named `wall`. They are not missing-zone failures: `bottom` and `wall-fluid` are both read back as walls after settings application. The automation stops on missing or ambiguous mappings of any required role.

## Frozen Fluent setup used on every mesh

### Solver and operating conditions

- Fluent: Ansys Fluent 2024 R2.
- Pressure-based solver, absolute velocity formulation.
- Steady calculation.
- Gravity enabled: `(0, -9.81, 0) m/s²`.
- Operating pressure: `0 Pa`.
- Energy equation: off.
- Sixteen active partitions/processes.

### Multiphase and materials

- Multiphase family: Mixture.
- Number of phases: 2.
- Primary `phase-1`: `water-vapor-at-psep`, density `5.7974339 kg/m³`.
- Secondary `phase-2`: `water-liquid-at-psep`, density `881.21088 kg/m³`.
- DPM interaction: disabled.

### Turbulence

- RNG `k-epsilon`.
- Differential viscosity model: enabled.
- Swirl-dominated flow option: enabled.
- Standard wall functions.

### Boundary conditions

- `liquidinlet`: liquid phase `116.92 kg/s`, vapor phase `0 kg/s`.
- `steaminlet`: vapor phase `80.69 kg/s`, liquid phase `0 kg/s`.
- Inlet turbulence intensity: `2.1099999%`.
- Liquid inlet hydraulic diameter: `0.01338 m`.
- Steam inlet hydraulic diameter: `0.72061 m`.
- `steamoutlet`: gauge pressure `1,120,000 Pa`; liquid backflow volume fraction `0`.
- Outlet turbulence hydraulic diameter: `0.876 m`.
- `bottom`: stationary, no-slip wall.
- `wall-fluid`: stationary, no-slip wall.

The DPM wall fields inherited in the case are irrelevant to this carrier-only calculation because DPM interaction is off and no injection/tracking call is made.

### Numerical methods and controls

- Pressure-velocity coupling: SIMPLE.
- Pressure discretization: PRESTO!.
- Momentum: second-order upwind.
- Turbulent kinetic energy: first-order upwind.
- Dissipation rate: second-order upwind.
- Multiphase/volume fraction: QUICK.
- Gradient: Green-Gauss node-based.
- Under-relaxation: pressure `0.3`, momentum `0.7`, `k`/epsilon `0.8`, multiphase `0.4`, drift `0.1`.
- Initialization: hybrid, ten initialization iterations.
- Automatic early convergence stopping was disabled for the formal 3000-iteration sequence so every mesh reached the same requested endpoint.

Residual criteria stored in the case are `1e-4` for continuity and `1e-3` for the remaining equations, but formal production did not stop early when these flags were met. This was deliberate: the controller records the full residual history and uses physical monitor stability as a separate criterion.

## Mesh ladder and preflight evidence

Filename labels are historical names, not actual cell counts. Actual characteristic size is calculated as

```text
h = (fluid-domain volume / cell count)^(1/3)
```

and refinement ratio is `r = h_coarser / h_finer`.

| Mesh | Actual cells | h (m) | r from previous | Min. orthogonal quality | Max. aspect ratio | Volume (m³) |
|---|---:|---:|---:|---:|---:|---:|
| 300k | 1,688,678 | 0.0237620 | — | 0.200732 | 20.3226 | 22.65670 |
| 600k | 3,609,102 | 0.0184476 | 1.28808 | 0.191653 | 18.4352 | 22.65799 |
| 900k | 5,335,623 | 0.0161938 | 1.13918 | 0.202194 | 20.1267 | 22.65842 |
| 1600k | 9,720,194 | 0.0132593 | 1.22132 | 0.200348 | 19.5466 | 22.65877 |
| 1900k | 10,756,635 | 0.0128190 | 1.03435 | 0.200177 | 18.7413 | 22.65884 |
| 2000k | 11,959,759 | 0.0123739 | 1.03597 | 0.198112 | 17.8078 | 22.65888 |
| 2300k | 13,370,267 | 0.0119225 | 1.03786 | 0.200535 | 18.9096 | 22.65891 |

All mesh checks completed without negative-volume or mesh-check errors. Quality is similar across the ladder. The final fine-grid ratios are small (`1.034-1.038`), which gives close fine-grid comparisons but may make observed-order and GCI estimates sensitive to numerical noise and incomplete iteration convergence.

`mesh-stage2.msh` was recorded as a legacy alias. SHA-256 comparison proved it is byte-identical to `mesh-600k.msh`:

```text
0fd7a11174663306c7e79539a37683019f3b1643ec32d378b57c9b4a59a64b34
```

It is therefore excluded as a duplicate, not counted as an eighth mesh.

## Automation implemented

The following code was created for this study:

- [`run_split_inlet_mesh_convergence.py`](../../scripts/setup/run_split_inlet_mesh_convergence.py): primary preflight and production controller.
- [`resume_split_inlet_mesh_convergence.py`](../../scripts/setup/resume_split_inlet_mesh_convergence.py): recovery controller for the interrupted 1600k run and continuation through incomplete meshes.
- [`check_mesh_convergence_status.py`](../../scripts/connection/check_mesh_convergence_status.py): read-only local/live status tool.
- [`mesh_convergence.py`](../../src/pyansys_fluent/mesh_convergence.py): reusable parsing, zone resolution, stability, and generalized-GCI helpers.
- [`test_mesh_convergence.py`](../../tests/test_mesh_convergence.py): unit tests for zone mapping, settings parity helpers, monitor stability, generalized GCI, and failure handling.

The test suite currently passes eight tests:

```text
........
Ran 8 tests
OK
```

### Controller behavior

For each mesh, the controller:

1. Verifies remote input files and free disk space.
2. Reads the raw mesh and captures cell/face/node counts, domain volume, quality, areas, centroids, and partition count.
3. Resolves required zone roles, rejecting ambiguous or missing mappings.
4. Loads the preserved template case and replaces its mesh.
5. Applies `mesh_study_settings.set`.
6. Reads the complete setup back from Fluent.
7. Verifies the critical fingerprint against the accepted baseline.
8. Verifies DPM interaction remains off.
9. Hybrid-initializes the formal run.
10. Executes 3000 iterations in blocks of 250.
11. Captures residual and physical metrics after every block.
12. Saves case/data at initialized, 1000, 2000, and final 3000 endpoints.
13. Writes local JSON/CSV/text evidence and a remote transcript.

No PyFluent setter is trusted without a readback. Temporary reports use unique scratch filenames to avoid stale-data parsing. Early convergence stopping is disabled during the standardized 3000-iteration pass.

## Execution history and recovery

1. The existing live partial solution was inspected and saved as diagnostic evidence.
2. The original five meshes (300k, 600k, 1600k, 2000k, 2300k) passed preflight.
3. The 300k and 600k formal runs completed normally.
4. The controller connection dropped during the 1600k calculation. The local block manifest had recorded 500 iterations, while the transcript proved progress through at least iteration 663.
5. After reconnection, a recovery pair was saved as:

   ```text
   mesh-1600k_recovered_iter663.cas.h5
   mesh-1600k_recovered_iter663.dat.h5
   ```

6. The user added `mesh-900k.msh` and `mesh-1900k.msh`. Both were added to the canonical ladder and passed the same preflight/fingerprint checks.
7. The recovery controller loaded the saved 1600k pair without hybrid reinitialization, completed the run, skipped already completed 300k/600k, then ran 900k, 1900k, 2000k, and finally 2300k.

### 1600k iteration bookkeeping exception

The 1600k run manifest and physical-monitor history label the final endpoint as 3000, but its residual CSV ends at Fluent iteration 3087. Console evidence indicates the recovery sequence effectively introduced an 87-iteration offset. The final field therefore appears to contain 87 more solver iterations than the nominal endpoint. This is a `diagnostic / unresolved` bookkeeping exception. It does not improve the convergence classification because pressure was still drifting. If strict equal-iteration parity is required for publication, rerun 1600k cleanly from hybrid initialization.

The completed 1600k manifest still contains the original disconnect error string even though its status is `completed`; the status checker suppresses stale errors unless a manifest status is `failed`. Future cleanup should move that error into explicit recovery history rather than leaving it as a top-level active error.

## Current execution status

| Mesh | State | Recorded iterations | Checkpoints present | Classification |
|---|---|---:|---|---|
| 300k | completed | 3000 | initialized, 1000, 2000, 3000 | unresolved |
| 600k | completed | 3000 | initialized, 1000, 2000, 3000 | unresolved |
| 900k | completed | 3000 | initialized, 1000, 2000, 3000 | unresolved |
| 1600k | completed after recovery | 3000 labelled; residual history to 3087 | initialized, recovery 663, 1000, 2000, 3000 | unresolved |
| 1900k | completed | 3000 | initialized, 1000, 2000, 3000 | unresolved |
| 2000k | completed | 3000 | initialized, 1000, 2000, 3000 | unresolved |
| 2300k | running | 1250 recorded; controller later observed near 1382 | initialized, 1000 | not yet classified |

Recorded total at the snapshot is `19,250 / 21,000` iterations. Fluent remained connected and the controller process was active. No DPM calculation was running.

## Completed endpoint results

Fluent reports outflow with a negative sign. The table preserves the signed values; compare magnitudes when calculating percentage changes.

| Mesh | Pressure drop (kPa) | Vapor at steam outlet (kg/s) | Liquid at steam outlet (kg/s) | Carrier quality, trend only (%) | Outlet velocity (m/s) | Domain velocity (m/s) | Domain vorticity (1/s) |
|---|---:|---:|---:|---:|---:|---:|---:|
| 300k | 31.0510 | -81.488642 | -0.84725781 | 98.970974 | 51.08266 | 32.85721 | 68.88294 |
| 600k | 29.0005 | -81.445409 | -0.01250556 | 99.984648 | 47.78058 | 32.12963 | 77.79892 |
| 900k | 27.6593 | -81.447366 | -0.00007952 | 99.999902 | 46.23508 | 30.81236 | 82.39088 |
| 1600k | 25.2610 | -81.461226 | -0.00008392 | 99.999897 | 43.04686 | 28.14025 | 85.84952 |
| 1900k | 24.0141 | -81.466425 | -0.00001114 | ~100.000000 | 44.14708 | 26.91599 | 86.00685 |
| 2000k | 24.1355 | -81.462457 | -0.00003356 | ~100.000000 | 42.55820 | 26.48653 | 86.89046 |

### Interpretation of completed endpoints

- Vapor outlet flow is highly stable: every completed value is approximately `81.45 kg/s` in magnitude.
- Pressure drop decreases from 31.05 kPa on the coarsest mesh to approximately 24.0 kPa on the fine meshes.
- Vorticity rises with refinement and appears to approach approximately `86-87 1/s`.
- Outlet and domain-averaged velocities have not formed a clean asymptotic sequence.
- Eulerian liquid outlet flow becomes extremely small on all meshes except 300k; percentage changes become ill-conditioned when the denominator is near zero.
- Carrier quality must remain labelled `trend only` because the closed-bottom geometry provides no liquid outlet.

## Iteration-independence evidence

The status tool calculates final-500 drift as `(max - min) / |mean|` using the saved 2500, 2750, and 3000 monitor points. Liquid carryover percentage drift is omitted below because its near-zero denominator makes relative percentages misleading.

| Mesh | Pressure-drop drift (%) | Vapor-flow drift (%) | Outlet-velocity drift (%) | Domain-velocity drift (%) | Vorticity drift (%) |
|---|---:|---:|---:|---:|---:|
| 300k | 4.377 | 0.0945 | 1.738 | 0.814 | 1.014 |
| 600k | 5.409 | 0.0497 | 0.658 | 4.373 | 0.526 |
| 900k | 9.650 | 0.0365 | 4.738 | 6.778 | 1.482 |
| 1600k | 8.164 | 0.0073 | 1.877 | 8.689 | 0.642 |
| 1900k | 2.693 | 0.0136 | 3.766 | 9.195 | 0.472 |
| 2000k | 2.456 | 0.0193 | 0.496 | 9.174 | 1.834 |

Proposed iteration-independence criteria were no more than 0.5% drift for primary monitors and no more than 1% for velocity/vorticity metrics. Vapor flow passes comfortably. Most pressure and velocity quantities fail. Vorticity is often close to the secondary criterion, but it is not uniformly stable.

The pressure change is real, not only a residual-plot interpretation. During the final 250 iterations, pressure drop increased by approximately 2.14% (300k), 1.88% (600k), 5.43% (900k), and 4.35% (1600k). Fine-mesh pressure drift improved but remained about 2.5-2.7% over the final 500 iterations.

## Residual evidence

| Mesh | Continuity | Maximum momentum residual | k | epsilon | Liquid volume fraction |
|---|---:|---:|---:|---:|---:|
| 300k | 0.05124 | 4.60e-6 | 1.41e-4 | 1.43e-3 | 4.22e-4 |
| 600k | 0.15054 | 1.45e-5 | 2.76e-4 | 1.14e-3 | 6.62e-4 |
| 900k | 0.18750 | 1.51e-5 | 2.59e-4 | 7.16e-4 | 7.83e-4 |
| 1600k | 0.21523 | 1.79e-5 | 2.98e-4 | 7.01e-4 | 7.47e-4 |
| 1900k | 0.24951 | 2.02e-5 | 3.48e-4 | 9.49e-4 | 7.75e-4 |
| 2000k | 0.23673 | 1.97e-5 | 3.06e-4 | 8.06e-4 | 6.69e-4 |

Momentum residuals are low, and the turbulence/volume-fraction equations are near or below `1e-3`. Continuity is high and generally plateaued or oscillatory. The calculations are numerically bounded rather than explosively divergent, but they are not conventionally converged steady solutions. Residuals alone cannot override the documented drift in pressure and velocity monitors.

## Adjacent-mesh sensitivity at the saved endpoints

| Comparison | Pressure drop (%) | Vapor outlet magnitude (%) | Outlet velocity (%) | Domain velocity (%) | Vorticity (%) |
|---|---:|---:|---:|---:|---:|
| 300k → 600k | -6.604 | -0.053 | -6.464 | -2.214 | +12.944 |
| 600k → 900k | -4.625 | +0.002 | -3.235 | -4.100 | +5.902 |
| 900k → 1600k | -8.671 | +0.017 | -6.896 | -8.672 | +4.198 |
| 1600k → 1900k | -4.936 | +0.006 | +2.556 | -4.351 | +0.183 |
| 1900k → 2000k | +0.506 | -0.005 | -3.599 | -1.596 | +1.027 |

The 1900k-to-2000k pressure difference is within the nominal 1% mesh criterion, but both solutions have approximately 2.5% pressure drift over their final 500 iterations. Therefore within-run uncertainty exceeds the apparent adjacent-grid difference. Pressure mesh independence cannot be claimed yet. Vapor flow is mesh-insensitive, while velocity metrics remain sensitive. Fine-grid vorticity is promising but not sufficient by itself.

## Richardson extrapolation and GCI status

Richardson extrapolation and Grid Convergence Index must not yet be reported as accepted results. They require:

- three successively refined meshes;
- actual characteristic-size ratios;
- a monotonic sequence for the quantity of interest;
- a usable observed order;
- iteration error materially smaller than grid-to-grid change.

Pressure is broadly monotonic through 1900k but reverses slightly at 2000k. More importantly, pressure iteration drift exceeds the fine-grid difference. Velocity sequences are not consistently monotonic. Fine refinement ratios are close to one, which amplifies sensitivity in observed-order estimates. The final analysis script may calculate diagnostic generalized-GCI values where mathematically possible, but the report must classify them as unresolved unless the iteration-stability condition is first addressed.

## Acceptance criteria and current classification

### Preflight

- Required zones and boundary types: **accepted**.
- Geometry signature: **accepted with small surface discretization variation recorded**.
- Mesh check and quality: **accepted**.
- Sixteen processors: **accepted**.
- Settings fingerprint parity: **accepted**.
- DPM off: **accepted**.

### Iteration independence

- Vapor outlet flow: **accepted as stable**.
- Pressure drop: **unresolved**.
- Outlet velocity: **unresolved**.
- Domain velocity: **unresolved**.
- Vorticity: **diagnostic / partly stable**.
- Residual convergence: **unresolved because continuity remains high**.

### Mesh independence

- Vapor outlet flow: **mesh-insensitive over completed meshes**, but it is heavily constrained by the imposed inlet flow and is not sufficient alone.
- Pressure drop: **not demonstrated**.
- Velocity/swirl field: **not demonstrated**.
- Liquid carryover/quality: **trend only by geometry decision**.
- Overall study: **diagnostic / mesh sensitivity unresolved** until the 2300k run and final analysis finish.

## Output locations and filenames

### Remote Fluent root

```text
C:\Users\qtra338\Documents\Mesh study\split_inlet_mesh_convergence_20260801
```

Each mesh has a remote subdirectory such as `mesh_2000k`. Standard case/data names are:

```text
mesh-<level>_initialized.cas.h5
mesh-<level>_initialized.dat.h5
mesh-<level>_checkpoint_1000.cas.h5
mesh-<level>_checkpoint_1000.dat.h5
mesh-<level>_checkpoint_2000.cas.h5
mesh-<level>_checkpoint_2000.dat.h5
mesh-<level>_iter3000_final.cas.h5
mesh-<level>_iter3000_final.dat.h5
```

The 1600k directory additionally contains the recovery pair labelled `recovered_iter663`.

### Local evidence root

```text
PyAnsys/output/split_inlet_mesh_convergence_20260801
```

Important cross-study files:

- [`preflight_manifest.json`](preflight_manifest.json)
- [`environment_preflight.json`](environment_preflight.json)
- [`mesh_matrix.csv`](mesh_matrix.csv)
- [`study_manifest.json`](study_manifest.json)
- [`current_partial_diagnostic_manifest.json`](current_partial_diagnostic_manifest.json)

Per-mesh evidence pattern:

```text
mesh_<level>/mesh-<level>_preflight.json
mesh_<level>/mesh-<level>_settings_readback.json
mesh_<level>/mesh-<level>_mesh_quality.txt
mesh_<level>/mesh-<level>_metrics.json
mesh_<level>/mesh-<level>_run_manifest.json
mesh_<level>/mesh-<level>_residual_history.csv
mesh_<level>/mesh-<level>_physical_monitor_history.csv
mesh_<level>/mesh-<level>_mass_balance_history.csv
mesh_<level>/mesh-<level>_surface_metrics.csv
```

Transcripts and large case/data files remain on the Windows Fluent host; local manifests hold their exact remote paths.

## How to check or continue the work

From `PyAnsys`:

```bash
.venv/bin/python scripts/connection/check_mesh_convergence_status.py
```

Machine-readable status:

```bash
.venv/bin/python scripts/connection/check_mesh_convergence_status.py --json
```

Read-only live Fluent status may be requested with:

```bash
.venv/bin/python scripts/connection/check_mesh_convergence_status.py --live
```

During an active `iterate` RPC, a second live PyFluent connection may block until Fluent returns control. The local manifest status remains safe and read-only. Do not terminate the production controller merely because a second live check is slow.

Run the unit tests with:

```bash
.venv/bin/python -m unittest tests/test_mesh_convergence.py
```

### Queued 2300k iteration extension

On 2026-08-03, a separate diagnostic extension was queued behind the active
2300k recovery controller. The formal controller is replaying the valid 2000
checkpoint through the required 3000 endpoint. Once it exits successfully, the
queued controller will load `mesh-2300k_iter3000_final.cas.h5` and its matching
data file, without initialization, and continue the same carrier solution to
6000 iterations. It will save extension checkpoints at 4000, 5000, and 6000.
No DPM injections are enabled or run.

The extension is deliberately separate from the formal mesh-study evidence:

```text
mesh_2300k/extension_3000_6000/
```

Its controller is:

```text
scripts/setup/extend_split_inlet_mesh_iteration_run.py
```

The normal status command now reports the extension as queued, running,
completed, or failed. Extension results are classified `diagnostic`; their
separate iteration-independence decision is `accepted` only when final-500
primary-monitor drift is at most 0.5% and secondary-monitor drift is at most
1.0%. The accepted-by-owner closed-bottom mass imbalance is reported but is not
used to decide this diagnostic continuation.

Do **not** blindly relaunch `resume_split_inlet_mesh_convergence.py` while the current controller is active. First check the local manifest, inspect the controller process/output, verify Fluent health, and confirm the latest remote checkpoint. Starting a second mutation controller against the same Fluent session risks duplicate iteration and mislabeled checkpoints.

The gRPC client prints a warning that the connection is insecure because TLS is not enabled. This is a transport-security warning, not a numerical Fluent warning, and it does not alter the CFD solution. Credentials must not be copied into documentation.

## Recommended next actions

1. Allow `mesh-2300k` to reach its formal 3000 endpoint.
2. Verify its final `.cas.h5` and `.dat.h5` checkpoint entries in the run manifest.
3. Freeze a final status snapshot and ensure all seven residual/physical CSVs are present.
4. Produce combined convergence tables and plots from the local CSVs.
5. Recalculate adjacent percentage changes including 2300k.
6. Attempt generalized Richardson/GCI only for monotonic quantities and label any result diagnostic if iteration drift remains larger than mesh change.
7. Allow the already queued 2300k diagnostic continuation to run from 3000 to 6000; verify its separate 4000, 5000, and 6000 checkpoints and final-500 monitor stability.
8. If pressure continues moving, define the result as a closed-bottom accumulating/quasi-steady state and compare meshes at a common accepted state definition rather than claiming steady convergence.
9. Decide whether to rerun 1600k cleanly to remove the 87-iteration recovery exception.
10. Update setup 07a, project experiments, current status, blockers, validation, setup ordering, and repository log with accepted/diagnostic/unresolved labels.

## Open technical questions

- Is a steady solution physically meaningful for the closed-bottom geometry with continuous liquid injection, or should the carrier field be treated as transient accumulation?
- If the liquid imbalance is accepted by design, what physical state should define a fair cross-mesh comparison: iteration count, elapsed physical time, liquid inventory, or a stable vapor-field monitor?
- Which local swirl quantity should be the primary report metric? Domain-averaged vorticity is available, but a fixed-plane tangential velocity or swirl number would be more physically interpretable.
- Should the approximately 0.27% steam-outlet area variation across meshes be normalized or retained as part of grid uncertainty?
- Does the 2300k endpoint confirm the apparent fine-grid pressure/vorticity plateau, or does its iteration drift remain dominant?
- Is a clean 1600k rerun required for strict publication-quality iteration parity?

## Evidence and repository cautions

- The worktree contains many pre-existing modified and untracked files from broader project activity. Do not reset or discard them.
- This report is a live snapshot, not the final mesh-convergence report.
- Machine-readable manifests and CSVs are the primary quantitative evidence.
- The setup-07a repository page is currently stale relative to execution and must be reconciled after completion.
- Purnanto replication and spiral enthalpy/DPM outputs are context only; they must not be mixed into this carrier mesh study.
- Preserve all original mesh files, the settings file, replication outputs, and unrelated worktree changes.

## Immediate handoff statement

A new Codex task should begin by reading repository `AGENTS.md` files, this report, `preflight_manifest.json`, `study_manifest.json`, the active `mesh-2300k_run_manifest.json`, and the status/controller scripts. It should check whether the existing Fluent controller is still active before making any connection or mutation. The safe immediate objective is to let 2300k finish, verify the final case/data pair, then analyze and document the seven-mesh dataset without running DPM.
