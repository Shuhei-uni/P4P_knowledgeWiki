# Fluent General Click-by-Click Guidance (2025 R2)

## Scope
This page is a reusable GUI navigation map for common Fluent setup tasks.

Source anchor:
- `CFD_wiki/raw/Ansys_Fluent_Users_Guide.pdf`
- `wiki/sources/ansys-fluent-users-guide-2025r2.md`

Evidence label policy for this page:
- `Reported`: explicitly listed in User's Guide sections/menu terminology.
- `Inferred`: practical click path assembled from Fluent UI flow when the exact dialog path is distributed across sections.

## 1) Start Fluent
1. Open `Ansys Fluent Launcher`.
2. Set:
   - `Dimension` (`2D` or `3D`)
   - `Precision` (`Double` recommended for most research CFD)
   - `Parallel` core count
3. Click `Start`.

Evidence:
- `Reported`: launcher/options/startup topics listed in User's Guide startup chapter.

## 2) Read Mesh or Case
1. In Fluent, go to `File > Read > Mesh...` to import mesh-only files.
2. Or go to `File > Read > Case...` for an existing setup case.
3. Confirm zone names and units immediately after load.

Evidence:
- `Reported`: read/write mesh and case operations are documented in file I/O sections.

## 3) Run Basic Mesh Checks
1. Open `Mesh` panel (or task equivalent in current UI mode).
2. Run `Check`.
3. Review negative volumes, skewness, and orthogonal quality flags.
4. If severe errors appear, stop and repair mesh before physics setup.

Evidence:
- `Inferred`: quality-check action sequence is standard Fluent workflow linked to mesh-check sections.

## 4) Enable Physics Models
1. Go to `Models`.
2. Enable required models (for example turbulence and multiphase).
3. Confirm model compatibility before proceeding (especially multiphase + turbulence combinations).

Evidence:
- `Inferred`: model activation flow follows standard Fluent setup order.

## 5) Define Materials and Cell Zones
1. Go to `Materials` and create/edit required fluids.
2. Go to `Cell Zone Conditions`.
3. Assign the correct material/model to each fluid zone.

Evidence:
- `Inferred`: standard Fluent setup sequence.

## 6) Set Boundary Conditions
1. Open `Boundary Conditions`.
2. For each boundary zone:
   - set boundary type/inputs,
   - verify direction/sign conventions,
   - confirm phase-related inputs for multiphase cases.
3. Re-open key boundaries once to verify no unintended default reset happened.

Evidence:
- `Inferred`: standard solver-side configuration path.

### 6.1) Velocity Inlet Turbulence: Intensity and Hydraulic Diameter
Goal: provide Fluent enough inlet turbulence information to convert the entered mean velocity, turbulence intensity, and size scale into turbulence-model variables such as `k` and dissipation rate.

Click path:
1. Go to `Boundary Conditions`.
2. Select the velocity-inlet boundary zone.
3. Open `Momentum` or the turbulence section shown inside the velocity-inlet dialog.
4. Set `Turbulence Specification Method` to `Intensity and Hydraulic Diameter`.
5. Enter `Turbulent Intensity (%)`.
6. Enter `Hydraulic Diameter (m)`.
7. Click `Apply`, then reopen the boundary once to confirm the values stayed assigned.

What hydraulic diameter means:
- For a circular pipe, hydraulic diameter equals the pipe diameter.
- For a non-circular duct, use `Dh = 4A/P`, where `A` is inlet cross-sectional area and `P` is wetted perimeter.
- For a rectangle with width `a` and height `b`, this simplifies to `Dh = 2ab/(a+b)`.
- For a square with side `s`, this simplifies to `Dh = s`.

What Fluent is doing with it:
- `Turbulent Intensity` controls the inlet turbulence kinetic energy scale.
- `Hydraulic Diameter` gives Fluent a turbulence length scale for the inlet.
- Changing hydraulic diameter does not change the mass flow area or velocity by itself; it changes the turbulence quantities imposed at the inlet.

Common failure mode:
- Using the old circular-pipe diameter after changing the inlet into a rectangular or square duct can preserve the same velocity but impose the wrong inlet turbulence length scale.

Fast recovery action:
- Recalculate `Dh` from the active inlet face geometry. If a boundary has been split only as an artificial phase-allocation device but the upstream physical duct is still one shared duct, keep the physical duct hydraulic diameter unless there is a deliberate reason to impose different turbulence scales on the split zones.

