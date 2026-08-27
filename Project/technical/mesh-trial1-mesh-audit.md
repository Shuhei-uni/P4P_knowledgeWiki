> **Retired source:** ResearchProject_wiki/wiki/technical/mesh-trial1-semi-automated-workflow.md
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# `mesh-trial1` Semi-Automated Mesh Improvement Workflow

## Purpose

Record the project-facing workflow and first audit artifact for improving the current `mesh-trial1` meshing branch without changing geometry or Named Selections.

Primary reusable guidance is the maintained
[Workbench `.meshdat` workflow](../../CFD_wiki/wiki/guidance/workbench-meshdat-semi-automated-improvement.md).
No direct Workbench GUI runner is retained in `PyAnsys`; after an operator
exports a candidate mesh, use the read-only
[`inspect_case.py`](../../PyAnsys/scripts/inspection/inspect_case.py) workflow
to inspect the loaded Fluent case.

## Inputs used on 2026-06-10

- `.meshdat`: `C:\Users\Shuhei Yokkaichi\Documents\CFD\New folder\meshing trial\mesh-trial1.meshdat`
- baseline Fluent mesh: `C:\Users\Shuhei Yokkaichi\Documents\CFD\New folder\meshing trial\mesh-trial1.msh`
- required-zones file: historical machine artifact path `../../PyAnsys/input/required-zones-mesh-trial1.txt` (not migrated)
- cell target: diagnostic only for now; not used as the primary acceptance rule

## Active required-zone contract

Boundary zones expected exactly from the Fluent-exported mesh:

- `liquid-inlet`
- `steam-inlet`
- `outlet`
- `bottom`
- `wall`
- `wall-smooth_spiral_separator`

Cell zones expected:

- `smooth_spiral_separator`

## Observed baseline audit

- `Observed`: baseline Fluent mesh reopened successfully through PyFluent
- `Observed`: boundary zones detected:
  - `bottom`
  - `liquidinlet`
  - `outlet`
  - `steaminlet`
  - `wall`
- `Observed`: cell zone detected:
  - `smooth_spiral_separator`
- `Observed`: node count was `255,163`
- `Observed`: face count was `2,915,260`
- `Observed`: cell count was `1,444,529`
- `Observed`: minimum orthogonal quality was about `0.03168`
- `Observed`: maximum equivolume skewness was about `0.96832`
- `Observed`: bad-cell fraction at orthogonal-quality thresholds was approximately:
  - `<= 0.15`: `2.56e-05`
  - `<= 0.10`: `3.46e-06`
  - `<= 0.05`: `6.92e-07`
- `Observed`: the strict split-inlet required-zone contract currently fails on the exported baseline mesh because:
  - `liquid-inlet` was exported as `liquidinlet`
  - `steam-inlet` was exported as `steaminlet`
  - `wall-smooth_spiral_separator` did not appear as a separate exported boundary zone

## Observed `.meshdat` diagnostic

- `Observed`: the `.meshdat` reopened in the workflow
- `Observed`: the `.meshdat` reopen did not expose usable cell-zone metrics or zone inventory through the same meshing-mode path
- `Inferred`: keep the exported baseline `.msh` as the acceptance reference for zone preservation and quality comparisons

## Generated artifacts

- Workflow report: historical machine artifact path `../../PyAnsys/output/meshdat-semi-automated/workflow-report.md` (not migrated)
- Machine-readable report: historical machine artifact path `../../PyAnsys/output/meshdat-semi-automated/workflow-report.json` (not migrated)
- Required-zones contract: historical machine artifact path `../../PyAnsys/input/required-zones-mesh-trial1.txt` (not migrated)

## Next action

1. Fix the Meshing/export path so the Fluent-exported mesh preserves the exact split-inlet and wall-zone names required by the contract.
2. Run conservative Workbench trials in this order:
   - coarser global size
   - local inlet-split / spiral refinement
   - adjusted growth rate
   - smoother transition
   - mild inflation only if stable
3. Export each successful candidate as `.msh.h5`.
4. Rerun the workflow with `--trial-mesh` entries and keep only meshes that reopen, preserve the exact required zones, and keep quality acceptable.
