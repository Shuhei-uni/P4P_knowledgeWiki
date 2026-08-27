> **Retired source:** the former root meeting-report file is recoverable from Git history.
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Machine-generated artifacts remain with their original external owners.

# Meeting Report — Mesh Refinement, Droplet Loading, and Wall Film

**Meeting date:** 2026-08-04  
**Purpose:** Brief update on the mesh-refinement checkpoint, the planned droplet-loading sensitivity study, the revised droplet-size distribution, and the unresolved wall-film stopping criterion.

## Executive summary

- **Mesh refinement:** Vapor throughput is already stable, but pressure drop, domain velocity, and vorticity continue to change with mesh size. The larger meshes also require more iterations to reach a comparable state. Mesh independence has not been demonstrated, and the finest, approximately 2.3-million-cell mesh is still in progress.
- **Droplet loading:** The next study is a one-factor sensitivity analysis in which the fixed `116.920 kg/s` liquid feed is partitioned between tracked fine droplets and the continuum liquid phase. The planned points are `1%`, `2%`, `3%`, `4%`, `5%`, and `10%`; the current `5%` case is diagnostic rather than converged.
- **Wall film:** Film inventory and maximum thickness increase between the `5,000`- and `10,000`-iteration snapshots. There is not yet a defensible iteration at which the film should be stopped; a thickness contour and fixed-interval histories are needed.

## Reader orientation

The model represents liquid in two ways:

| Term | Meaning in this report |
|---|---|
| **Tracked droplets / discrete phase model (DPM)** | Individual or parcel-based fine-mist droplets injected with the steam and transported through the separator. |
| **Continuum or Eulerian liquid** | The bulk liquid flow entering through the liquid inlet; this represents liquid that is not being treated as steam-carried fine mist. |
| **Global DPM interaction** | Two-way coupling: tracked droplets can return mass, momentum, and other source terms to the carrier flow. |
| **Wall film** | Liquid deposited on separator surfaces and handled by the wall-film model. |
| **Iteration** | A numerical solver update, not elapsed physical time. Therefore, an iteration count alone is not a physical stopping criterion. |

The total liquid feed is held at `116.920 kg/s`. In the planned cases, only the allocation between tracked fine droplets and continuum liquid changes; geometry, mesh, solver controls, and the selected injection distribution should remain fixed.

## 1. Mesh-refinement checkpoint

The table reports the available endpoint values at a common `3,000`-iteration checkpoint. The descriptive labels are used here so that the comparison can be read without project-specific case names; the historical record IDs are retained only in the traceability list at the end.

### Completed endpoint results

| Mesh-refinement level | Actual cells | Characteristic size, `h` [m] | Pressure drop [kPa] | Vapor at steam outlet [kg/s] | Liquid at steam outlet [kg/s] | Outlet velocity [m/s] | Domain velocity [m/s] | Domain vorticity [1/s] | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Coarsest completed | 1,688,678 | 0.0237620 | 31.0510 | 81.488642 | 0.84725781 | 51.08266 | 32.85721 | 68.88294 | Completed endpoint |
| Intermediate 1 | 3,609,102 | 0.0184476 | 29.0005 | 81.445409 | 0.01250556 | 47.78058 | 32.12963 | 77.79892 | Completed endpoint |
| Intermediate 2 | 5,335,623 | 0.0161938 | 27.6593 | 81.447366 | 0.00007952 | 46.23508 | 30.81236 | 82.39088 | Completed endpoint |
| Fine 1 | 9,720,194 | 0.0132593 | 25.2610 | 81.461226 | 0.00008392 | 43.04686 | 28.14025 | 85.84952 | Completed endpoint |
| Fine 2 | 10,756,635 | 0.0128190 | 24.0141 | 81.466425 | 0.00001114 | 44.14708 | 26.91599 | 86.00685 | Completed endpoint |
| Fine 3 | 11,959,759 | 0.0123739 | 24.1355 | 81.462457 | 0.00003356 | 42.55820 | 26.48653 | 86.89046 | Completed endpoint |
| Finest in progress | 13,370,267 | 0.0119225 | — | — | — | — | — | — | In progress at checkpoint |

