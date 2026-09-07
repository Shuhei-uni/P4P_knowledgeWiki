# Split-Inlet Carrier-Field Mesh-Convergence Study

## 1. Purpose and final status

Carrier-field mesh-resolution study for the post-replication spiral/split-inlet
model.

- Parent setup: [07-pure-phase-split-actual-area.md](07-pure-phase-split-actual-area.md)
- Study ID: `split_inlet_mesh_convergence_20260801`
- Final classification: `Diagnostic — iteration independence and mesh independence unresolved`
- Seven formal meshes completed at 3000 iterations.
- One 900k diagnostic extension completed at 6000 iterations.
- DPM and Eulerian Wall Film were excluded from every calculation.

The final technical interpretation and machine-evidence links are in
[`STUDY_DIAGNOSTIC_CLOSURE_20260805.md`](../PyAnsys/output/split_inlet_mesh_convergence_20260801/STUDY_DIAGNOSTIC_CLOSURE_20260805.md).

## 2. Authoritative execution baseline

The executed study used:

```text
C:\Users\qtra338\Documents\Mesh study\partial_solution_diagnostic_20260801.cas.h5
C:\Users\qtra338\Documents\Mesh study\Source\mesh_study_settings.set
```

The partial solution was preserved as diagnostic evidence. Every formal mesh
was freshly hybrid-initialized. The settings file plus complete Fluent readback
was the execution authority, with critical-settings fingerprint:

```text
424a9bf02bbd78060dee3a2874103e5149aa4aa555a09e2add69da4d2a0158c5
```

The historical `FFF.1-2.cas.h5` archive remains setup-lineage evidence but was
not the numerical authority for this production study. Setup `08c` is a sibling
one-inlet enthalpy/DPM branch and is not the setup-07a baseline.

## 3. Verified geometry and zones

All seven meshes represent the same spiral/split-inlet domain and contain:

| Role | Fluent zone | Type | Final state |
|---|---|---|---|
| Outer-wall liquid strip | `liquidinlet` | mass-flow inlet | accepted |
| Inner/core steam region | `steaminlet` | mass-flow inlet | accepted |
| Steam outlet | `steamoutlet` | pressure outlet | accepted |
| Closed separator bottom | `bottom` | wall | accepted |
| Vessel walls | `wall-fluid` | wall | accepted |
| Fluid domain | `fluid` | fluid cell zone | accepted |

Geometry evidence across the mesh ladder:

- `liquidinlet` area `0.004889896 m2`;
- `steaminlet` area `0.5192861 m2`;
- distinct liquid/steam inlet centroids confirm separate parts of the inlet;
- domain volume `22.65670-22.65891 m3`;
- required zone mapping is unambiguous on every mesh.

The `bottom` wall is intentional and must not be changed within setup 07a.

## 4. Frozen physics, boundaries and numerics

Identical Fluent readback was required and accepted across all meshes:

- Fluent 2024 R2, 16 processes;
- pressure-based steady Mixture model with two phases;
- phase 1 `water-vapor-at-psep`, density `5.7974339 kg/m3`;
- phase 2 `water-liquid-at-psep`, density `881.21088 kg/m3`;
- RNG `k-epsilon`, differential viscosity and swirl-dominated option;
- gravity `(0, -9.81, 0) m/s2`, operating pressure `0 Pa`;
- Energy off;
- liquid inlet `116.92 kg/s`, vapor inlet `80.69 kg/s`;
- inlet turbulence intensity `2.1099999%`;
- hydraulic diameters `0.01338 m` liquid and `0.72061 m` steam;
- `steamoutlet` gauge pressure `1,120,000 Pa`, liquid backflow VF `0`;
- SIMPLE, PRESTO!, Green-Gauss node-based gradient;
- second-order momentum, first-order `k`, second-order epsilon, QUICK volume fraction;
- pressure/momentum/`k`/epsilon/multiphase/drift URFs `0.3/0.7/0.8/0.8/0.4/0.1`;
- fresh hybrid initialization for each formal mesh;
- DPM interaction off and no injection update/tracking.

