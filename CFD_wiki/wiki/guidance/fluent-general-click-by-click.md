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

## 12) When Answering User Setup Questions
Use this response structure:
1. `Goal`
2. `Click path`
3. `What to check before clicking Next`
4. `Common failure mode`
5. `Fast recovery action`

If a click path is uncertain, mark it `Inferred` and point back to source page for verification.