Evidence:
- `Reported`: Fluent supports velocity-inlet turbulence specification through intensity and hydraulic diameter terminology in boundary-condition setup.
- `Inferred`: the non-circular duct calculation and artificial-split-zone caution are practical setup guidance based on the standard hydraulic-diameter definition and Fluent boundary-condition usage.

## 7) Solver Controls and Initialization
1. Open `Solution Methods` and select coupling/discretization schemes.
2. Open `Solution Controls` and set relaxation factors if needed.
3. Open `Initialization`.
4. Use `Hybrid Initialization` unless a stronger case-specific method is required.
5. Initialize.

Evidence:
- `Reported`: initialization workflow is explicitly covered in Fluent documentation.
- `Inferred`: exact ordering with methods/controls is practical best-order usage.

## 8) Monitors and Run
1. Open `Monitors` and define residual plus physical monitors.
2. Open `Run Calculation`.
3. Set iteration count (or timestep controls for transient runs).
4. Click `Calculate`.
5. Watch residual trend and key physical monitors together.

Evidence:
- `Inferred`: standard run-control path and monitoring order.

## 9) Save and Export
1. Save working state via `File > Write > Case...` and `File > Write > Data...`.
2. Use clear run IDs in filenames.
3. Export plots/reports as needed for validation records.

Evidence:
- `Reported`: read/write case-data actions are documented in file operation sections.

## 10) Open Existing Case/Data for Post-Processing
Goal: load a solved Fluent run so fields are available for flux reports, XY plots, vectors, contours, and pathlines.

1. Start Fluent with the same dimensionality and precision used for the run. If unsure, use `3D` and `Double Precision`.
2. Go to `File > Read > Case...` and select the relevant `.cas.h5` case file.
3. Go to `File > Read > Data...` and select the matching `.dat.h5` data file.
4. Wait for Fluent to finish reading the data; large `.dat.h5` files can take several minutes.
5. Check that contours are available by opening `Results > Graphics > Contours`.
6. Check fluxes through `Reports > Fluxes...`; choose `Mass Flow Rate`, select inlet/outlet boundary zones, then click `Compute`.
7. For vectors, use `Results > Graphics > Vectors`.
8. For plots along a surface/line, first create or select the surface, then use `Results > Plots > XY Plot`.
9. If Fluent says no data is available, the case was loaded without the matching data file or the data file does not match that case.

What to check before trusting results:
- The `.dat.h5` should normally be paired with the same setup/mesh `.cas.h5` that produced it.
- If there are multiple `.cas.h5` files, prefer the one that was saved with or immediately before the `.dat.h5` run.
- Opening a setup-only `.cas.h5` lets you inspect boundary conditions and mesh, but not solved contours/fluxes.

Evidence:
- `Reported`: Fluent supports separate read operations for case and data files in the file I/O workflow.
- `Inferred`: the post-processing check sequence is assembled from standard Fluent Results and Reports panel usage.

## 11) Baseline DPM Particle-Tracking Setup
Goal: run a quick droplet-size carryover check after the continuous separator flow field is acceptably stable.

Use this for a time-limited baseline:
1. Save the converged or best-available continuous-flow `case/data`.
2. Go to `Models > Discrete Phase` and enable DPM.
3. For the first baseline, use one-way tracking unless droplet mass loading is intentionally being coupled back into the continuous phase.
4. Create one `Surface` injection from the separator inlet or from the steam-core/droplet-release surface being tested.
5. Use `water-liquid` or the relevant droplet material.
6. Set a single diameter per quick run. A minimal geothermal separator sweep is:
   - `5e-6 m` for fine mist;
   - `1e-5 m` for the Purnanto-style `10 um` baseline;
   - `4.1e-5 m` for the larger Harwell-inferred marker.
7. Set injection velocity to follow the carrier flow if the goal is passive droplet carryover. If Fluent requires explicit components, use the inlet normal/tangential direction from the solved inlet setup rather than inventing a new direction.
8. Set steam outlet DPM behavior to `escape`.
9. Set any physical brine collection outlet, sump, or intended collection surface to `trap`.
10. Set ordinary separator walls intentionally:
   - `reflect` if the droplet should bounce/continue and wall deposition is not being counted;
   - `trap` if any wall impact is being treated as permanent collection;
   - wall-film interaction only when running an explicit wall-film test.
11. Track particles and record `escaped`, `trapped`, and `incomplete` counts for each diameter.
12. Compute efficiency as `1 - escaped/injected`, and bracket uncertainty if incomplete tracks are significant.