Reference condition is approximately `1600 kJ/kg`, using the verified phase
flows `116.92/80.69 kg/s`.

## 5. Mesh ladder

Actual characteristic size is `h = (domain volume / cell count)^(1/3)`.
Filename labels are not treated as cell counts.

| Mesh | Actual cells | h (m) | Min. orthogonal quality | Max. aspect ratio |
|---|---:|---:|---:|---:|
| 300k | 1,688,678 | 0.0237620 | 0.200732 | 20.3226 |
| 600k | 3,609,102 | 0.0184476 | 0.191653 | 18.4352 |
| 900k | 5,335,623 | 0.0161938 | 0.202194 | 20.1267 |
| 1600k | 9,720,194 | 0.0132593 | 0.200348 | 19.5466 |
| 1900k | 10,756,635 | 0.0128190 | 0.200177 | 18.7413 |
| 2000k | 11,959,759 | 0.0123739 | 0.198112 | 17.8078 |
| 2300k | 13,370,267 | 0.0119225 | 0.200535 | 18.9096 |

All mesh checks passed. `mesh-stage2.msh` is byte-identical to
`mesh-600k.msh` and was excluded as a duplicate.

## 6. Acceptance criteria

Iteration independence required:

- primary monitor drift no more than `0.5%` over the accepted final window;
- velocity/vorticity drift no more than `1%`;
- residual history considered together with physical monitors;
- no unresolved oscillation or monotonic inventory drift.

Mesh independence required:

- no more than `1%` medium-to-fine change in primary metrics;
- no more than `2%` for secondary metrics;
- iteration error smaller than grid-to-grid change;
- no qualitative topology reversal.

Richardson extrapolation/GCI is accepted only for a monotonic sequence with a
usable observed order and iteration error small enough not to dominate the
grid difference.

## 7. Formal result

Every mesh reached the formal 3000-iteration endpoint and saved initialized,
1000-, 2000- and 3000-iteration case/data pairs.

| Mesh | Pressure drop (kPa) | Vapor outlet (kg/s) | Pressure final-500 drift (%) | Domain-velocity drift (%) | Classification |
|---|---:|---:|---:|---:|---|
| 300k | 31.0510 | -81.4886 | 4.377 | 0.814 | unresolved |
| 600k | 29.0005 | -81.4454 | 5.409 | 4.373 | unresolved |
| 900k | 27.6593 | -81.4474 | 9.650 | 6.778 | unresolved |
| 1600k | 25.2610 | -81.4612 | 8.164 | 8.689 | unresolved |
| 1900k | 24.0141 | -81.4664 | 2.693 | 9.195 | unresolved |
| 2000k | 24.1355 | -81.4625 | 2.456 | 9.174 | unresolved |
| 2300k | 23.7092 | -81.4465 | 2.660 | 9.133 | unresolved |

Steam-outlet vapor flow is stable and mesh-insensitive. Pressure and velocity
are not iteration-independent. Fine-grid pressure differences are smaller than
within-run pressure drift, so mesh convergence is not demonstrated.

## 8. 900k iteration diagnostic

The 900k mesh was continued from a verified iteration-4000 checkpoint to 6000,
with separate case/data files every 250 iterations. The formal 3000 files were
not overwritten.

Final 5500-6000 drift:

- pressure drop `4.612%`;
- vapor outlet flow `0.0217%`;
- outlet velocity `1.485%`;
- domain velocity `1.700%`;
- vorticity `1.825%`.

Only vapor flow passed. The extension remained `unresolved`.

A reversible post-processing audit measured liquid volume using Fluent's
volume integral of `phase-2-vof`:

| Iteration | Liquid inventory (kg) | Pressure drop (kPa) | Liquid at steam outlet (kg/s) |
|---:|---:|---:|---:|
| 4000 | 104.054 | 31.029 | -0.00758 |
| 5000 | 134.328 | 33.069 | -0.38028 |
| 5500 | 152.103 | 33.591 | -1.06011 |
| 6000 | 171.030 | 34.049 | -2.81420 |

Liquid inventory increased `64.37%` from 4000 to 6000. This directly confirms
that the pressure field is being compared while the phase inventory is still
changing.

## 9. Physical limitation and evidence-use rule

The user has accepted the liquid imbalance as a consequence of the intended
closed-bottom geometry. It is therefore reported rather than used as the sole
rejection gate. However, a steady calculation has no storage term. With liquid
entering continuously and no dedicated liquid outlet, the observed increasing
inventory prevents a conserved steady interpretation.

Consequences:

- liquid carryover and carrier quality are trend-only;
- no validated separator-efficiency claim is allowed;
- no accepted Richardson/GCI result is allowed;
- further steady iterations on setup 07a are not recommended;
- DPM and EWF remain blocked behind a defensible carrier-field formulation.

## 10. Outputs

Local evidence root:

```text
PyAnsys/output/split_inlet_mesh_convergence_20260801
```

Key files:

- `study_manifest.json` and `mesh_matrix.csv`;
- one preflight/readback/quality/metrics/manifest and residual/monitor/mass-flow
  CSV set per mesh;
- `mesh_900k/extension_4000_6000_iteration_diagnostic3/`;
- `mesh_900k/checkpoint_liquid_inventory/`;
- `STUDY_DIAGNOSTIC_CLOSURE_20260805.md`.

Remote case/data and transcripts are under:

```text
C:\Users\qtra338\Documents\Mesh study\split_inlet_mesh_convergence_20260801
```

## 11. Meeting visualization evidence (2026-08-10)

A post-processing-only Fluent graphics pass loaded the separately saved 900k
iteration-4000 and iteration-6000 case/data checkpoints. It used the same
longitudinal `x=-1.5 m` section, cell values, camera and fixed display ranges:

- phase-2 liquid volume fraction `0-0.05` for the diagnostic comparison, with
  separate full-range `0-1` exports preserved;
- absolute static pressure `1.10-1.20 MPa`;
- Mixture-model carrier pathlines released from `liquidinlet`, explicitly not
  DPM particle tracks.

The matched contours visually confirm the quantitative finding: the
liquid-rich wall region expands while inventory increases `64.37%`, and the
pressure field shifts while pressure drop increases `9.73%`. No iterations,
initialization, DPM update or case/data write occurred during the graphics
pass.

Meeting package:

- [Tuesday meeting brief](../PyAnsys/output/setup07_meeting_visuals_20260811/MEETING_BRIEF.md)
- [decision-summary figure](../PyAnsys/output/setup07_meeting_visuals_20260811/09_tuesday_decision_summary.png)
- [matched liquid-field contours](../PyAnsys/output/setup07_meeting_visuals_20260811/06_closed_bottom_liquid_field_comparison.png)
- [matched pressure contours](../PyAnsys/output/setup07_meeting_visuals_20260811/07_closed_bottom_pressure_field_comparison.png)
- [machine-readable visual manifest](../PyAnsys/output/setup07_meeting_visuals_20260811/visual_manifest.json)

These images are `Diagnostic / unresolved` evidence. Steady iterations are
not physical time, so the inventory change must not be reported as a physical
accumulation rate.

## 12. Next action

Freeze setup 07a as diagnostic/unresolved. If report-quality steady pressure
drop and separation performance are required, define a new setup branch with a
physically credible liquid discharge. Qualify one medium mesh for iteration
independence before repeating any mesh ladder.

A closed-bottom transient branch is appropriate only for a finite-time filling
or redistribution question, with defined initial inventory, physical time,
timestep independence and time-dependent inventory outputs.