**Interpretation.** Vapor outlet flow is stable at approximately `81.45 kg/s` (less than approximately `0.06%` variation), but pressure drop decreases from `31.05` to approximately `24.0 kPa`, domain velocity decreases from `32.86` to `26.49 m/s`, and vorticity increases from `68.88` to `86.89 1/s`. The larger meshes require more iterations to reach a comparable state. At the common endpoint, domain-velocity drift is approximately `9.2%` for the two finest completed meshes, while pressure drift remains approximately `2.5–2.7%`. The endpoint differences therefore combine mesh-resolution effects with iteration effects; mesh independence has not been demonstrated. ([mesh-refinement checkpoint](../experiments/purnanto-08b-parity-split-inlet/mesh-convergence-checkpoint-20260803.md))

## 2. Droplet-loading sensitivity analysis

The appropriate name for this work is a **droplet-loading sensitivity analysis**, or a **one-factor parameter sweep**. The swept factor is the fraction of the total liquid feed represented by tracked droplets:

```text
m_tracked droplets = f_droplet × 116.920 kg/s
m_continuum liquid = (1 − f_droplet) × 116.920 kg/s
```

| Loading point | Share assigned to tracked droplets | Tracked-droplet flow [kg/s] | Continuum-liquid flow [kg/s] | Purpose |
|---|---:|---:|---:|---|
| No-droplet reference | `0%` | `0.000` | `116.920` | Optional carrier-only control; not a droplet-loading claim |
| Low loading | `1%` | `1.169` | `115.751` | Planned sensitivity point |
| Low-to-mid loading | `2%` | `2.338` | `114.582` | Planned sensitivity point |
| Mid loading | `3%` | `3.508` | `113.412` | Planned sensitivity point |
| Mid loading | `4%` | `4.677` | `112.243` | Planned sensitivity point |
| Current diagnostic | `5%` | `5.846` | `111.074` | Existing reference point; not yet converged |
| Upper sensitivity | `10%` | `11.692` | `105.228` | Planned upper/extreme sensitivity point |

For this first sweep, keep the mesh, geometry, solver settings, injection material and surface, DPM controls, and droplet-size distribution fixed. Change only the tracked-droplet total and the complementary continuum-liquid flow. The current `5%` case has approximately `57.55%` carrier imbalance and continuity of approximately `2.86e-1`, so it should be treated as a diagnostic rather than a converged physical baseline. The earlier unpartitioned additional-load case is not a physically comparable sweep point. ([partitioned droplet-loading setup](../experiments/purnanto-09cV2-dpm-partition-control/setup.md), [diagnostic results](../experiments/purnanto-09cV2-dpm-partition-control/results.md), [global-interaction comparison](../observations/03-08b-09c-global-dpm-interaction.md))

## 3. Droplet-size and mass-distribution basis

The historical droplet sizes were based on Purnanto's Harwell-based estimate, not on a measured geothermal-inlet particle-size distribution. The reported basis uses an approximately `10 µm` average/Sauter-scale input, the relation `x_med = 1.42 × x_sa`, and approximate distribution markers at `0.3 × x_med` and `2.9 × x_med`. Treating `10 µm` as `x_sa` gives an inferred median of approximately `14.2 µm` and an approximate range of `4.26–41.18 µm`. The exact project injection diameters and original mass allocation are not listed in the source, so the inherited mapping is a **modelling reconstruction**, not a measured PSD. ([Purnanto source extraction](../../CFD_wiki/wiki/sources/purnanto-2013-cfd-geothermal-separator.md), [fine-mist distribution record](../experiments/purnanto-09cV3-fine-mist-psd/fine-mist-interpretation.md))

The new distribution is being changed because global DPM interaction is now enabled. Tracked droplets can feed source terms back into the carrier flow, so the DPM population should represent only the fine mist plausibly transported from the steam inlet. Bulk brine, films, slugs, and other large liquid mass are assumed to belong to the continuum liquid entering through the liquid inlet. This avoids allowing a coarse droplet class to dominate the coupled DPM source, and it preserves the total liquid feed rather than deleting or double-counting the excluded mass.

The provisional distribution was derived in four steps: (1) use `5–100 µm` as the fine-mist range, with a separate `100–150 µm` coarse-tail sensitivity if approved; (2) add resolution in the `20–60 µm` transition range, where capture, settling, Stokes, and breakup behaviour are most relevant; (3) represent each interval by its geometric midpoint; and (4) fit a truncated Rosin–Rammler cumulative **mass** distribution using `F(30 µm) = 0.50` and `F(60 µm) = 0.90`. This gives `n = 1.7320` and `d_c = 37.070 µm` before truncation and renormalisation.

