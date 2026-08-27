> **Retired source:** Setups/past/reported/08b-purnanto-parity-split-inlet-rebuild.md
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# Purnanto Parity Split-Inlet Rebuild

## Setup metadata

| Field | Value |
|---|---|
| Setup ID | `08b` |
| Lifecycle | `reported` |
| Role | parity-reset split-inlet rebuild |
| Parent setup | [00a](../purnanto-00a-live-setup-audit/setup.md) |
| Child setups | [08c](../purnanto-08c-inlet-loading-sensitivity/setup.md), [09a](../purnanto-09a-dpm-deterministic-carryover/setup.md) |
| Evidence-use label | scoped steam-carryover screening; DPM debug evidence |
| Outcome | needs follow-up |
| Linked report | [08b results](results.md) |

## 1. Purpose

Define setup `08b` as the extraction-first parity rebuild branch for the current project.

This branch exists because setup `07` is no longer trusted as the closest reconstruction of the original Purnanto Fluent setup, while setup `08` proved a useful one-inlet PyFluent scaffold but does not yet answer the current project question:

- preserve the actual observed Purnanto Fluent setup as closely as possible;
- change only the inlet representation needed for the project's two-phase inlet objective;
- rebuild `DPM` from extracted evidence rather than from memory;
- use that rebuilt branch, not setup `07`, as the next verification and validation target.

Primary authority:

- [00a-purnanto-setup-5000-live-audit.md](../purnanto-00a-live-setup-audit/setup.md)
- [08-purnanto-one-inlet-massflow-recreation.md](../purnantov2-08-one-inlet-massflow-recreation/setup.md)
- [live setup reference](../purnanto-00a-live-setup-audit/technical-live-setup-reference.md)
- [Project state and next decision](../../index.md)

## 2. Setup Identity

| Item | Value |
|---|---|
| Setup order | `08b` |
| Branch role | active parity-reset and V&V candidate |
| Parent authority | live audited Purnanto setup `00a` with local one-inlet rebuild lessons from `08` |
| Geometry label | `purnanto` |
| Continuous-phase intent | preserve observed Purnanto solver/model/numerics stack unless extraction proves otherwise |
| Inlet representation | two-zone split inlet for project two-phase inlet study |
| DPM intent | preserve observed DPM model settings where present; reconstruct injections only after extraction confirms what is actually missing |
| Evidence-use label | extraction-first parity rebuild |

Evidence labels used in this report:

- `Observed`: taken from the loaded Purnanto case/data audit.
- `Retained`: kept intentionally from the observed Purnanto setup.
- `User-specified`: deliberate project change from the observed Purnanto setup.
- `Assumed`: temporary placeholder until the extraction workflow proves the value.
- `Uncertain`: known unresolved item that must not be treated as settled parity.

### 2.1 Base geometry and mesh for `08b` onward

The following mesh is the shared base for setup `08b` and later setup/simulation branches unless a later setup record explicitly documents a mesh change:

| Item | Value | Evidence label |
|---|---:|---|
| Geometry | `Purnanto` | `User-reported` |
| Base mesh file/target | `purnanto-extended.msh` | `Existing 08b automation target` |
| Nodes | `1,309,312` | `User-reported` |
| Cells | `7,601,261` | `User-reported` |
| Minimum orthogonal quality | `0.2` | `User-reported` |
| Maximum aspect ratio | `18.4` | `User-reported` |

Mesh inheritance rule:

- `08b` and later descendants inherit this geometry/mesh as their base.
- The controlled differences between those branches are Fluent settings, such as boundary conditions, models, numerics, DPM, coupling, or wall-film options.
- A later mesh replacement, remesh, or geometry change must be recorded
  explicitly in the child Project setup record.

The mesh statistics are recorded as user-provided setup metadata; they are not by themselves a mesh-independence or solution-acceptance result.

### 2.2 Purnanto reference mesh

The Purnanto source/live-audit mesh uses the same `Purnanto` geometry but a different mesh from the `08b`-onward project base mesh:

