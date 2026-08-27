> **Retired source:** Setups/archived/02d-transient-vof-brine-outlet-model-form-sensitivity.md
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# Setup 02d — Transient VOF Brine-Outlet Model-Form Sensitivity

## Setup metadata

| Field | Value |
|---|---|
| Setup ID | `02d` |
| Lifecycle | `future` |
| Role | transient multiphase model-form sensitivity / setup definition |
| Parent setup | [02c — Mixture brine-outlet pressure sensitivity](../full-geometry-02c-mixture-pressure-sensitivity/setup.md) |
| Child cases | `VOF-IC0-P1120`, `VOF-IC1-P1120`, `VOF-IC2-P1120`; later, only after qualification: `VOF-P1115`, `VOF-P1120`, `VOF-P1125` |
| Controlled change | Replace the parent steady Mixture formulation with transient explicit VOF; preserve the parent geometry, mesh, physical operating basis, inlet topology, and baseline outlet pressure. |
| Evidence-use label | `User-specified` setup definition plus observed, case-only VOF rebuild evidence; no numerical result. |
| Outcome | IC0 case-only rebuilds exist on two mesh resolutions; IC1/IC2 remain gated by mesh/timestep readiness and human-approved patch regions. |
| Linked report | none — create a results report only after a qualified transient run. |

### 0.1 Case-only build record — 2026-08-14

`Observed`: the requested mesh was found and explicitly read from Fluent as `C:\Users\syok443\P4P simulation\brine-outlet-620kcells.msh.h5`. Fluent read `620,431` mixed cells, `1,770,229` nodes, two velocity inlets (`liquid-inlet`, `steam-inlet`), two pressure outlets (`brine-outlet`, `steam-outlet`), and the lower brine-outlet geometry in the fluid-zone naming. The exact lower pipe connectivity was not visually inspected in this case-only operation; its geometry-role confirmation remains a run-readiness item.

`Observed`: the following pre-initialization, case-only artifact was written and then explicitly reloaded for readback verification:

```text
C:\Users\syok443\P4P simulation\VOF-IC0-P1120-preinit-20260814T000000Z.cas.h5
```

The artifact is a **mesh-based reconstruction**, not a direct clone of a verified `02c` case/data parent. It passed readback for pressure-based `unsteady-1st-order` (the Fluent 2025 R2 representation compatible with explicit VOF), gravity `[0, -9.81, 0] m/s²`, `0 Pa` operating pressure, explicit/sharp VOF, Geo-Reconstruct, PRESTO!, RNG k-epsilon, and the named boundary-condition contract. `water-vapor` is phase 1/primary and `water-liquid` phase 2/secondary, with densities `5.73` and `881.77 kg/m³` respectively. Its liquid volume fraction is `1.0` at `liquid-inlet`, `0.0` at `steam-inlet`; liquid backflow fraction is `1.0` at `brine-outlet` and `0.0` at `steam-outlet`; both outlets are `1,120,000 Pa` gauge and both inlets are `27.118 m/s` with `1,140,000 Pa` initial gauge pressure.

`Observed`: no initialization, liquid patch, calculation iteration, data-file write, DPM injection, or EWF setup was performed. DPM continuous-phase interaction is off and no injections exist. The readback evidence is `02d VOF-IC0 build verification` (historical machine artifact path: `../../../PyAnsys/output/02d_vof_ic0_build_verification.json`; not migrated).

`Missing information / hold`: the mesh quality/local cell-size survey, timestep selection, physical-time monitor definitions, visual confirmation of lower-pipe connectivity, surface-tension source, and any surface-contact-angle decision remain incomplete. The loaded case contains Fluent's default `1 s` transient-control value; it is **not** endorsed as `VOF-DT1` and must not be used for a run until the Section 6 Courant assessment is completed.

### Coarse patch-platform rebuild and IC1 selection hold — 2026-08-14

`Observed`: a separately loaded coarse mesh was rebuilt as the same no-patch `VOF-IC0-P1120` configuration and reload-verified. It contains `275,448` mixed fluid cells, `815,716` nodes after Fluent write/read, one fluid cell zone (`simple-spiral-separator--brine-outlet-`), the expected `liquid-inlet`, `steam-inlet`, `brine-outlet`, and `steam-outlet` boundaries, minimum orthogonal quality `0.250006`, and maximum aspect ratio `65.1632`. The case-only artifact is:

```text
C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\VOF-IC0-P1120-coarse-patch-platform-preinit-20260814T000000Z.cas.h5
```

It passed the same VOF/BC readback contract as the first IC0 artifact. The saved artifact remains pre-initialization: no data-file write or calculation iteration was performed.

`Observed live test state`: the coarse test session was then Hybrid Initialized successfully (Fluent's internal `10` initialization passes; no transient flow timestep or calculation iteration). This activates the VOF Patch panel. The initialized field has deliberately not been saved as a data file so that it can be inspected before a patch decision.

`Observed candidate selection`: at the user's direction, a boundary-distance register was created in the initialized session as `vof_ic1_brine_outlet_5cells`. Readback confirms type `boundary`, source boundary list `[brine-outlet]`, option `cell-distance`, and distance `5`; Fluent reported `1,499` marked cells and displayed the register. This is an inspection candidate only, not proof that the complete pipe volume is selected. No `VOF-IC1-P1120` patch was applied. Visually confirm that the cells extend from the brine outlet through the entire tangential pipe to its vessel entrance, without including lower-vessel cells. If confirmed, patch phase-2 (`water-liquid`) volume fraction `alpha_liquid = 1.0` in this register only; otherwise delete/recreate it with an adjusted distance before any patch.

`User-approved IC1 patch`: the user inspected the five-cell candidate and approved its small lower-vessel spill as preferable to an under-filled pipe. The initialized session therefore patched `domain = phase-2`, `variable = mp` (the Fluent 2025 R2 phase-2 liquid volume-fraction field), `value = 1.0`, and `register = vof_ic1_brine_outlet_5cells`. The exact saved checkpoint is:

```text
C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\VOF-IC1-P1120-coarse-patch-platform-20260814T000000Z.cas.h5
C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\VOF-IC1-P1120-coarse-patch-platform-20260814T000000Z.dat.h5
```

This is a coarse-mesh patch-platform artifact, not a qualified transient result. It has no flow iteration/timestep, but it intentionally includes Hybrid Initialization plus the liquid patch and data write.

`Observed IC2 plane-based patch`: the boundary-distance candidate was deleted before use and replaced by the requested global-coordinate region approach. `vof_ic2_pool_below_y_0p30m` is an `inside` hexahedral cell register with full mesh horizontal extents `x = [-2.068679, 1.066381] m`, `z = [-1.461048, 1.066492] m`, and vertical interval `y = [-1.484584, +0.300000] m`. It therefore marks all fluid cells below the horizontal plane `y = +0.30 m`; Fluent reported `39,127` marked cells and displayed the register. The user inspected and approved this pool shape. It was patched with `domain = phase-2`, `variable = mp`, and `value = 1.0`, then saved as:

```text
C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\VOF-IC2-Y030-P1120-coarse-patch-platform-20260814T000000Z.cas.h5
C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\VOF-IC2-Y030-P1120-coarse-patch-platform-20260814T000000Z.dat.h5
```

No flow timestep or calculation iteration occurred. This is a reproducible coarse-mesh initialization/patch artifact, not a transient result.

### Coarse-mesh numerical-stability screen — 2026-08-14

`Correction / observed`: the user authorized an explicitly **non-production numerical smoke test** of IC0, the approved five-cell IC1 pipe patch, and IC2 `Y030`. The original journals requested two 1,000-step blocks at fixed `1.0e-5 s`; the step was applied after every case/data load, because a data-file read restores run controls. However, residual convergence checking remained enabled. Fluent stopped at 69/69/67 steps for IC0/IC1/IC2 Y030, respectively, and each transcript states `solution is converged`. The files below are therefore retained **nominally labelled** outputs, not evidence of 1,000/2,000 completed steps:

```text
C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\VOF-IC0-P1120-coarse-stability-iter1000-20260814T023000Z.cas.h5 + .dat.h5
C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\VOF-IC0-P1120-coarse-stability-iter2000-20260814T023000Z.cas.h5 + .dat.h5
C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\VOF-IC1-P1120-coarse-stability-iter1000-20260814T024000Z.cas.h5 + .dat.h5
C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\VOF-IC1-P1120-coarse-stability-iter2000-20260814T024000Z.cas.h5 + .dat.h5
C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\VOF-IC2-Y030-P1120-coarse-stability-iter1000-20260814T024000Z.cas.h5 + .dat.h5
C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\VOF-IC2-Y030-P1120-coarse-stability-iter2000-20260814T024000Z.cas.h5 + .dat.h5
```

The exact early-stop terminal continuity residuals were `9.4124e-04` (IC0), `9.0899e-04` (IC1), and `9.3460e-04` (IC2 Y030). A prior `1.0 s` queue attempt stopped before a checkpoint, and its subsequent IC1/IC2 files from the `20260814T023000Z` queue are retained solely as discarded large-step diagnostics: loading their data files reset the intended timestep. They are excluded from this screen's conclusion.

`In progress`: a fresh native queue now starts from uniquely saved sources which were reloaded and read back after all data reads with `time_step_size = 1.0e-5 s`, `time_step_count = 2000`, `max_iter_per_time_step = 20`, all six residual `check_convergence` flags `false`, and no physical convergence reports. It must reach flow time `0.0200 s` in each case to count as a completed 2,000-step screen. Its first IC0 transcript had continued through step 54 despite residuals that would previously have triggered early stopping. Final outcome remains pending transcript/flow-time evidence.

This screen does **not** close the local mesh/Courant timestep, physical-monitor, continuous-liquid-inventory, averaging/stationarity, surface-tension, or geometry-readiness gates. `1.0e-5 s` is a deliberately conservative error-screen setting, not a justified production `VOF-DT1`.

### IC2 liquid-level initialization sensitivity — planned

The plane-based register makes the initial-pool sensitivity one-dimensional and reproducible. For each case, preserve the same mesh, VOF/BC/numerics state, Hybrid Initialization, and approved five-cell IC1 pipe patch. Then create an inside-hexahedron register with the same full horizontal extents above and patch phase-2 `mp = 1.0` for all cells satisfying `y <= y_cut`. Do not alter the brine or steam outlet pressures, inlet conditions, or any physical model solely for this initialization sensitivity.

| Case ID | `y_cut` (m) | Register naming pattern | Purpose / interpretation limit |
|---|---:|---|---|
| `VOF-IC2-Y000-P1120` | `+0.00` | `vof_ic2_pool_below_y_0p00m` | lowest pool bracket; checkpoint saved |
| `VOF-IC2-Y015-P1120` | `+0.15` | `vof_ic2_pool_below_y_0p15m` | shallow-pool lower bracket |
| `VOF-IC2-Y030-P1120` | `+0.30` | `vof_ic2_pool_below_y_0p30m` | inspected central pool; checkpoint saved |
| `VOF-IC2-Y045-P1120` | `+0.45` | `vof_ic2_pool_below_y_0p45m` | moderate higher-pool bracket |
| `VOF-IC2-Y060-P1120` | `+0.60` | `vof_ic2_pool_below_y_0p60m` | deliberately higher-pool bracket |

`Observed Y000 checkpoint`: starting from the saved IC1 pipe-patch case/data—not the Y030 field—the full-width `y <= +0.00 m` register `vof_ic2_pool_below_y_0p00m` marked `33,200` cells. It was patched as phase-2 `mp = 1.0` and saved as:

```text
C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\VOF-IC2-Y000-P1120-coarse-patch-platform-20260814T000000Z.cas.h5
C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\VOF-IC2-Y000-P1120-coarse-patch-platform-20260814T000000Z.dat.h5
```

The `+0.15`, `+0.45`, and `+0.60 m` heights are `Assumed / sensitivity` values, selected as evenly spaced offsets around the visually accepted `+0.30 m` central level. All levels are below the user-stated `+1.704 m` inlet elevation. They are not claims about physical steady liquid level, initial mass, or interface location. Before running any of them, record Fluent-reported marked-cell count/volume and calculate the corresponding initialized liquid mass using the accepted liquid density; then apply the same timestep/monitor/stationarity gates as IC0.

### Fine-mesh patch cases and dormant native queue — 2026-08-14

`Observed`: the fine `620,431`-cell mesh (domain `x = [-2.068679, 1.066749] m`, `y = [-1.484584, 6.994597] m`, `z = [-1.461048, 1.066830] m`) now has independently saved paired case/data inputs for the approved IC1 five-cell outlet-distance patch and all five IC2 global-coordinate pool levels. Each IC2 sibling was rebuilt from the saved IC1 field, not from another pool-height field. Artifact paths are:

```text
C:\Users\syok443\P4P simulation\VOF-IC1-P1120-fine-patch-platform-20260814T000000Z.cas.h5 + .dat.h5
C:\Users\syok443\P4P simulation\VOF-IC2-Y000-P1120-fine-patch-platform-20260814T000000Z.cas.h5 + .dat.h5
C:\Users\syok443\P4P simulation\VOF-IC2-Y015-P1120-fine-patch-platform-20260814T000000Z.cas.h5 + .dat.h5
C:\Users\syok443\P4P simulation\VOF-IC2-Y030-P1120-fine-patch-platform-20260814T000000Z.cas.h5 + .dat.h5
C:\Users\syok443\P4P simulation\VOF-IC2-Y045-P1120-fine-patch-platform-20260814T000000Z.cas.h5 + .dat.h5
C:\Users\syok443\P4P simulation\VOF-IC2-Y060-P1120-fine-patch-platform-20260814T000000Z.cas.h5 + .dat.h5
```

`Observed`: the dormant Fluent-native journal `02d-fine-vof-ic0-ic1-ic2-queue-20260814T000000Z.jou` was written locally and remotely but **not executed**. It contains seven sequential jobs: IC0, IC1, and IC2 Y000/Y015/Y030/Y045/Y060. IC0 is Hybrid Initialized after loading its clean pre-initialization case. Each patched case instead loads its saved case/data pair without reinitializing, then runs `500` iterations, writes an explicit paired checkpoint, runs a further `500` iterations, and writes the final paired checkpoint. No job has been started. Its future run outputs are `*-fine-iter500.cas.h5/.dat.h5` and `*-fine-iter1000.cas.h5/.dat.h5`.

`Hold`: the journal must remain dormant until the production timestep, monitor package, averaging window, initial liquid volumes/masses, and other Stage-1 readiness gates are explicitly defined. Its presence is run preparation, not run authorization or numerical evidence.

## 1. Objective and hypothesis

**Objective.** Determine whether explicitly resolving the continuous water–vapour interface with VOF gives a more physically plausible liquid-drainage path through the tangential brine outlet than the existing Mixture-model cases.

**Scientific hypothesis (`User-specified`).** At the baseline outlet pressure, a meaningful VOF solution may form a steam core connected to the steam outlet and a continuous liquid structure that follows the vessel wall/lower vessel into the tangential brine pipe, without excessive vapour discharge through that pipe. The expected liquid structure is not assumed to be a flat horizontal pool. ([experiment-3-brief-2026-08-14], user-provided brief)

This is a **model-form sensitivity**, not another pressure-outlet sensitivity. No flashing or evaporation-condensation model is introduced merely because VOF is enabled.

### 1.1 Scope and lineage

The comparable Mixture control is setup `02c`, particularly its unprimed baseline at equal brine and steam-outlet gauge pressures. The historical VOF side branch [02b](../../phase-01-purnanto-baseline-and-inlet-exploration/purnanto-02b-vof-split-inlet-transient/setup.md) remains archived as an invalid qualitative run; it is context only and must not be overwritten, treated as a parent artifact, or used as numerical evidence.

Before building `02d`, load and record a verified parent case/data path. Confirm that it contains the intended physical tangential brine-pipe geometry, split velocity inlets, pressure outlets, material properties, and mesh. The currently documented `02c` screens are not a stable parent result, so their results must not be used to validate VOF.

## 2. Parent physical operating basis

The following values are `User-specified` for this experiment and must be read back from the selected parent before the VOF model-form change is saved. They are the controlled common basis for the Mixture-versus-VOF comparison. ([experiment-3-brief-2026-08-14], user-provided brief)

| Quantity | Required value | Evidence / status |
|---|---:|---|
| Operating pressure | `0 Pa` gauge | `User-specified`; readback required |
| Inlet velocity | `27.118 m/s` | `User-specified`; preserve split-inlet value and direction |
| Inlet reference / initialization gauge pressure | `1.140 MPa` | `User-specified`; confirm where represented in the parent |
| Steam-outlet gauge pressure | `1.120 MPa` | `User-specified`; pressure outlet |
| Baseline brine-outlet gauge pressure | `1.120 MPa` | `User-specified`; pressure outlet |
| Liquid density | `881.77 kg/m³` | `User-specified`; verify material/property use |
| Vapour density | `5.73 kg/m³` | `User-specified`; verify material/property use |
| Gravity magnitude | `9.81 m/s²` | `User-specified`; verify vector against the established geometry coordinate system |
| Geometry and mesh | exact selected parent geometry/mesh | `User-specified` control rule; do not remesh automatically |

**Inherited settings.** Keep energy and phase-change treatment consistent with the verified parent. `Uncertain`: the parent energy/phase-change state and gravity vector have not been supplied in this brief, so they must be recorded from Fluent rather than guessed.

## 3. Required Fluent model and numerical configuration

| Category | Required setting | Status / implementation note |
|---|---|---|
| Solver family | pressure-based, **Transient** | `User-specified`; confirm no unintended solver-family drift |
| Multiphase model | VOF | `User-specified`; replaces Mixture only |
| Primary phase | water-vapour | `User-specified`; confirm that its volume fraction is the complement of liquid |
| Secondary phase | water-liquid | `User-specified`; patch and diagnostics use `alpha_liquid` |
| VOF formulation | Explicit | `User-specified`; required before qualification |
| Interface treatment | Sharp | `User-specified`; read back the exact Fluent control/name |
| Volume-fraction discretization | Geo-Reconstruct | `User-specified`; do not silently substitute another scheme |
| Gravity | ON | `User-specified`; use parent-coordinate gravity vector after verification |
| Turbulence | RNG k-epsilon | `User-specified`; preserve parent wall treatment unless a separately documented change is required |
| Pressure discretization | PRESTO! | `User-specified` |
| Energy / phase change | preserve parent state | no new flashing, evaporation, or condensation model |
| Surface tension | existing confirmed project/reference value only | see Section 8 |

`Missing information`: pressure–velocity coupling, momentum/turbulence discretization, under-relaxation/explicit VOF controls, iterations per time step, phase backflow fractions, material viscosity, and exact wall treatment. Read these from the verified parent or Fluent configuration and record them in the future results report. Do not invent them.

## 4. Boundary-condition contract

| Boundary role | Required state |
|---|---|
| Split liquid-side inlet | Preserve verified parent zone identity, velocity direction, `27.118 m/s`, phase condition, and `1.140 MPa` reference/initial gauge-pressure basis. |
| Split vapour-side inlet | Preserve verified parent zone identity, velocity direction, `27.118 m/s`, phase condition, and `1.140 MPa` reference/initial gauge-pressure basis. |
| Steam outlet | Pressure outlet, `1.120 MPa` gauge; preserve/record verified VOF backflow phase settings. |
| Tangential brine outlet | Pressure outlet, `1.120 MPa` gauge for qualification; explicitly record VOF backflow phase settings. |
| Walls | Preserve verified parent wall and material interaction settings. Do not introduce an unsupported contact angle. |

### Geometry and zone gate

Before changing physics, verify that the lower tangential pipe end face is the `brine outlet`, the pipe is fluid-connected to the lower vessel, the steam outlet and both split inlet faces are correct, and there are no ambiguous additional openings. Stop for user direction if any zone name, connectivity, or boundary type is ambiguous.

## 5. Initialization study and human-assisted patching gate

All three definitions use the qualified baseline brine pressure (`P_brine = 1.120 MPa`). They are separate initialization sensitivities, not interchangeable starts for one result.

| Case ID | Definition | Build/run status |
|---|---|---|
| `VOF-IC0-P1120` | Hybrid/parent-consistent initialization; **no liquid patch**. | May proceed only after the Section 10 verification gate. |
| `VOF-IC1-P1120` | After initialization, patch `alpha_liquid = 1` inside the **complete brine-pipe fluid volume only**. Do not patch a large vessel region. | **Human-assisted hold.** |
| `VOF-IC2-P1120` | After initialization, patch `alpha_liquid = 1` in a small lower-vessel region with upper level approximately just above the brine-pipe entrance. | **Human-assisted hold.** |

### Required human-assisted procedure for IC1 and IC2

Do not guess patch geometry through gRPC, TUI workarounds, coordinates, or inferred cells. If an unambiguous separate cell zone/register does not already exist, stop and ask the user to create or identify the selection.

At the hold point, report all four items below and wait for input:

1. required region (`IC1`: full brine-pipe fluid volume; `IC2`: small lower-vessel region immediately above pipe entrance);
2. currently visible Fluent zones and cell registers;
3. desired approximate geometry; and
4. exact manual action requested (for example, create a named cell register, plane/coordinate-based selection, or GUI region).

For `VOF-IC2-P1120`, the approved setup record must add the upper liquid-level coordinate, patched volume, and estimated initial liquid mass before running. These are currently `Missing information`, not values to infer.

## 6. Timestep analysis and temporal sensitivity

Do not select a production timestep by convention. For each verified parent mesh, inspect or obtain the relevant local cell sizes in the inlet, liquid-wall region, lower vessel, brine-pipe entrance, brine pipe, and brine outlet. Use

```text
Delta_t <= Co_target * Delta_x / U_reference
Co_target = 0.25
U_reference = 27.118 m/s
```

For illustration only, `Delta_x = 0.01 m` yields `Delta_t ≈ 9.22e-5 s`; therefore `1e-4 s` is only a plausible starting order of magnitude, not a prescribed timestep. Smaller locally controlling cells require a smaller `Delta_t`. ([experiment-3-brief-2026-08-14], user-provided brief)

| Case | Timestep | Purpose / acceptance |
|---|---:|---|
| `VOF-DT1` | `Delta_t`, justified from measured mesh sizes | qualification / production candidate |
| `VOF-DT2` | `Delta_t / 2` | temporal sensitivity; compare time-averaged engineering outputs over documented comparable windows |

The VOF result is not temporally qualified until `VOF-DT2` gives acceptably similar time-averaged outputs to `VOF-DT1`; the numerical tolerances and averaging window must be defined before interpreting results.

## 7. Mesh assessment gate

Assess the existing mesh—without automatically changing it—in the spiral inlet, liquid-separation/impact region, vessel wall, lower vessel, brine-pipe entrance, and brine pipe. Record local approximate cell size, mesh-quality statistics, and whether the interface/Courant constraint can be met.

If refinement appears necessary, stop and report: (1) inadequate region, (2) current approximate cell size, (3) recommended target size, and (4) why interface resolution is inadequate. The user decides any geometry or mesh-topology change.

## 8. Surface tension and staged physics

Use a project/reference surface-tension value only if it is already confirmed in the selected parent or source record. `Missing information`: confirmed value, source, and whether a wall-adhesion/contact-angle condition is required. Do not choose an arbitrary contact angle; if one is necessary but unsupported, label it `Sensitivity / unresolved modelling assumption` (high risk) and seek direction.

The first qualification is deliberately simple:

| Stage | Physics scope | Decision rule |
|---|---|---|
| 1 | VOF continuous phases only | required first; establish credible interface/drain behaviour |
| 2 | VOF + DPM | only after Stage 1 is interpretable |
| 3 | VOF + DPM + EWF | only after Stage 2; do not enable film-to-VOF or VOF-to-film conversion during Stage 1 |

## 9. Required monitors, diagnostics, and comparisons

Configure physical-time histories for:

- liquid and vapour mass flow at the brine outlet;
- liquid and vapour mass flow at the steam outlet;
- continuous-liquid inventory;
- pressure near the brine outlet and in the lower vessel;
- whole-domain mass imbalance; and
- area-averaged liquid volume fraction at the brine outlet, if practical.

Freeze the precise surface/point definitions and Fluent sign convention. Record both raw Fluent values and outward-positive values when Fluent reports outward flow as negative.

Prepare `alpha_liquid = 0.5` isosurfaces and transient liquid-volume-fraction contours. Inspect the liquid wall sheet, lower-liquid structure, pool formation, rotating interface, brine-pipe filling, and vapour penetration into the brine pipe.

After startup, assess **statistical stationarity**, not perfect pointwise constancy: liquid inventory, brine liquid/vapour flow, and steam-outlet flow must oscillate around documented mean values. Calculate time-averaged values over a stated post-startup window.

Use the same definitions as setup `02c` for direct comparison:

```text
liquid_closure_error =
abs(liquid_in - liquid_brine_out - liquid_steam_out) / abs(liquid_in)

steam_wrong_outlet_fraction =
abs(vapour_brine_out) / abs(vapour_in)
```

Compare `Mixture—no initialization`, `Mixture—locally primed drain`, and VOF using liquid/vapour outlet flows, liquid inventory, pressure, and mass closure. VOF additionally reports interface topology/motion and liquid structure near the drain. No result may be called physically superior solely because it is visually sharper.

## 10. Setup verification and stop conditions

### Required readiness checklist

1. VOF and transient solver are active; vapour is primary and liquid secondary.
2. Gravity, explicit VOF, sharp interface treatment, Geo-Reconstruct, and PRESTO! are read back.
3. Steam and tangential brine outlets are correctly identified pressure outlets at `1.120 MPa` baseline.
4. Parent geometry/mesh and all non-model-form settings are read back; unintended changes are rejected.
5. IC0/IC1/IC2 definitions and any approved patch region are documented.
6. Relevant local mesh sizes are known and timestep is Courant-justified.
7. The `DT1`/`DT2` sensitivity plan, monitor package, and averaging window are defined.
8. Surface-tension/contact-angle evidence and staged DPM/EWF state are recorded.

### Mandatory stop conditions

Stop and request user input before proceeding if the brine pipe or lower-liquid region cannot be uniquely selected; a patch register is absent; mesh refinement is indicated; connectivity or zone names are ambiguous; a geometry-related VOF assumption is needed; or a required Fluent setting cannot be read/set reliably through the available interface. Do not use increasingly complex geometric or TUI workarounds.

## 11. Qualification sequence and future pressure sweep

1. Verify the parent geometry, mesh, zones, and all inherited settings.
2. Configure and read back the Stage-1 VOF baseline.
3. Determine `VOF-DT1` from measured local cells; define `VOF-DT2`.
4. Run **only when authorized**: `VOF-IC0-P1120` as the no-patch qualification case.
5. Stop for human region approval before `VOF-IC1-P1120` and `VOF-IC2-P1120`; record their reproducibility data.
6. Qualify temporal sensitivity and establish an averaging window before any pressure comparison.
7. Only then prepare direct-comparison VOF pressure cases: `VOF-P1115` (`1.115 MPa`), `VOF-P1120` (`1.120 MPa`), and `VOF-P1125` (`1.125 MPa`) at the brine outlet, with the steam outlet fixed at `1.120 MPa`.

No final production simulation is authorized by this setup report.

## 12. Assumptions, risks, and linked evidence

| Item | Label | Risk | Handling |
|---|---|---|---|
| Experimental requirements in this report | `User-specified` | Low | source: `[experiment-3-brief-2026-08-14]`, the user-provided experiment brief |
| Parent case identity and actual Fluent readback | `Missing information` | High | verify before build; do not clone an unverified live session |
| Local VOF-relevant cell sizes / quality | `Missing information` | High | assess before timestep or production recommendation |
| IC1 and IC2 geometry | `Missing information` | High | user-approved Fluent register/selection required |
| Surface tension and contact angle | `Missing information` | Medium–High | use confirmed existing value only; otherwise retain as sensitivity/open assumption |
| Whether VOF improves drainage plausibility | `Inferred hypothesis` | High | decide only from qualified transient monitor, topology, and sensitivity evidence |

## Cross-references

- Parent/control: [02c — Mixture brine-outlet pressure sensitivity](../full-geometry-02c-mixture-pressure-sensitivity/setup.md)
- Historical invalid VOF context: [02b — VOF split-inlet transient](../../phase-01-purnanto-baseline-and-inlet-exploration/purnanto-02b-vof-split-inlet-transient/setup.md)
- Setup lineage: historical ordering is recoverable from Git history.
- Project state: [current Project state](../../../index.md)
