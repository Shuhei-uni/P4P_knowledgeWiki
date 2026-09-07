# Workbench `.meshdat` Semi-Automated Mesh Improvement

## Purpose

Reusable workflow for improving a Workbench/Meshing branch conservatively when the available inputs are:

- a `.meshdat` exported after manual Named Selections and initial mesh controls
- a baseline Fluent `.msh` or `.msh.h5` from the same setup
- a text file listing required boundary and cell zones

This page is for the case where geometry must stay fixed and only mesh controls may change.

## Evidence labels

- `Reported`: supported by official PyFluent or Ansys documentation
- `Observed`: reproduced in the local `PyAnsys` workflow on `2026-06-10`
- `Inferred`: practical recommendation assembled from documentation plus local behavior

## Key guardrails

- `Reported`: PyFluent exposes Fluent Meshing workflows and Fluent Meshing file-import commands, including Workbench `.meshdat` / `.mechdat` support in the meshing import layer ([PyFluent meshing workflows](https://fluent.docs.pyansys.com/version/stable/user_guide/meshing/new_meshing_workflows.html), [PyFluent import TUI](https://fluent.docs.pyansys.com/version/dev/api/meshing/tui/file/import_/import__contents.html)).
- `Reported`: `.meshdat` is a Meshing file format suitable for import into Ansys Workbench ([ANSYS Meshing User's Guide PDF listing](https://ansyshelp.ansys.com/public/Views/Secured/corp/v251/en/pdf/ANSYS_Meshing_Users_Guide.pdf)).
- `Inferred`: the reliable automation boundary in this repo is to automate reopen/audit/reporting in PyFluent and keep Workbench control edits operator-driven.
- `Inferred`: do not create, delete, rename, or infer Named Selections. Preserve the existing zone contract and change only mesh controls.

## Current split-inlet contract

- `liquid-inlet` and `steam-inlet` are intentional separate boundary zones and must not be merged.
- Match required zone names exactly from the Fluent-exported mesh.
- Fail the mesh if either split inlet is missing, renamed, merged into one generic inlet zone, or exported as the wrong boundary type.
- Keep using the exported baseline `.msh` as the acceptance reference, while treating `.meshdat` as the editable Workbench-side source.

## Recommended sequence

### 1. Audit the baseline Fluent mesh first

1. Run the PyFluent workflow against the baseline `.msh` or `.msh.h5`.
2. Record:
   - exact boundary zones
   - exact cell zones
   - cell count
   - minimum orthogonal quality
   - maximum equivolume skewness
   - bad-cell fraction
3. Treat the baseline mesh as the zone-contract source of truth if the `.meshdat` reopen is less informative.

Why this matters:

- `Observed`: on the local `mesh-trial1` sample, the baseline `.msh` reopened cleanly and exposed all required zone and quality information.

### 2. Reopen the `.meshdat` as a diagnostic input

1. Reopen the `.meshdat` in the same PyFluent workflow.
2. Record what is visible.
3. If the `.meshdat` does not expose full cell-zone metrics or mesh-statistics paths, do not force the `.meshdat` to become the audit source of truth.
4. Keep using the baseline Fluent mesh as the acceptance reference for zones and metrics.

Why this matters:

- `Observed`: on the local `mesh-trial1.meshdat` sample, the file reopened but did not expose usable cell-zone metrics or the same mesh-statistics path in meshing mode.

### 3. Apply only conservative mesh-control trials in Workbench/Meshing

Use `3` to `5` controlled trials only.

Recommended order:

1. `trial-01-coarser-global-size`
   - increase global size about `10` to `15 %`
2. `trial-02-local-inlet-spiral-refine`
   - keep Trial 01 global coarsening
   - add only local refinement near both split inlets and the spiral
3. `trial-03-adjust-growth-rate`
   - make growth one conservative notch smoother
4. `trial-04-smoother-transition`
   - prefer smoother or slower transition where available
5. `trial-05-mild-inflation-if-stable`
   - only after earlier trials reopen/export cleanly

Do not:

- switch geometry
- add new scoping definitions just to support a trial
- change the mesh-method family unless the baseline branch already uses compatible alternatives

### 4. Export each candidate back to Fluent mesh format

1. Generate the mesh.
2. Export `.msh.h5` if possible.
3. Keep one exported file per trial with stable names.

### 5. Validate each exported mesh in PyFluent

For each exported mesh:

1. Reopen it in Fluent through PyFluent.
2. Check exact zone preservation against the baseline mesh.
3. Check all required boundary and cell zones from the required-zones text file.
4. Record node count, face count, and cell count for diagnostics.
5. Check quality gates:
   - minimum orthogonal quality
   - maximum equivolume skewness
   - bad-cell fraction below orthogonal-quality thresholds `0.15`, `0.10`, and `0.05`
6. Save one comparison report.

Keep node count, face count, and cell count in the report, but treat them as diagnostic unless the task explicitly asks for a Student-compatible mesh.

## Success rule

A trial is successful only if:

- Fluent reopens the exported mesh
- required zones are still present
- exact baseline zone preservation still passes
- quality metrics improve or remain acceptable

## Repo implementation

- Runner: `../../../PyAnsys/scripts/run_mesh_improvement_workflow.py`
- Local operator guide: `../../../PyAnsys/docs/findings/MESHDAT_SEMI_AUTOMATED_WORKFLOW.md`
- Existing lower-level reopen helpers: `../../../PyAnsys/scripts/mesh_trial_harness_lib.py`

## Example local evidence

- `Observed`: generated workflow report for `mesh-trial1` at `../../../PyAnsys/output/meshdat-semi-automated/workflow-report.md`
- `Observed`: corrected baseline `mesh-trial1.msh` reopened with split inlet zones, but the current Fluent-exported names were `liquidinlet` and `steaminlet`, and the exported wall list did not include `wall-smooth_spiral_separator`.
- `Observed`: the strict required-zone contract therefore currently fails on the exported baseline mesh and must be fixed at the Meshing source/export level before trial meshes can be accepted.

## Uncertainty

- `Inferred`: this workflow is intentionally semi-automated because the repo has reliable PyFluent reopen/audit evidence but not yet a proven direct Workbench GUI automation path for changing mesh controls without operator review.