| Item | Value | Evidence label |
|---|---:|---|
| Geometry | `Purnanto` | `Observed` |
| Nodes | `572,556` | `Observed` in the existing Purnanto live audit |
| Cells | `2,964,593` | `Observed` / `User-reported` |
| Minimum orthogonal quality | `0.2776` | `User-reported`, rounded from the audit value `0.277635` |
| Maximum aspect ratio | `12.889` | `User-reported`, rounded from the audit value `12.8899` |

This is the Purnanto reference mesh for parity comparison. It is not the inherited base mesh for `08b` and later project descendants unless a setup explicitly records that mesh switch.

Node-count clarification: the latest user message supplied `5722556` without separators. This record interprets that as `572,556` because it matches the existing Purnanto live-audit record and the associated `2,964,593`-cell mesh. Confirm and revise if `5,722,556` was intended.

## 3. Deliberate Change Budget

This branch is allowed to change only two setup ideas at first:

1. replace the single mixed `Mass-Flow Inlet` with a two-zone inlet representation suited to the project;
2. add project DPM injections through the steam-side inlet only after the original Purnanto DPM settings are extracted and compared.

Everything else should default to:

```text
match the observed Purnanto case first,
then document each intentional deviation explicitly
```

## 4. Continuous-Phase Parity Rule

Treat the observed Purnanto case as the authority for:

- solver family;
- steady/transient mode;
- multiphase model;
- turbulence model;
- gravity and operating pressure;
- material properties;
- discretization schemes;
- under-relaxation factors;
- outlet settings;
- any named cell-zone or wall setting that survives on the current geometry.

Do not inherit those settings from setup `07` if they disagree with the live Purnanto audit.

## 5. Inlet Rule For Setup 08b

### Continuous-flow target

Keep the Purnanto target phase flows:

- vapor `80.69 kg/s`
- liquid `116.92 kg/s`

### Geometric/inlet interpretation

Use a split inlet that maps the project hypothesis:

- outer-wall side = liquid-dominant inlet zone
- inner/core side = steam-side inlet zone

Boundary-type rule:

- `Uncertain`: do not freeze the boundary type as `Velocity Inlet` or split `Mass-Flow Inlet` purely from memory;
- extract what Fluent allows cleanly on the chosen mesh branch and preserve parity with the observed one-inlet case as far as possible;
- if the final branch uses split `Velocity Inlet` zones, record that as a `User-specified` deviation rather than calling it observed Purnanto parity.

Current branch decision after local case inspection:

- `User-specified`: the active `08b` rebuild keeps the split inlet as two `Mass-Flow Inlet` boundaries rather than converting the branch to split `Velocity Inlet`;
- `Retained`: this is intentionally aligned with the setup-family logic already used in setup `07`, where the split-inlet areas and target phase flow rates were calculated directly and then imposed through mass-flow inlet control;
- do not treat the presence of split `Mass-Flow Inlet` zones in the current `08b` case as an accidental setup drift by itself.

## 6. DPM Rule For Setup 08b

Observed starting point from the live audit:

- `Observed`: `DPM` model settings exist in the saved Purnanto case.
- `Observed`: the saved case has no active injections.

This means:

- do not claim the original Purnanto injection implementation is already known;
- do not copy setup `07` injections into this branch and call them parity;
- first extract the full live DPM model tree, then recreate only the settings that are actually present;
- add project injections through the steam-side inlet as a new controlled layer once the carrier setup is accepted.

Initial project rule for the added injections:

- injection origin = steam-side inlet zone
- particle material = water-droplet surrogate matched to the liquid phase unless extraction proves a different legacy material was used
- injection diameters/counts = `Uncertain` until extracted or explicitly chosen as a project sensitivity set

Observed extracted DPM payload from `purnanto-enthalpy1600-particle-extract/injections.json`:

- injection count: `9`
- total injected mass flow: `116.91 kg/s`
- common settings across all nine entries:
  - `particle_type = inert`
  - `material = water-liquid`
  - `injection_type = surface`
  - `injection_surfaces = steaminlet` in the rebuilt case
  - `numpts = 2`
  - `ntries = 1`
  - `stochastic-on = false`
  - `random-eddy-on = false`
  - `use-face-normal = false`
  - velocity components: `x-vel = 0.0`, `y-vel = 0.0`, `z-vel = 0.0`
