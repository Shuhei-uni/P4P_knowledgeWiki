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

## 10) When Answering User Setup Questions
Use this response structure:
1. `Goal`
2. `Click path`
3. `What to check before clicking Next`
4. `Common failure mode`
5. `Fast recovery action`

If a click path is uncertain, mark it `Inferred` and point back to source page for verification.