### Recommended provisional distribution

| Diameter interval [µm] | Representative injection diameter [µm] | Mass share of tracked droplets | Tracked-droplet flow at `5%` [kg/s] |
|---:|---:|---:|---:|
| `5–10` | `7.07` | `6.998%` | `0.409128` |
| `10–20` | `14.14` | `19.931%` | `1.165149` |
| `20–30` | `24.49` | `21.680%` | `1.267410` |
| `30–40` | `34.64` | `18.688%` | `1.092501` |
| `40–60` | `48.99` | `22.738%` | `1.329262` |
| `60–80` | `69.28` | `8.016%` | `0.468606` |
| `80–100` | `89.44` | `1.949%` | `0.113944` |
| **Total** | — | **`100.000%`** | **`5.846000`** |

Use the same relative weights at every sweep point:

```text
m_i(f_droplet) = mass_share_i × f_droplet × 116.920 kg/s
```

The first new distribution comparison should use seven separate steam-inlet injections at `5%` tracked-droplet loading and be recorded as a new child case, leaving the historical six-bin results traceable. **Supervisor input requested:** confirm whether this provisional fine-mist distribution should become the baseline and whether the `100–150 µm` coarse-tail sensitivity is needed.

## 4. Wall-film status

The available continuation results show a substantial iteration dependence:

| Solver iteration | Film inventory [kg] | Maximum thickness [mm] | Maximum film Courant number (CFL) [-] |
|---:|---:|---:|---:|
| `5,000` | `0.2022` | `0.457` | `5.07e-3` |
| `10,000` | `0.2884` | `0.614` | `3.03` |

Between these snapshots, film inventory increases by `42.6%` and maximum thickness by `34.2%`; continuity also worsens. There is therefore no defensible stopping iteration yet. The next run should record film inventory, maximum and area-average thickness, film CFL, DPM-to-film source, film outflow, and residuals at fixed intervals. Use a CFL guard of less than `1` and select a stable interval—or explicitly report an accumulating/quasi-steady state—rather than stopping on iteration count alone. ([wall-film continuation results](../experiments/purnanto-010V2d-ewf-combined-mechanisms/results.md), [iteration-continuation observation](../observations/06-010v2-iteration-continuation.md))

> **Figure placeholder — wall-film thickness contour**
>
> Insert the separator-vessel wall-film-thickness contour here.
>
> Briefly discuss where the film is concentrated, whether it follows the expected wall-flow path, whether isolated very-thick regions occur, and whether the pattern changes between the selected checkpoints.

## 5. Decisions requested and next actions

| Decision / action | Supervisor discussion point |
|---|---|
| Mesh comparison | Continue the fine meshes until a common stable window is available, or accept a clearly labelled quasi-steady/accumulating diagnostic. |
| Droplet-loading sweep | Approve `1%`, `2%`, `3%`, `4%`, `5%`, and `10%` at fixed total liquid mass, with `0%` as an optional control. |
| Droplet baseline | Confirm the provisional `5–100 µm` seven-bin distribution and whether the `100–150 µm` coarse tail should be tested. |
| Wall-film stopping rule | Advise which combination of film histories, CFL, residuals, and contour behaviour is sufficient to stop or classify the run. |

Next, continue the running finest mesh and mature the carrier-flow state, rerun the `5%` point with the revised distribution, execute the loading sweep, and add the wall-film contour and histories before making a final stopping decision.

## Appendix A — Metric definitions and source trail

The following project record IDs are retained only so the analysis can be reproduced; they are not required to understand the main discussion.

- [Mesh-refinement checkpoint](../experiments/purnanto-08b-parity-split-inlet/mesh-convergence-checkpoint-20260803.md)
- [Partitioned droplet-loading setup](../experiments/purnanto-09cV2-dpm-partition-control/setup.md)
- [Partitioned droplet-loading diagnostic results](../experiments/purnanto-09cV2-dpm-partition-control/results.md)
- [Fine-mist droplet-size and mass-distribution record](../experiments/purnanto-09cV3-fine-mist-psd/fine-mist-interpretation.md)
- [Purnanto technical source extraction](../../CFD_wiki/wiki/sources/purnanto-2013-cfd-geothermal-separator.md)
- [Droplet carryover and re-entrainment physics basis](../../CFD_wiki/wiki/physics-basis/droplets-carryover-and-re-entrainment.md)
- [Fine-mist size-cutoff evidence](../../CFD_wiki/wiki/synthesis/geothermal-fine-mist-size-cutoff-evidence.md)
- [Wall-film continuation results](../experiments/purnanto-010V2d-ewf-combined-mechanisms/results.md)
- [Global-DPM wall-film results](../experiments/purnanto-010V2d-2-ewf-global-dpm/results.md)
- [Wall-film iteration-continuation observation](../observations/06-010v2-iteration-continuation.md)