- archive metadata present in every extracted entry:
  - `surfaces = 2`
  - `boundary = 30047`
  - `dpm-fname` blank in the extracted payload

| Injection name | Diameter [m] | Diameter [micron] | Mass flow [kg/s] | Share of total |
|---|---:|---:|---:|---:|
| `injection-5-micron` | `5.63e-06` | `5.63` | `0.19` | `0.16%` |
| `injection-28-micron` | `2.814e-05` | `28.14` | `0.78` | `0.67%` |
| `injection-56-micron` | `5.627e-05` | `56.27` | `0.97` | `0.83%` |
| `injection-112-micron` | `0.00011254` | `112.54` | `1.95` | `1.67%` |
| `injection-168-micron` | `0.000168811` | `168.81` | `1.95` | `1.67%` |
| `injection-348-micron` | `0.00034888` | `348.88` | `23.38` | `20.00%` |
| `injection-562-micron` | `0.0005627` | `562.70` | `29.23` | `25.00%` |
| `injection-844-micron` | `0.00084406` | `844.06` | `29.23` | `25.00%` |
| `injection-1631-micron` | `0.00163184` | `1631.84` | `29.23` | `25.00%` |

Rebuild interpretation:

- the script preserves the extracted diameters, mass-flow split, and common DPM toggles;
- the archive payload does not provide a strong reason to treat any injection as anything other than a steam-side surface source in the rebuilt case;
- the explicit runtime replay now omits the extra material-bootstrap and stream-override steps because they were not needed for a clean rebuild on the Student Edition machine.

## 7. Required Extraction Workflow

Before using setup `08b` for V&V, complete this order:

1. export the live Purnanto setup tree from Fluent through `PyAnsys`;
2. compare exported settings against the existing human-written setup notes;
3. build a machine-readable parity checklist for:
   - models
   - materials
   - phases
   - boundary conditions
   - numerics
   - DPM model settings
4. rebuild the continuous field on the local/current mesh with only the split-inlet change active;
5. read back the applied settings after each parent-model activation;
6. only then add DPM injections through the steam-side inlet.

## 8. Acceptance Gate

Treat setup `08b` as ready for V&V only when:

1. extracted-versus-rebuilt continuous-phase settings are reconciled or explicitly bounded;
2. inlet phase targets match the intended values closely enough to treat the branch as correctly imposed;
3. residual and monitor behavior is stable enough for comparison;
4. the DPM model state is rebuilt from extracted evidence rather than guessed memory;
5. any remaining unknown injection detail is labeled `Uncertain` and scoped as a sensitivity, not as exact historical parity.

## 9. What Setup 08b Replaces

For project decision-making:

- setup `07` becomes comparison-only context, not the next primary V&V parent;
- setup `08` remains a useful one-inlet automation scaffold and parity-check sandbox;
- setup family `09` stays reserved for later DPM sensitivity work after a trusted parity-reset branch exists.

## 10. Immediate Build Questions

Use setup `08b` to answer these questions in order:

1. What settings in setup `07` actually drifted away from the live Purnanto case?
2. Can Python export and replay the true Purnanto continuous-phase setup reliably enough to remove manual setup error?
3. Once that parity is recovered, does the split-inlet project variant still behave acceptably?
4. After that, what is the minimum justified DPM injection definition through the steam-side inlet?

## 11. Extraction Comparison

This section compares:

- the archived live 1680J setup at `PyAnsys/cases/actual_setup_archives/purnanto-enthalpy1680-live-extract/live/settings_root_tree.json`;
- the rebuilt case/data replay exported from `purnanto-extended-rebuilt.cas.h5` and `purnanto-extended-rebuilt.dat.h5`;
- the detailed 1600 particle report already captured in this branch note.

### 11.1 What Matches Cleanly

The rebuilt replay preserves the main continuous-phase authority from the live 1680J archive:

- solver family remains pressure-based and steady;
- multiphase remains mixture with 2 phases;
- energy remains off;
- viscous model remains RNG `k-epsilon` with standard wall treatment, differential viscosity model, and swirl-dominated flow enabled;
- species remains off with the same phase-material mapping;
- outlet pressure remains `1120000 Pa` with `Total Pressure` backflow specification;
- DPM max steps, step-length-factor, pressure-force, and virtual-mass settings now read back the same as the archive;
- the rebuilt carrier phase still targets the same broad physical stack as the original archive, but the exported tree is more explicit in how Fluent 2026 R1 serializes the active branches.

### 11.2 Deliberate or Observed Differences

| Area | Original 1680J archive | Rebuilt replay | Interpretation |
|---|---|---|---|
| Solver family | pressure-based, steady | pressure-based, steady | matches |
| Multiphase model | mixture, 2 phases | mixture, 2 phases | matches |
| Energy model | off | off | matches |
| Viscous model | RNG `k-epsilon`, standard wall function, differential viscosity on, swirl-dominated flow on | same physics, exported with a more explicit Fluent 2026 R1 tree | matches in intent |
| Species model | off, `water-vapor-at-psep` / `water-liquid-at-psep` | off, same phase-material mapping | matches |
| Outlet pressure | `1120000 Pa` | `1120000 Pa` | matches |
| Inlet topology | single `mass_flow_inlet.inlet` | split `velocity_inlet.liquidinlet` and `velocity_inlet.steaminlet` | intentional project change |
| Outlet topology | `pressure_outlet.outlet` | `pressure_outlet.steamoutlet` | mesh aliasing change |
| Wall topology | `wall.wall-fluid` | `wall.wall` and `wall.bottom` | mesh aliasing change |
| Operating density | `mixture-averaged` | `minimum-phase-averaged` | still drifting in Fluent 2026 R1 replay |
| Operating temperature | `298.15 K` | not serialized in the rebuilt export | still missing from replay export |
| DPM activity | no active injections | 9 active surface injections on `steaminlet` | rebuilt from the 1600 extract |
| DPM model forces | pressure force on, virtual mass on | pressure force on, virtual mass on | matches after direct replay |
| DPM tracking | `max_num_steps = 10000`, `step-length-factor = 5` | `max_num_steps = 10000`, `step-length-factor = 5` | matches after direct replay |
| Initialization patch | `patch_reconstructed_interface = false` | `patch_reconstructed_interface = true` | still a replay difference |
| Continuity monitor | `absolute_criteria = 0.0001` | `absolute_criteria = 0.001` | still a run-control difference |
| Injection payload | none | 9 injections, `116.91 kg/s` total | detailed table below |

### 11.3 DPM Injection Inventory

The original 1680J archive contains no active injections, so the injection inventory below comes entirely from the 1600 particle extract and is the intended DPM layer for setup `08b`.

Common parameters across all 9 injections:

- `particle_type = inert`
- `material = water-liquid`
- `injection_type = surface`
- `injection_surfaces = steaminlet`
- `numpts = 2`
- `ntries = 1`
- `stochastic-on = false`
- `random-eddy-on = false`
- `use-face-normal = false`
- velocity components all `0.0`
- `particle_drag = spherical`
- `turbulent_dispersion = false`
- `particle_rotation = false`
- `rough_wall_treatment_enabled = false`
- `custom_laws.enabled = false`
- `custom_laws.law_1 = inert-heating`

| Injection name | Diameter [micron] | Mass flow [kg/s] | Share of total |
|---|---:|---:|---:|
| `injection-5-micron` | `5.63` | `0.19` | `0.16%` |
| `injection-28-micron` | `28.14` | `0.78` | `0.67%` |
| `injection-56-micron` | `56.27` | `0.97` | `0.83%` |
| `injection-112-micron` | `112.54` | `1.95` | `1.67%` |
| `injection-168-micron` | `168.81` | `1.95` | `1.67%` |
| `injection-348-micron` | `348.88` | `23.38` | `20.00%` |
| `injection-562-micron` | `562.70` | `29.23` | `25.00%` |
| `injection-844-micron` | `844.06` | `29.23` | `25.00%` |
| `injection-1631-micron` | `1631.84` | `29.23` | `25.00%` |

Total injected mass flow: `116.91 kg/s`.

This matches the detailed injection table already captured in this report and confirms that the rebuilt DPM layer is the same 9-particle-size split recorded from the 1600 extract.