Boundary behavior:
- `escape`: the particle leaves the domain and is counted as escaped at that boundary.
- `trap`: the particle is removed from tracking and counted as collected at that boundary.
- `reflect`: the particle bounces from the boundary and remains active; it is not counted as collected.
- `incomplete`: the trajectory did not finish within tracking controls, so it should not be silently counted as separated.

Physical models to keep simple for the first sweep:
- Drag law: use Fluent's default spherical-particle drag law unless the case has a documented reason to change it.
- Particle rotation, rotational drag, and Magnus lift: leave off for baseline liquid droplets unless the report specifically studies non-spherical/rotating particles or strong rotation-induced lift. These options add interpretation burden and can change trajectory behavior without improving the separator-efficiency evidence.
- Stochastic tracking: optional sensitivity for turbulent dispersion; first get a deterministic/standard baseline, then repeat with stochastic tracking if small droplets are sensitive.
- Unsteady particle tracking: use it only for transient carrier flow or if particle residence/fate depends on time-varying fields. For a steady carrier solution, steady DPM tracking is the cheap baseline.
- Update DPM sources / interaction with continuous phase: use one-way coupling first when droplets are only diagnostic tracers. Enable source updates only when represented droplet mass loading is high enough that momentum or mass exchange should affect the gas/mixture solution.

Common failure mode:
- Treating every wall as `trap` can overstate separator efficiency, while leaving a true collection region as `reflect` can understate it. Wall behavior should match the physics claim you want to make.

Fast recovery action:
- If you are short on time, run only `5 um`, `10 um`, and `41 um`; record escaped/trapped/incomplete counts, and postpone wall-film modelling until the basic DPM fate counts are stable.

Evidence:
- `Reported`: Fluent DPM boundary-condition terminology includes escape, trap, reflect, and particle fate reporting in DPM post-processing.
- `Inferred`: the three-diameter time-limited baseline and model-simplification choices are practical guidance derived from the maintained Purnanto-style separator-efficiency workflow and annular-flow DPM/EWF evidence.

## 11A) Eulerian Wall Film: first separator baseline

Goal: enable EWF for the first wall-film deposition/drainage case without also enabling every available film interaction.

Version note:
- `Reported`: current Fluent documentation exposes the controls below, but exact panel names can vary by Fluent release and active multiphase model. The project currently uses Fluent 2024 R2, so read back every changed value after enabling the parent model.

### Model Options and Setup

| Setting | First `10a` recommendation | Reason |
|---|---|---|
| Eulerian Wall Film | `On` | activates the film equations |
| Solve Momentum | `On` | allows film velocity, drainage, and shear-driven motion to be solved |
| Momentum method | `Momentum Equation` | needed for explicit gravity/shear/pressure-gradient choices; use Analytical Solution only as a fallback diagnostic |
| Gravity Force | `On` | separator film drainage is gravity-sensitive |
| Surface Shear Force | `On` | gas flow can drive the wall film |
| Pressure Gradient | `On` if available | swirling separator pressure gradients may move the film; record this as part of the baseline |
| Spreading Term | `Off` initially | postpone film-thickness smoothing/spreading as a separate sensitivity |
| Surface Tension | `Off` initially | postpone contact-angle and capillary effects until film formation is stable |
| Solve Energy | `Off` | matches the current Energy-off carrier model; no evaporation/condensation claim |
| Solve Scalar | `Off` | no dissolved-species or mineral transport in `10a` |
| Film Material | `water-liquid` | match the current DPM liquid surrogate |
| DPM Coupling | `On` | droplets must be able to transfer mass to the film |
| Phase Coupling / VOF Coupling | `Off` | do not introduce VOF or phase-change coupling in `10a` |
| Treat Sharp Edge | `Off` initially | reserve edge separation for the re-entrainment branch |