## Appendix B — Fluent settings for the relevant cases

This appendix records the Fluent settings that matter for interpreting the three cases discussed in the meeting. The case names are retained here as identifiers because they are needed to reproduce the work; the descriptive role of each case is given first. `Observed` means that the value was read from a case, replay, or diagnostic report; `User-specified` means that it was selected for the project branch; `Inferred` means that it follows from the setup logic but was not directly exposed by the readback; and `Uncertain` means that the current evidence is insufficient to claim the value.

### B.1 08b — carrier-field mesh refinement and parity-rebuild context

The mesh-refinement checkpoint associated with **08b** is a carrier-field comparison. DPM tracking and Eulerian Wall Film (EWF) were excluded from the mesh-selection runs, and the formal mesh ladder used a nominal `3,000` iterations per mesh. Equal iteration count is not treated as equal convergence. The DPM settings below describe the associated parity-rebuild context, not an active DPM model in the mesh-convergence calculation. ([mesh-refinement checkpoint](../experiments/purnanto-08b-parity-split-inlet/mesh-convergence-checkpoint-20260803.md), [08b parity-rebuild record](../experiments/purnanto-08b-parity-split-inlet/setup.md))

#### Carrier-field settings

| Fluent setting | Recorded value | Evidence / interpretation |
|---|---|---|
| Fluent release | Ansys Fluent `2024 R2` for the live-reference audit; a replay was also inspected in Fluent `2026 R1` | `Observed`; the replay version is a source of serialization differences, not a claim that the mesh checkpoint used both releases. |
| Solver | `3D`, double precision, pressure-based, steady | `Observed` in the live-reference setup. |
| Multiphase model | `Mixture`, two phases | `Observed`. Phase 1 is `water-vapor-at-psep`; phase 2 is `water-liquid-at-psep`. |
| Energy, species, radiation | Energy `Off`; species `Off`; radiation `None` | `Observed`. |
| Turbulence | RNG `k-epsilon`; standard wall functions; differential-viscosity and swirl-dominated-flow options enabled | `Observed` in the extracted/reference settings; the swirl option is relevant to the separator's curved flow. |
| Gravity and operating state | Gravity `(0, -9.81, 0) m/s²`; operating pressure `0 Pa`; operating temperature `298.15 K` | Gravity and pressure are `Observed`; the temperature is observed in the live archive but was not serialized in the rebuilt replay. |
| Operating density | Mixture-averaged in the live archive | `Observed`; the replay read back minimum-phase-averaged, so this remains a parity item to verify before claiming exact reproduction. |
| Phase-material properties | Vapor: `5.7974339 kg/m³`, `1.52062e-5 kg/(m·s)`; liquid: `881.21088 kg/m³`, `1.45544e-4 kg/(m·s)` | `Observed` reference values; they should be read back again if the case is rebuilt in a different Fluent release. |
| Inlet arrangement | Two split inlet zones: a liquid-dominant zone and a steam-side zone | The 08b branch is defined around split mass-flow control, but one replay/export serializes the zones with `velocity_inlet` names. The final Fluent boundary-type readback should be recorded before parity is claimed. |
| Inlet phase targets | Vapor `80.690 kg/s`; liquid `116.920 kg/s`; inlet pressure field `1,140,000 Pa`; turbulence intensity `2.11%`; hydraulic diameter `0.724 m` | `Observed` project targets. |
| Outlet | Pressure outlet with pressure field `1,120,000 Pa`; total-pressure backflow specification; liquid backflow volume fraction `0` | `Observed`; the project mesh uses `steamoutlet` as the only outlet. |
| Walls | `wall`/`wall-fluid` and `bottom` are stationary no-slip walls; roughness height `0`, roughness constant `0.5` | `Observed`; the closed-bottom topology is important because it limits full liquid-mass closure. |
| EWF in mesh checkpoint | `Off` / excluded from the mesh-selection study | `Observed scope`; no wall-film conclusion should be drawn from the 08b mesh table. |