### 11.4 Provisional DPM Decision Log For The Fluent 2024 R2 Rebuild

The items below are the currently unresolved or partly extracted DPM settings that must be fixed for setup `08b` before the two-zone inlet branch is treated as a stable parity rebuild.

Decision rule:

- if the live archive or extracted payload already proves a value, keep it;
- if the setting would add extra physics beyond the observed Purnanto carrier-field workflow, leave it off for `08b`;
- if Fluent forces a choice for a missing item, choose the least-assertive one-way baseline and label it `User-specified`.

| Setting group | 08b choice | Evidence label | Decision |
|---|---|---|---|
| Interaction with continuous phase / update DPM sources | `Off` | `User-specified` | Keep `08b` as one-way DPM over a solved steady carrier field. The original 1680J archive had no active injections, so there is no parity basis for letting droplets feed momentum or mass back into the carrier solution in this branch. |
| Unsteady particle tracking | `Off` | `Inferred` | Keep particle tracking steady/frozen because the carrier solution for `08b` is pressure-based steady and Purnanto-style DPM is a post-convergence tracking layer, not a transient particle-release study. |
| High-resolution tracking | `On` | `User-specified` | Turn this on for the rebuilt split-inlet branch because the separator has strong swirl and curved trajectories. This is a numerical-quality choice, not a claimed historical parity setting. |
| Pressure force | `On` | `Observed` | Keep as extracted from the archive/replay comparison. |
| Virtual mass force | `On` | `Observed` | Keep as extracted from the archive/replay comparison. |
| Turbulent dispersion | `Off` | `Observed` | Keep off. The extracted injection payload reports `turbulent_dispersion = false`, `stochastic-on = false`, and `random-eddy-on = false`. |
| Stochastic tracking / random eddy model | `Off` | `Observed` | Keep off for `08b`. If later sensitivity work needs turbulent dispersion, move it into setup family `09`, not the parity-reset branch. |
| Particle rotation | `Off` | `Observed` | Keep off because the extracted injection payload reports `particle_rotation = false`. |
| Rough-wall particle treatment | `Off` | `Observed` | Keep off because the extracted injection payload reports `rough_wall_treatment_enabled = false`. |
| Breakup / coalescence / wall-film coupling | `Off` | `User-specified` | Leave all advanced secondary droplet physics off in `08b`. None of these are evidenced in the extracted Purnanto payload, and they would shift the branch from parity rebuild into model-development work. |
| User-defined functions / custom laws | `Off` | `Observed` | Keep disabled. The extracted injection payload reports `custom_laws.enabled = false`. |
| Maximum tracking steps | `10000` | `Observed` | Keep the archive/replay value as the first `08b` target. If incomplete tracks remain significant on the split-inlet geometry, raise only as a logged recovery deviation. |
| Step length factor | `5` | `Observed` | Keep the archive/replay value as the first `08b` target. |
| Number of tries | `1` | `Observed` | Keep the extracted injection value while stochastic tracking remains off. |
| Parcel count / `numpts` | `2` | `Observed` | Keep the extracted injection value for parity with the recovered 1600 injection payload. |
| Averaging | leave default / not used | `User-specified` | Do not add transient or statistical averaging logic to `08b`; this branch is a steady carrier + DPM tracking rebuild. |
| Interaction range | leave default / inactive | `User-specified` | Do not activate extra particle-interaction logic unless a later dense-DPM or collision model is intentionally introduced. |

### 11.5 Injection Momentum-Exchange Choice

Current rebuild decision for the injection drag / momentum-exchange law:

- change the current injection-side `Stokes-Cunningham` choice to `Spherical`;
- label this as `Observed` if the Fluent 2024 R2 field matches the extracted payload name exactly, otherwise label it `Retained from extracted replay intent`.

Reason:

- the extracted injection payload already reports `particle_drag = spherical`;
- the smallest recovered droplet bin is about `5.63 um`, and the remaining bins are much larger, so this branch does not need a slip-correction-first drag choice as its baseline claim;
- keeping `Spherical` is also the cleaner parity decision because it matches the recovered rebuild payload instead of a guessed Fluent default.