Fluent documents `Solve Momentum`, the momentum terms, DPM coupling, phase coupling, and sharp-edge controls in the EWF model-options dialog ([official model-options reference](https://ansyshelp.ansys.com/public/Views/Secured/corp/v251/en/flu_ug/flu_ug_models_task_page.html)).

### Wall boundary settings

For each selected physical film wall:

1. Open `Boundary Conditions` and select the wall.
2. Open the `Wall Film` tab.
3. Select the Eulerian film-wall condition.
4. Use `Initial Condition`, with zero initial film height and zero initial film velocity unless a measured/pre-existing film is intentionally being tested.
5. Keep external user source terms off for `10a`; DPM deposition is the liquid source.
6. Set the DPM wall interaction to the standard wall-film/impingement path, not `trap` or ordinary `reflect`.
7. Leave `Flow Momentum Coupling` **off** for the first `10a` stability baseline. This lets the carrier flow drive the film while the film does not yet feed momentum back into the bulk flow. Turn it on only in `11a` when film-to-carrier feedback is the intended change.
8. Confirm that film-wall edges are connected to other film walls or to an intentional film outlet/drain. Fluent treats unconnected film-wall edges as film-flow outlets, which can otherwise look like unexplained mass loss ([official wall-boundary reference](https://ansyshelp.ansys.com/public/views/secured/corp/v251/en/flu_ug/flu_ug_ewf_sec_bound.html)).

Do not enable for the first `10a` run:

- Film Phase Change;
- partial wetting/contact angle;
- Particle Splashing;
- Edge Separation;
- Particle Stripping;
- VOF interaction;
- custom source terms.

Those are appropriate later sensitivities, especially `11a`, but would make the first film result difficult to attribute.

#### Splash-state readback note

When reviewing an existing EWF case, read back both the global `Particle Splashing` setting and the wall-level `DPM Wall Splash` setting. If either is enabled, classify the case as splash-sensitive rather than as a clean deposition/drainage baseline. Record the splashed-parcel count and impingement model with the case snapshot.

### Solution Method and Control

For the first transient film run:

- Time discretization: `First Order Implicit` initially;
- Film continuity and momentum: `First Order Upwind` initially;
- move to second-order schemes only after film mass and residuals are bounded;
- use conservative/adaptive film sub-time stepping if available;
- monitor film Courant number and keep it controlled rather than choosing a large arbitrary film timestep;
- do not set a small arbitrary `Maximum Thickness`. Fluent removes film material when that limit is exceeded, so a low value creates an artificial sink ([official solution-controls reference](https://ansyshelp.ansys.com/public/Views/Secured/corp/v251/en/flu_ug/flu_ug_ewf_sec_eqns.html));
- initialize the flow, then initialize the wall-film variables through the EWF model before iterating.

If two-way DPM/continuous-phase interaction remains enabled, Fluent may hide the `Film Steps per DPM Step` control; the documentation states that this control is only available when DPM interaction with the continuous phase is disabled. Do not treat its absence as a setup error.

### Minimum EWF monitors

Create or inspect:

- `Film Thickness`;
- `Film Mass`;
- `Film Velocity Magnitude`;
- `Film Courant Number`;
- `Film DPM Mass Source`;
- `Film Outflow Mass`;
- `Film Stripped Mass` and `Film Separated Mass`—these should remain zero or inactive in `10a` if stripping/separation is disabled;
- steam-outlet liquid phase flux and DPM escaped mass.

These variables are listed in Fluent's Eulerian Wall Film field-variable category ([official field-variable reference](https://ansyshelp.ansys.com/public/views/secured/corp/v251/en/flu_ug/flu_ug_fvtables.html)).

### Common failure modes

- Film mass disappears because an unconnected film-wall edge is acting as a film outlet.
- Film mass is artificially removed because `Maximum Thickness` is too small.
- Film never forms because DPM coupling or the wall-film boundary condition was not applied to the intended wall.
- Film becomes unstable because surface tension, splashing, stripping, and feedback were enabled together.
- The film result cannot be interpreted because the film-to-flow `Flow Momentum Coupling` setting changed unintentionally.

## 11B) DPM wall-return sensitivity: `10b`

Goal: test whether the assumed DPM wall fate changes carryover, without activating EWF or claiming that a physical film has been resolved.

### Parent and controls to keep fixed

Start from the same `09c` case used for the two-way DPM reference. Keep unchanged:

- `Interaction with Continuous Phase = On`;
- `Update DPM Sources Every Flow Iteration = On`;
- `DPM Iteration Interval = 1`;
- injection surfaces, diameters, represented mass flow, particle count, spherical drag, rotation, and stochastic-dispersion settings;
- `steamoutlet = escape` and physical collection region = `trap`.

### Nested child sequence

#### Producing `10b-1` and `10b-2` from `09c`

Use a fresh copy of `09c` for each child. Do not edit the original `09c` case after saving the copy.

##### Common preparation for both children

1. Load the original `09c` case/data.
2. Save a fresh working copy under the child label you are preparing (`10b-1` or `10b-2`).
3. Confirm `Models > Eulerian Wall Film` is `Off`.
4. Confirm `Models > Discrete Phase` is `On`.
5. Record the original `09c` value of `Interaction with Continuous Phase`.
6. Keep that same value for the `10b` comparison. If the original `On` state reproduces the previous failure, stop, make a fresh fallback copy with that setting `Off`, and use the same `Off` state for both `10b-1` and `10b-2`.
7. Do not change injection definitions, particle material, drag, tracking limits, particle count, stochastic settings, inlet/outlet conditions, or geometry.
8. Open `Boundary Conditions` and identify the physical liquid-impact wall zones. Do not change inlets, `steamoutlet`, or the collection boundary.
9. On each selected wall, open the `DPM` tab and record the existing boundary type and restitution coefficients before changing anything.

##### Build `10b-1`: built-in wall-return variation

1. Start from the fresh `09c` copy prepared above and save it as `10b-1`.
2. On selected liquid-impact wall zones only, open `Boundary Conditions > wall > DPM`.
3. Set `Discrete Phase BC Type` to `wall-jet` if that option is available.
4. If `wall-jet` is not available, stop before inventing a value and record the available options. The fallback is a separate `reflect` restitution sensitivity, not an unchanged copy of `09c`.
5. Leave `steamoutlet = escape`, the physical collection boundary = `trap`, and all other walls unchanged.
6. Confirm `wall-film`, `trap`, and `reinject` are not selected on the impact walls.
7. Save the case/data as `10b-1` and record the changed wall zones and final wall BC readback.
8. Run the same initialization and tracking procedure used for `09c`, with no other model changes.

`wall-jet` is a built-in wall-fate surrogate for screening; it does not resolve a physical liquid film. Fluent defines it separately from `reflect`, `trap`, `escape`, `wall-film`, and `user-defined` boundary conditions ([official DPM boundary reference](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_discrete_bc.html)).

##### Build `10b-2`: user-defined wall-return variation

Only proceed after `10b-1` has been saved and its wall-return sensitivity is meaningful.

1. Reload the original `09c` case/data and save a fresh copy as `10b-2`; do not build it by carrying over unrelated changes from `10b-1`.
2. Confirm EWF remains `Off` and the global DPM coupling state matches `10b-1`.
3. Compile or interpret one `DEFINE_DPM_BC` UDF.
4. On the same selected liquid-impact wall zones, set `Discrete Phase BC Type` to `user-defined`.
5. Hook only the intended `DEFINE_DPM_BC` function.
6. Use one bounded return rule based on documented impact quantities, such as impact angle or normal impact speed.
7. Define a safe fallback fate outside the valid range.
8. Leave all other wall, inlet, and outlet DPM conditions unchanged.
9. Do not enable EWF, Particle Splashing, Edge Separation, Particle Stripping, custom drag, material changes, or extra source terms.
10. Save the UDF source, compiled/loaded state, selected wall zones, and final boundary-condition readback with the `10b-2` case.

Do not use `reinject` for this internal-wall test. Fluent's `reinject` condition is intended for reintroducing particles at a domain boundary and is not equivalent to an internal wall-return law ([official DPM boundary reference](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_discrete_bc.html)).

##### Verification before either run

- EWF is `Off`.
- No wall has `Eulerian Film Wall` settings active.
- Only the intended impact-wall DPM condition changed.
- `steamoutlet` remains `escape`.
- The collection boundary remains `trap`.
- The global DPM coupling state matches the comparison parent.
- The injection list and represented mass loading still match `09c`.
- The case is saved under a new child name before initialization.

### Settings to leave off in all `10b` children

- Eulerian Wall Film;
- EWF DPM Coupling;
- Particle Splashing;
- Edge Separation;
- Particle Stripping;
- Phase/VOF Coupling;
- custom DPM drag or body force;
- stochastic dispersion, particle rotation, or material changes unless they are the separate planned test.

### Required `10b` reports

- wall impacts by wall zone;
- returned/wall-jet/user-defined particle count and represented mass;
- escaped, trapped, and incomplete counts by injection;
- steam-outlet escaped DPM mass;
- phase-flux liquid carryover;
- full mass balance and comparison against `10b-0`.

For unsteady tracking, Fluent can report injected mass, mass in domain, escaped mass, and related DPM quantities; use these reports when available rather than relying only on trajectory counts ([DPM report definitions](https://ansyshelp.ansys.com/public/views/secured/corp/v251/en/flu_ug/flu_ug_reporting_sec_monitoring_solution.html)).

## 12) When Answering User Setup Questions
Use this response structure:
1. `Goal`
2. `Click path`
3. `What to check before clicking Next`
4. `Common failure mode`
5. `Fast recovery action`

If a click path is uncertain, mark it `Inferred` and point back to source page for verification.
