# `.meshdat` Semi-Automated Mesh Improvement Workflow

This workflow is for the case where you already have:

- a Workbench Meshing `.meshdat` exported after manual Named Selections and initial mesh controls
- a baseline Fluent `.msh` or `.msh.h5` from that same setup
- a text file listing required boundary and cell zones

It is deliberately conservative.

It does **not**:

- modify geometry
- create, delete, rename, or infer Named Selections
- auto-optimise blindly

It does:

1. reopen the baseline Fluent mesh in PyFluent
2. audit boundary zones, cell zones, cell count, and quality metrics
3. reopen the `.meshdat` as a diagnostic input
4. write a five-trial conservative plan for Workbench/Meshing
5. validate any exported trial `.msh` or `.msh.h5`
6. save one JSON report and one Markdown comparison report

## Current split-inlet contract

The workflow keeps these zones in a diagnostic contract, but exact preservation is not a hard-fail condition at this stage:

### Boundary zones

- `liquid-inlet`
- `steam-inlet`
- `outlet`
- `bottom`
- `wall`
- `wall-smooth_spiral_separator`

### Cell zones

- `smooth_spiral_separator`

Boundary-type expectations:

- `liquid-inlet` -> `velocity-inlet`
- `steam-inlet` -> `velocity-inlet`
- `outlet` -> `pressure-outlet`
- `bottom` -> `wall`
- `wall` -> `wall`
- `wall-smooth_spiral_separator` -> `wall`

Warn if:

- either split inlet is missing
- the two split inlets are merged into one generic inlet zone
- either split inlet is renamed unexpectedly
- any required zone is exported under the wrong Fluent boundary type

Hard-fail only if:

- Fluent/PyFluent cannot reopen the exported mesh
- mesh quality metrics cannot be extracted
- generation or export fails
- the mesh is clearly corrupted or unusable

## Reliability boundary

The reliable automation boundary in this repo is:

- **automated**: reopen, audit, compare, and report with PyFluent
- **operator-driven**: open the `.meshdat` in Workbench/Meshing and apply mesh-control changes only

This keeps the workflow aligned with the user rule set while avoiding fragile GUI automation.

## Required-zones file format

Use a plain text file like:

```text
[boundary]
inlet
outlet
wall
wall-smooth_spiral_separator

[cell]
smooth_spiral_separator
```

The parser also accepts one-line forms such as `boundary: inlet` and `cell: fluid`.

## Conservative trials

The runner writes the same five trial intents every time:

1. `trial-01-coarser-global-size`
2. `trial-02-local-inlet-spiral-refine`
3. `trial-03-adjust-growth-rate`
4. `trial-04-smoother-transition`
5. `trial-05-mild-inflation-if-stable`

These are instructions for the Meshing operator, not hidden auto-tuning.

When doing inlet-region local sizing:

- apply it consistently to both `liquid-inlet` and `steam-inlet` unless deliberately testing something else later
- inspect whether the poorest cells cluster along the split edge between those two inlet faces
- inspect whether poor cells also cluster near the spiral wall, inlet-vessel blend, outlet, or bottom boundary

## Command

From the repository root:

```powershell
.\PyAnsys\.venv\Scripts\python.exe .\PyAnsys\scripts\run_mesh_improvement_workflow.py `
  --meshdat "C:\Users\Shuhei Yokkaichi\Documents\CFD\New folder\meshing trial\mesh-trial1.meshdat" `
  --baseline-mesh "C:\Users\Shuhei Yokkaichi\Documents\CFD\New folder\meshing trial\mesh-trial1.msh" `
  --required-zones ".\PyAnsys\input\required-zones.txt" `
  --output-dir ".\PyAnsys\output\meshdat-workflow" `
  --cell-target 1000000 `
  --processor-count 1
```

If you do not have the required-zones file yet, you can still generate a baseline-observed template:

```powershell
.\PyAnsys\.venv\Scripts\python.exe .\PyAnsys\scripts\run_mesh_improvement_workflow.py `
  --meshdat "C:\Users\Shuhei Yokkaichi\Documents\CFD\New folder\meshing trial\mesh-trial1.meshdat" `
  --baseline-mesh "C:\Users\Shuhei Yokkaichi\Documents\CFD\New folder\meshing trial\mesh-trial1.msh" `
  --output-dir ".\PyAnsys\output\meshdat-workflow" `
  --cell-target 1000000 `
  --processor-count 1 `
  --write-observed-zones-template
```

That template is based on the baseline mesh reopen only. Treat it as a starter, not as a substitute for the real required-zone contract.

## After Workbench exports trial meshes

Rerun the same command and append one `--trial-mesh` entry per exported mesh:

```powershell
.\PyAnsys\.venv\Scripts\python.exe .\PyAnsys\scripts\run_mesh_improvement_workflow.py `
  --meshdat "C:\Users\Shuhei Yokkaichi\Documents\CFD\New folder\meshing trial\mesh-trial1.meshdat" `
  --baseline-mesh "C:\Users\Shuhei Yokkaichi\Documents\CFD\New folder\meshing trial\mesh-trial1.msh" `
  --required-zones ".\PyAnsys\input\required-zones.txt" `
  --output-dir ".\PyAnsys\output\meshdat-workflow" `
  --cell-target 1000000 `
  --processor-count 1 `
  --trial-mesh "trial-01-coarser-global-size=C:\path\to\trial-01.msh.h5" `
  --trial-mesh "trial-02-local-inlet-spiral-refine=C:\path\to\trial-02.msh.h5"
```

## Success rule

A trial is marked successful only if:

- Fluent reopens the exported mesh
- quality gates remain acceptable

Cell count, face count, and node count are still recorded, but they are diagnostic by default and are not the primary pass/fail rule unless a Student-compatible target is explicitly requested.

The quality gate compares:

- minimum orthogonal quality
- maximum equivolume skewness
- bad-cell fraction below orthogonal-quality thresholds `0.15`, `0.10`, and `0.05`

The report also shows:

- which metrics improved against the baseline
- exact missing or renamed zones
- wrong boundary-type exports
- zone preservation warnings, not hard failures
- manual-review placeholders for the inlet split edge, spiral wall / vessel blend, outlet region, bottom region, and overall simulation suitability

## Outputs

The workflow writes:

- `workflow-report.json`
- `workflow-report.md`
- Fluent transcripts
- optional `required-zones-template.txt`

Use the Markdown report as the quick review artifact and the JSON report as the machine-readable record.
