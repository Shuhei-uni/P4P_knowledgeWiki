# Semi-Automated Mesh Improvement Workflow

## Inputs
- `.meshdat`: `C:\Users\Shuhei Yokkaichi\Documents\CFD\New folder\meshing trial\mesh-trial1.meshdat`
- Baseline mesh: `C:\Users\Shuhei Yokkaichi\Documents\CFD\New folder\meshing trial\mesh-trial1.msh`
- Required zones file: `C:\Users\Shuhei Yokkaichi\Documents\CFD\P4P_knowledgeWiki\PyAnsys\input\required-zones-mesh-trial1.txt`
- Cell target: `diagnostic only / not enforced`

## Required zone contract
- Boundary: `bottom` | expected Fluent type `wall`
- Boundary: `liquid-inlet` | expected Fluent type `velocity-inlet`
- Boundary: `outlet` | expected Fluent type `pressure-outlet`
- Boundary: `steam-inlet` | expected Fluent type `velocity-inlet`
- Boundary: `wall` | expected Fluent type `wall`
- Boundary: `wall-smooth_spiral_separator` | expected Fluent type `wall`
- Cell zone: `smooth_spiral_separator`

## Baseline audit
- Baseline boundary zones: `bottom, liquidinlet, outlet, steaminlet, wall`
- Baseline cell zones: `smooth_spiral_separator`
- Baseline nodes: `255163`
- Baseline faces: `2915260`
- Baseline cells: `1444529`
- Baseline min orthogonal quality: `0.03167744882757173`
- Baseline max equivolume skewness: `0.968323`
- Baseline bad-cell fraction <= 0.15: `2.5613885217949934e-05`
- Baseline bad-cell fraction <= 0.10: `3.4613358402635045e-06`
- Baseline bad-cell fraction <= 0.05: `6.92267168052701e-07`
- Baseline required-zone contract satisfied: `False`
- Baseline missing required boundaries: `['liquid-inlet', 'steam-inlet', 'wall-smooth_spiral_separator']`
- Baseline wrong boundary types: `{}`
- Baseline missing required cell zones: `[]`

## `.meshdat` diagnostic reopen
- `.meshdat` boundary zones: `not available from meshing reopen`
- `.meshdat` cell zones: `not available from meshing reopen`
- `.meshdat` nodes: `None`
- `.meshdat` faces: `None`
- `.meshdat` cells: `None`

## Conservative trial plan
### trial-01-coarser-global-size
- Intent: Reduce unnecessary density without making cell count the primary target.
- Increase the global element size or relevance center by about 10 to 15 percent.
- Do not touch named selections, body suppression, or topology cleanup settings.
- Keep all method assignments identical to the baseline mesh branch.

### trial-02-local-inlet-spiral-refine
- Intent: Recover quality near the inlet and spiral while still allowing a coarser global field.
- Start from Trial 01 settings.
- Apply inlet-region local sizing consistently to both `liquid-inlet` and `steam-inlet` unless deliberately testing something else later.
- Add only local face or body sizing near the inlet split edge and spiral region at about 10 to 15 percent finer than the surrounding field.
- Do not create new scoping selections; reuse only existing selectable entities.

### trial-03-adjust-growth-rate
- Intent: Reduce abrupt size jumps without materially changing the geometry definition.
- Start from Trial 02 settings.
- Make the growth rate slightly smoother, for example one conservative notch lower than the baseline.
- Leave proximity and curvature capture logic unchanged unless they were already active in the baseline branch.

### trial-04-smoother-transition
- Intent: Improve transition quality around refined zones while staying conservative on total-cell growth.
- Start from Trial 03 settings.
- Prefer slower or smoother transition behavior if that control is available in the active meshing method.
- Do not switch mesh method families unless the baseline branch already uses multiple compatible methods.

### trial-05-mild-inflation-if-stable
- Intent: Try a mild wall treatment only after earlier trials reopen cleanly.
- Apply only if Trials 01 to 04 generate and export successfully.
- Use a mild inflation setup such as a small number of layers and gentle growth.
- Abort this trial if inflation introduces collapses, negative volume warnings, or worse reopen behavior.

## Trial validation results

- No exported trial meshes were supplied yet. Use the planned trials above, export each `.msh.h5`, then rerun this command with `--trial-mesh` entries.
## Comparison table

| Mesh | Reopen | Zones ok | Min orth | Max equiv skew | Bad<=0.15 | Bad<=0.10 | Bad<=0.05 | Nodes | Faces | Cells | Overall local review |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | yes | false | 0.03167744882757173 | 0.968323 | 2.5613885217949934e-05 | 3.4613358402635045e-06 | 6.92267168052701e-07 | 255163 | 2915260 | 1444529 | baseline reference |
