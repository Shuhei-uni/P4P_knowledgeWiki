# Mesh Trial Harness

This harness is the first local PyFluent path for repeatable mesh trials under a
hard cell-count cap.

It is designed for the common case where you hand over:

- a partially worked `.cas.h5`, or
- a partially worked `.msh` / `.meshdat`

with named zones such as walls, inlet, and outlet already present.

## What v1 does

The harness:

1. prefers `.cas.h5` and falls back to `.msh`
2. reopens the artifact
3. records exact zone inventory
4. records baseline mesh metrics
5. runs optional trials
6. compares every completed trial against the baseline

The current scorecard is:

- minimum orthogonal quality
- maximum equivolume skewness
- bad-cell fraction below the chosen orthogonal-quality threshold

First-trial success means:

- exact zone preservation when possible
- cell count at or below the cap
- improvement in any `2` of the `3` scorecard metrics

## Artifact lanes

### 1. Artifact reopen lane

Supported:

- `.cas`
- `.cas.h5`
- `.msh`
- `.msh.h5`
- `.mesh`
- `.mesh.h5`
- `.meshdat`

This lane uses:

- meshing mode for exact zone inventory
- meshing mode for cell count and quality diagnostics

This is intentional for Student-license cases because solver mode may refuse to
open meshes above the solver cell limit even when meshing mode can still inspect
them.

### 2. Geometry remesh lane

If a geometry file is supplied, the harness runs three watertight trials:

- coarse poly
- tighter poly
- poly-hexcore

Current v1 sizes:

- coarse poly: `surface-max-size = 120`
- tighter poly: `surface-max-size = 80`
- poly-hexcore: `surface-max-size = 80`, `hex-max-cell-length = 120`

### 3. Mesh-only salvage lane

If only an existing mesh or case is available, the harness can attempt a limited
salvage trial:

- read artifact in meshing mode
- `clear_mesh()`
- `auto_mesh()`

This uses Fluent defaults and should be treated as a structured test, not a
guaranteed best-practice remesh recipe.

## Output files

The harness writes:

- `summary.json`
- one JSON report per trial
- Fluent transcripts
- any written trial `.cas.h5` / `.msh` outputs

Each trial report includes:

- input artifact metadata
- zone inventory or preservation result
- cell count
- minimum orthogonal quality
- maximum equivolume skewness
- bad-cell count and fraction
- pass/fail against the cell cap
- delta versus baseline
- success assessment

## Current command

From the repository root:

```powershell
.\PyAnsys\.venv\Scripts\python.exe .\PyAnsys\scripts\run_mesh_trial_harness.py `
  --input-artifact "C:\Users\Shuhei Yokkaichi\Documents\CFD\New folder\meshing trial\mesh-trial1.msh" `
  --output-dir ".\PyAnsys\output\mesh-trial1" `
  --processor-count 1 `
  --cell-cap 1000000 `
  --bad-quality-threshold 0.15
```

If you also have geometry:

```powershell
.\PyAnsys\.venv\Scripts\python.exe .\PyAnsys\scripts\run_mesh_trial_harness.py `
  --input-artifact "C:\Users\Shuhei Yokkaichi\Documents\CFD\New folder\meshing trial\mesh-trial1.msh" `
  --geometry-file "C:\path\to\your\geometry.step" `
  --output-dir ".\PyAnsys\output\mesh-trial1-with-geometry" `
  --processor-count 1 `
  --cell-cap 1000000 `
  --bad-quality-threshold 0.15
```

## Notes from `mesh-trial1.msh`

On the supplied `mesh-trial1.msh`, the harness proved that:

- baseline reopen works in meshing mode
- exact named-zone preservation can be checked from the mesh statistics export
- mesh-only salvage can run
- mesh-only salvage reduced cell count slightly from `1,444,509` to
  `1,443,493`
- mesh-only salvage improved bad-cell fraction below the `0.15` threshold from
  about `7.62e-06` to `5.54e-06`
- writing a new `.cas.h5` or `.msh` is blocked by the Student license once the
  mesh remains above `1,048,576` cells
- the trial still did not pass the first scorecard because it stayed above the
  `1,000,000` target and improved only `1` of the `3` scorecard metrics

Use the JSON reports as the primary artifact when a trial is diagnostically
useful but Fluent refuses to save the post-trial mesh.

On the supplied `mesh-trial1.meshdat`, Fluent reopened the file but did not
expose cell-zone metrics or the `report.mesh_statistics` path in meshing mode on
this local Student setup. The harness now records that as a completed but
partial diagnostic instead of failing.

## Learnings

- For Student-license work, `.msh` is the best first-class artifact for reopen,
  diagnostics, and limited salvage.
- `.meshdat` should be treated as a weaker fallback artifact. It may reopen, but
  it may not expose enough meshing-side APIs for full metrics or zone checks.
- Meshing mode is more useful than solver mode for over-limit student cases
  because solver mode can refuse meshes that meshing mode can still inspect.
- Exact zone preservation can be checked reliably from the exported mesh
  statistics text, even when higher-level APIs are limited.
- Trial outputs should stay useful even when Fluent cannot save a result. The
  report JSON and transcript are often the real deliverable under a student cell
  cap.

## Challenges Faced

- Fluent launch was unstable after crashy runs. Stale `fluent`, `cx2610`, or
  `ansyscl` processes had to be cleared before a clean rerun.
- Parallel meshing launch was less stable on this local setup. `--processor-count 1`
  was the safer default than `2`.
- Mesh writes can fail late because the Student license checks the output size at
  write time, not just at reopen time.
- Some PyFluent meshing utilities can return `None` instead of a list for
  partial artifacts, so the harness had to degrade gracefully instead of
  assuming full API support.
- Paths with spaces required quoted TUI file paths for reliable reopen/write
  behavior.

## Prime note

`PyPrimeMesh` is intentionally not part of this first harness.

Keep Prime behind a capability gate until there is a real-file proof for:

- import
- diagnostics
- minimal improvement
- export
- Fluent reopen with preserved zones