#### Numerical controls and convergence monitors

| Control group | Recorded setting |
|---|---|
| Pressure–velocity coupling | `SIMPLE` |
| Gradient | Green–Gauss Node Based |
| Pressure interpolation | `PRESTO!` |
| Momentum, `k`, epsilon | Second Order Upwind |
| Volume fraction | `QUICK` |
| Time and velocity formulation | Pseudo-time `Off`; absolute velocity formulation |
| Rhie–Chow option | High-order term relaxation disabled |
| Under-relaxation factors | Pressure `0.3`; momentum `0.7`; volume fraction approximately `0.4`; `k` `0.8`; epsilon `0.8`; density and body force `1.0`; slip/drift approximately `0.1`; turbulent viscosity `1.0` |
| Residual criteria | Continuity `1e-4`; velocity components, volume fraction, `k`, and epsilon `1e-3` |
| Initialization | Hybrid-style initialization in the working branch; the exact initialization transcript was not extracted. The archive/replay comparison records `patch_reconstructed_interface = false` versus `true`, so this remains a replay difference. |
| Mesh-study endpoint | Nominal `3,000` iterations, with within-run monitor stability still required before endpoint differences can be interpreted as mesh effects. |

#### DPM settings associated with the 08b rebuild

| DPM setting | Recorded value | Evidence / interpretation |
|---|---|---|
| Activity in the original live archive | No active injections | `Observed`; the original carrier setup alone does not prove the historical injection implementation. |
| Rebuilt injection layer | Nine surface injections through the steam-side inlet, total approximately `116.91 kg/s` in the extracted payload | `Observed` from the particle extract; this is a rebuild layer, not an active part of the carrier-only mesh checkpoint. |
| Particle and injection type | Inert particles, liquid material, surface injection; `numpts = 2`; `ntries = 1`; all initial velocity components `0` | `Observed` in the extracted payload. |
| DPM interaction with continuous phase | `Off` | `User-specified` one-way baseline for the parity-rebuild branch; it is not part of the carrier-only mesh-selection calculation. |
| Unsteady tracking | `Off` | `Inferred` from the steady carrier workflow; verify in the final case. |
| High-resolution tracking | `On` | `User-specified numerical-quality choice for the curved/swirl flow, not a claimed historical Purnanto setting. |
| Pressure force and virtual mass | Both `On` | `Observed` in the archive/replay comparison. |
| Turbulent dispersion, stochastic/random eddy, rotation, rough-wall treatment | `Off` | `Observed` in the extracted payload. |
| Breakup, coalescence, wall-film coupling, UDF/custom laws | `Off` | `User-specified` least-assertive baseline; none is evidenced in the recovered payload. |
| Tracking limits | Maximum steps `10,000`; step-length factor `5` | `Observed` archive/replay values. |
| Drag law | `Spherical` in the extracted payload; the current rebuild decision is to replace a `Stokes-Cunningham` field if that is what the Fluent panel shows | `Observed` extracted intent; verify the exact Fluent 2024 R2 field before labelling it as a readback. |

The associated mesh result should therefore be read as: **a pressure-based, two-phase carrier-field comparison with a split inlet, not a converged DPM/EWF result**. The residual and monitor evidence remains unresolved, and the larger meshes require more iterations to reach a comparable state.

### B.2 010V2d — combined wall-film interaction, global DPM interaction off

**010V2d** is the combined wall-film branch used as the control for the global-DPM comparison. It inherits the fixed transient and film controls from the clean `010V2` wall-film setup, then combines only the EWF mechanisms that were accepted from the isolated branches. The historical diagnostic checkpoint was captured on Fluent `2024 R2`, server `1`, at `5,000` iterations. ([010V2d setup definition](../experiments/purnanto-010V2d-ewf-combined-mechanisms/setup.md), [010V2d results](../experiments/purnanto-010V2d-ewf-combined-mechanisms/results.md))

#### Inherited carrier and DPM controls

| Setting group | 010V2d value | Why it matters |
|---|---|---|
| Carrier model | Same project two-phase `Mixture` carrier basis, split inlet, project materials, RNG `k-epsilon`, Energy `Off`, and accepted mesh/wall definitions | These settings are inherited from the parent and should not change when comparing `010V2d` with `010V2d-2`. |
| Historical DPM allocation | Six legacy injection classes; nominal `5%` of the `116.920 kg/s` liquid feed: `5.846 kg/s` tracked and `111.074 kg/s` continuum liquid | This is the legacy distribution used by the diagnostic result. It is not the new seven-bin fine-mist distribution in the main report. |
| Global DPM interaction | `Off` | The defining control value for `010V2d`. |
| Particle tracking | Unsteady tracking `Off`; remove the old `0.001 s` particle-time-step override; maximum DPM steps `10,000` | The three items are the required parent correction before a clean comparison. |
| DPM material and wall path | Use the verified project DPM/film material identities; couple impacted droplets through the wall-film path on the confirmed film wall | Material names and wall interaction must be read back because a material mismatch can change deposition without changing the nominal flow rate. |

#### Eulerian Wall Film and transient settings

| Fluent setting | Recorded value | Evidence / interpretation |
|---|---|---|
| EWF model | `On`; DPM coupling `On` | `Observed`/inherited control. |
| Film wall | `wall` only is confirmed as the EWF wall; `bottom` is not the EWF wall and retains a DPM trap role | `Observed` in the diagnostic readback. |
| Impingement and initial film | `Stanton–Rutland` impingement; initial film height `0 m`; initial film velocity `0 m/s` in all components | `Observed` wall-level readback. |
| Film momentum model | Solve Momentum `On`; Momentum Equation; gravity force `On`; surface shear force `On`; pressure gradient `On` if exposed | The first three are inherited project settings; pressure-gradient availability must be recorded in the active Fluent panel. |
| Optional EWF mechanisms | Combined branch uses the accepted subset of splash, edge separation, and stripping. The 5,000-iteration readback confirms splash with four splashed particles and permits film-boundary separation; root-level stripping readback remains unavailable. | `Observed` where the API exposes it; unavailable values are not interpreted as `Off`. |
| Other first-control switches | Spreading `Off`; surface tension `Off`; EWF energy/scalar `Off`; phase/VOF coupling `Off`; wall flow-momentum coupling `Off`; coupled solution `Off` | `Observed`/inherited controls from `010V2`; read back again if the branch is rebuilt. |
| Flow time stepping | Transient, first-order implicit; fixed flow timestep `1.0e-5 s`; `40` configured steps; `1` iteration per step | `Observed` intended live-case control. Do not change this while diagnosing a film-CFL or source spike. |
| Film control | Maximum Courant number `0.5` as a conservative assumed starting value if exposed; per-flow iterations `1`; reporting interval `1`; sub-iterations `10`; sub-iteration stop `1e-8`; DPM per film steps `20`; EWF DPM relaxation `0.5` as an assumed starting value | Values marked assumed require panel readback before they are treated as exact case settings. |
| Film step adaptation | Leave Fluent increase/decrease factors at their defaults and record them; do not enable adaptive stepping as an unlabelled change | Keeps the global-interaction comparison interpretable. |

#### What the 010V2d diagnostic actually established

| Checkpoint quantity | Documented value | Limitation |
|---|---:|---|
| Solver state | `5,000` iterations; Fluent `2024 R2`, server `1` | Final snapshot, not an interval history. |
| Global DPM interaction | `Off` | Confirmed by the audit. |
| Film wall / impingement | `wall` / `Stanton–Rutland` | Top-level EWF Settings API is incomplete. |
| Film inventory | `0.20221152 kg` | Current inventory only; no time-integrated closure. |
| Maximum / area-average film thickness | `0.457306 mm` / approximately `3.425 µm` | Local and distributed final-state measures. |
| Maximum film CFL | `5.0655e-3` | Final-state numerical diagnostic only. |
| Selected-surface carrier imbalance | Approximately `57.54%` | The flux scope is incomplete, so this is not a full-domain mass balance. |

The `10,000`-iteration continuation reached approximately `0.2884 kg` film inventory, `0.614 mm` maximum thickness, and CFL `3.03`, while continuity also worsened. That is why 010V2d does not yet provide a defensible iteration-based stopping point for the wall film. ([iteration-continuation observation](../observations/06-010v2-iteration-continuation.md))

### B.3 010V2d-2 — same combined wall film with global DPM interaction on

**010V2d-2** is intended to inherit the accepted 010V2d state and change one physics switch: `DPM Interaction with Continuous Phase = On`. The branch also retains source updates every flow iteration with a DPM iteration interval of `1`. This is the relevant coupling sensitivity, but the available checkpoints are not a strict same-iteration restart pair. ([010V2d-2 setup definition](../experiments/purnanto-010V2d-2-ewf-global-dpm/setup.md), [010V2d-2 results](../experiments/purnanto-010V2d-2-ewf-global-dpm/results.md), [global-interaction comparison](../observations/05-010v2d-global-dpm-interaction.md))

#### Controlled settings

| Setting | 010V2d-2 value | Must remain unchanged from 010V2d |
|---|---|---|
| Global DPM interaction with continuous phase | `On` | This is the intended controlled change. |
| DPM source updates | Every flow iteration: `On` | Retained parent value. |
| DPM iteration interval | `1` | Retained parent value. |
| EWF wall and film model | Same `wall` film wall, Stanton–Rutland impingement, film material, zero initial film state, and combined accepted mechanism set | Do not alter the wall-film branch while testing global interaction. |
| Transient controls | Same fixed `1.0e-5 s` flow timestep, `40` configured steps, `1` iteration per step, film schemes, and source under-relaxation | A timestep or scheme change would create a second sensitivity variable. |
| DPM tracking | Unsteady tracking `Off`; no `0.001 s` particle-time override; maximum steps `10,000` | Corrected parent control. |
| Injection payload | Historical six-bin legacy PSD, including the dominant `348.88 µm` class | Keep fixed for the legacy interaction comparison; the new seven-bin fine-mist PSD belongs in a separately named child case. |

#### Available 4,189-iteration readback

| Checkpoint quantity | Value | Interpretation limit |
|---|---:|---|
| Evidence identity | Fluent `2024 R2`, server `3`, monitor iteration `4,189` | Different server and final iteration from the 010V2d `5,000` checkpoint. |
| Global DPM interaction | `On`; source update every iteration; interval `1` | Confirmed controlled setting. |
| Film wall and splash | `wall`; Stanton–Rutland; four configured splashed particles | Root-level edge/separation/stripping flags remain unavailable through the adapter. |
| Film inventory | `0.1691669 kg` | Final inventory only; no interval closure. |
| Maximum / area-average film thickness | `0.511775 mm` / `2.865 µm` | Final-state local and distributed measures. |
| Maximum film CFL | `5.6902e-3` | Final-state numerical diagnostic only. |
| Selected-surface carrier imbalance | `57.5405%` | Scoped phase-flux diagnostic, not a closed full-domain balance. |
| Continuity residual | `6.043e-3` | Does not establish carrier convergence. |

The historical control allocation is nominally `5.846 kg/s` tracked droplets plus `111.074 kg/s` continuum liquid. The 4,189-iteration comparison artifact reports approximately `5.91841 kg/s` for the six-injection represented total, while the 5,000-iteration 010V2d artifact reports approximately `5.95951 kg/s`. These are small but real payload differences, so fate comparisons must be normalised by the actual reported injection total at each checkpoint rather than by nominal `5%` alone.

#### Comparison integrity and next paired run

| Comparison item | 010V2d | 010V2d-2 | Consequence |
|---|---|---|---|
| Global DPM interaction | `Off` | `On` | Intended primary difference. |
| Source-update rule | Not active globally | Every flow iteration, interval `1` | Intended coupling difference. |
| Final documented checkpoint | `5,000` iterations | `4,189` iterations | Not a matched physical-time or iteration comparison. |
| Fluent evidence server | Server `1` | Server `3` | Restart/checkpoint identity is not fully proven from the read-only artifacts. |
| Film source and closure histories | Not available | Not available | Film inventory differences cannot yet be attributed solely to global DPM interaction. |

For the next decisive run, create two copies from one saved, read-back-verified 010V2d checkpoint. Keep the mesh, carrier settings, transient timestep, EWF flags, wall condition, materials, injection diameters, per-bin masses, DPM tracking controls, and monitor definitions identical. Turn global interaction on in only one copy, then compare the same physical-time interval using direct DPM-to-carrier source, DPM-to-film source, film inventory, film outflow, thickness, CFL, residual, and particle-fate histories. The current 010V2d-2 result is therefore a **configuration-level diagnostic**, not yet a decisive causal A/B result.

The historical 010V2d-2 result must also not be described as using the new fine-mist distribution. Once supervisor approval is obtained for the provisional `5–100 µm` seven-bin distribution, create a new child case and change only the injection diameters and relative mass weights while preserving the global-interaction and EWF controls above.