### 11.6 Apply-Now Working Rule

Until a fuller Fluent tree export proves otherwise, apply DPM in setup `08b` with this minimal working package:

```text
one-way DPM
unsteady particle tracking = off
high-resolution tracking = on
pressure force = on
virtual mass = on
stochastic / random eddy / turbulent dispersion = off
particle rotation = off
rough-wall treatment = off
custom laws / UDFs = off
drag law = spherical
max_num_steps = 10000
step-length-factor = 5
```

Recovery rule:

- if `incomplete` particles are still large on the two-zone geometry, first increase `max_num_steps`;
- only if that fails should `step-length-factor` or other tracking controls be changed;
- any such change must stay logged as a split-inlet rebuild deviation, not as proven Purnanto parity.

### 11.7 Staged Injection-Test Rule

For the next practical Fluent 2024 R2 test pass, use a staged subset of the recovered injection bins instead of running the full 9-bin set immediately.

Stage-1 working set:

- inject only the recovered steam-side bins up to and including `168.81 um`:
  - `5.63 um`
  - `28.14 um`
  - `56.27 um`
  - `112.54 um`
  - `168.81 um`

Stage-1 interpretation:

- `User-specified`: this is a cost-control and screening choice for the rebuilt split-inlet branch, not a new claim about the original Purnanto injection inventory;
- `Inferred`: if the `168.81 um` bin does not show meaningful escape through the steam outlet, the larger recovered bins are less likely to control first-pass steam-carryover conclusions in this branch.

Stage-2 escalation trigger:

- if the `168.81 um` injection shows non-negligible steam-outlet escape, then extend the test to the larger recovered bins:
  - `348.88 um`
  - `562.70 um`
  - `844.06 um`
  - `1631.84 um`

Boundary note:

- keep all tested bins on `steaminlet` for `08b`;
- do not move the larger bins to `liquidinlet` inside this branch unless a separate non-parity hypothesis is being created and logged explicitly.

Limitation note:

- this staged rule is a practical screening shortcut, not proof that the larger bins are physically absent from entrained steam;
- if later evidence, supervisor direction, or early trajectories suggest coarse-bin escape remains plausible, rerun the larger recovered bins and log the branch as expanded beyond the minimum screening set.

### 11.8 Live 5000-Iteration Post-Processing Result On The Applied Split-Inlet Case

Live post-processing was run against the already-loaded Fluent 2024 R2 case/data pair:

- case: `C:\Users\syok443\Documents\TwoPhaseInletV2(Purnanto)\TwoPhaseInletV2(Purnanto)-25-05000.cas.h5`
- data: `C:\Users\syok443\Documents\TwoPhaseInletV2(Purnanto)\TwoPhaseInletV2(Purnanto)-25-05000.dat.h5`
- machine-readable summary: `PyAnsys/output/live_postprocess/TwoPhaseInletV2(Purnanto)-25-05000-summary.json`
- human-readable summary: `PyAnsys/output/live_postprocess/TwoPhaseInletV2(Purnanto)-25-05000-report.md`

Observed carrier-field phase-flux report from the saved `5000`-iteration field:

| Quantity | Value |
|---|---:|
| Liquid inlet mass flow | `116.92 kg/s` |
| Steam/vapor inlet mass flow | `80.69 kg/s` |
| Steam outlet liquid mass flow | `0.082132007 kg/s` |
| Steam outlet vapor mass flow | `81.464165 kg/s` |
| Flux-based steam-line liquid removal `eta_phase = 1 - m_liq,steam_out / m_liq,in` | `0.9992975367` |
| Steam-outlet dryness `x_out` | `0.9989928175` |
| Mixture inlet total used by the live report | `197.61 kg/s` |
| Mixture outlet total used by the live report | `81.546281 kg/s` |
| Mixture mass imbalance magnitude | `116.063719 kg/s` |
| Mixture mass imbalance ratio relative to reported inlet mixture flow | `0.5873372754` |

Interpretation:

- `Observed`: the steam-line liquid carryover signal is small relative to the liquid inlet flow.
- `Observed`: the same live report still shows a very large whole-domain mixture imbalance because the current branch has only the steam outlet in the exported flux summary and is not closing the lower liquid inventory through a separate drain or brine outlet.
- `Inferred`: treat the `99.93 %` flux-based liquid-removal number as a **scoped steam-line carryover diagnostic**, not as a full separator mass-balance efficiency result for setup `08b`.
- `User-specified`: this branch remains acceptable as a split-inlet / steam-carryover screening case, but not yet as a report-quality quantitative validation result.

### 11.9 Live DPM Summary On The Current 6 Active Injections

After the post-processing pass, Fluent was instructed to refresh the DPM summary on the already-loaded field using `/solve/dpm-update`.

Active injections present in the loaded case:

- `injection-5-micron`
- `injection-28-micron`
- `injection-56-micron`
- `injection-112-micron`
- `injection-168-micron`
- `injection-348-micron`

User-scoped limitation for this pass:

- `User-specified`: the larger recovered bins `562.70 um`, `844.06 um`, and `1631.84 um` were intentionally not included in the active test set for this run.
- `Inferred`: any DPM interpretation below is therefore a **partial-bin diagnostic** only, not the full recovered 9-bin Purnanto-style injection inventory.

Observed aggregate DPM summary after the update:

| Fate | Aggregate count / report value | Interpretation |
|---|---:|---|
| `Incomplete` | `13012` particles | dominant outcome |
| `Escaped` | `8` particles at `steamoutlet` | direct steam-line carryover in the current active 6-bin set |
| `Trapped` | no row reported | treat as `0` reported trapped particles in this summary pass |
| Escaped represented mass flow | `7.005e-04 kg/s` | very small escaped mass relative to the active represented total |
| Incomplete represented mass flow | `2.922e+01 kg/s` | almost the entire active represented mass remains unresolved by tracking completion |

Observed / inferred detail from the live summary text:

- `Observed`: Fluent reports only `Incomplete` and `Escaped` rows in the refreshed summary output.
- `Observed`: the escaped particles leave through `steamoutlet` zone `50065`.
- `Inferred`: because no `Trapped` row was printed, this pass should be read as having **no reported trapped-particle fate in the aggregate summary output**.
- `Inferred`: the escaped-row injection index range points to `injection-5-micron`, so the small amount of completed escape appears to come from the finest active bin in this pass.
- `Inferred`: the incomplete-row index range spans from `injection-5-micron` to `injection-348-micron`, so incomplete tracking is affecting multiple active bins rather than just one coarse-bin outlier.

Interpretation for setup `08b`:

- `Observed`: the current DPM tracking result is not strong carryover evidence because the incomplete count (`13012`) dominates the finished escaped count (`8`).
- `Inferred`: the dominant uncertainty is still tracking completion, not direct evidence that the current active 6-bin set is cleanly trapped or cleanly escaped.
- `User-specified`: do **not** promote this pass to a report-quality DPM efficiency claim.
- `User-specified`: keep the result as `Debug only` / screening evidence for the active 6-bin subset on the saved `5000`-iteration carrier field.

Immediate recovery rule after this live DPM pass:

1. if a stronger DPM claim is needed, rerun the same active injections with a higher tracking budget before expanding the physics model;
2. change `max_num_steps` first, because the current result is dominated by `Incomplete`;
3. only after tracking completion improves should per-bin escape/trap interpretation be treated as stronger evidence;
4. if finer attribution is needed, export or capture the per-injection zone summaries rather than relying only on the aggregate `dpm-summary` output.

### 11.10 Injection-By-Injection `dpm-sample` Check On The Current 6 Active Injections

The user confirmed that the manual diagnostic was performed one injection at a time through Fluent `Results > Reports > Discrete Phase > Sample`.

To match that workflow without rebuilding the setup, the already-loaded live case was post-processed again through Fluent `report/dpm-sample`, one active injection at a time, using `steamoutlet` as the selected reporting boundary.

Observed per-injection result:

| Injection | Diameter | Tracked | Escaped | Trapped | Incomplete | Interpretation |
|---|---:|---:|---:|---:|---:|---|
| `injection-5-micron` | `5.63 um` | `2170` | `8` | `0` | `2162` | only active bin with reported completed steam-line escape in this sampled pass |
| `injection-28-micron` | `28.14 um` | `2170` | `0` | `0` | `2170` | all sampled tracks reported incomplete |
| `injection-56-micron` | `56.27 um` | `2170` | `0` | `0` | `2170` | all sampled tracks reported incomplete |
| `injection-112-micron` | `112.54 um` | `2170` | `0` | `0` | `2170` | all sampled tracks reported incomplete |
| `injection-168-micron` | `168.81 um` | `2170` | `0` | `0` | `2170` | all sampled tracks reported incomplete |
| `injection-348-micron` | `348.88 um` | `2170` | `0` | `0` | `2170` | all sampled tracks reported incomplete |

Aggregate over the six one-injection sample passes:

| Quantity | Value |
|---|---:|
| Total tracked | `13020` |
| Total escaped | `8` |
| Total trapped | `0` |
| Total incomplete | `13012` |

Observed / inferred interpretation:

- `Observed`: the one-injection-at-a-time pass reproduces the same aggregate count split already seen in the refreshed live DPM summary: `8` escaped and `13012` incomplete.
- `Observed`: within this sampled pass, the only reported completed escape comes from `injection-5-micron`.
- `Observed`: no sampled injection reported any trapped-particle count.
- `Inferred`: for the currently active 6-bin subset, the unresolved issue is still tracking completion, not evidence of meaningful completed escape from the coarser bins.
- `User-specified`: because this pass still excludes `562.70 um`, `844.06 um`, and `1631.84 um`, it remains a **partial-bin diagnostic** only.
- `Inferred`: treat this table as a useful per-bin screening snapshot for setup `08b`, not as report-quality DPM separation proof.

## 12. Automation Note

The current executable rebuild path for this branch is implemented in:

- `PyAnsys/scripts/setup/setup08b_purnanto_split_inlet_rebuild.py`

Validation note:

- tested on the Student Edition Windows target over SSH;
- target mesh: `purnanto-extended.msh`;
- short run validated at `5` iterations;
- output case written successfully as `purnanto-extended-rebuilt-rerun5.cas.h5`;
- output data written successfully as `purnanto-extended-rebuilt-rerun5.dat.h5`;
- the direct DPM replay now restores pressure-force, virtual-mass, max-step, and step-length-factor values from the archive;
- Fluent 2026 R1 still refuses to serialize the archived operating-density method, operating temperature, and continuity threshold cleanly through the current API path;
- the residual patch state still reads back as `true`, so that remains a deliberate review item rather than silent parity.

### 12.1 Read-Only Case Inspection On Applied Split-Inlet Case

Read-only inspection performed against:

- `PyAnsys/data/Purnanto Application to Split inlet geom/purnanto_applied_split_inletgeom.set`
- `PyAnsys/data/Purnanto Application to Split inlet geom/setup-steps`
- remote case loaded through gRPC server `1`:
  - `C:\Users\syok443\Documents\TwoPhaseInletV2(Purnanto)\TwoPhaseInletV2(Purnanto).cas.h5`

Inspection outcome:

- `Observed`: the saved split-inlet case loads with:
  - `liquidinlet` as `mass-flow-inlet`
  - `steaminlet` as `mass-flow-inlet`
  - `steamoutlet` as `pressure-outlet`
- `Retained`: the split `mass-flow inlet` implementation is intentional for `08b`, not a setup mistake, because this branch is currently following the setup-`07` actual-area / target-flow logic rather than a split-velocity reinterpretation.
- `Retained`: the current `steaminlet` hydraulic diameter is also intentional for this rebuilt geometry and should be treated as the updated branch value rather than forced back toward the older `~0.724 m` legacy value.
- `Observed`: the journal file includes intermediate `velocity-inlet` screens and canceled edits, but those do not represent the final saved case state and must not be used alone as proof of a boundary-condition error.

Remaining caution from this inspection:

- `Uncertain`: the injection-side advanced DPM physical-model state, especially whether any secondary-breakup-related toggles remain materially active in the saved case, was not fully resolved in this inspection pass;
- leave that question open for a later dedicated DPM review rather than treating it as settled parity.
