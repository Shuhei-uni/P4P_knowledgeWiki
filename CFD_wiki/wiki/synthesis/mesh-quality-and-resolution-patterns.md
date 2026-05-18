# Synthesis: Mesh Quality, Node Count, and Independence Patterns

## Scope
Reusable guidance for judging whether a CFD mesh is credible enough to continue solving, with emphasis on Fluent orthogonal quality, mesh/node counts, and what geothermal/two-phase papers actually report.

## Key Takeaway
`Inferred`: A minimum orthogonal quality of 6.73e-2 is not automatically fatal in Fluent, but it is a warning-level value for a high-swirl, two-phase separator case. The decision should be based on where the bad cells are located, whether Fluent reports severe mesh warnings, and whether a mesh-independence check stabilizes the outputs of interest.

## Paper Evidence

### Purnanto 2013 Geothermal Separator
- `Reported`: the separator paper used unstructured tetrahedral meshes for all separator geometries and states that, given vessel size, node counts in the order of millions were preferable for sufficient refinement ([purnanto-2013], p.6).
- `Reported`: the same paper used an average element size of 5 cm and local face sizes as small as 1 cm near high-gradient boundary regions ([purnanto-2013], p.6).
- `Reported`: incomplete DPM particle tracks remained a concern, and the authors state that further mesh refinement was likely needed ([purnanto-2013], p.8).
- `Missing`: no exact node count per geometry, skewness, orthogonal quality, aspect ratio, or mesh-independence table is reported.

### Mubarok 2020 Geothermal Flow Meters
- `Reported`: six mesh densities were tested using Richardson extrapolation for a geothermal two-phase flow-meter model ([mubarok-2020], p.7).
- `Reported`: mesh cell counts increased from 329,805 to 1,887,432 cells; Mesh 6 was selected because extrapolated errors for pressure drop, enthalpy, and mass flow were each below 1% ([mubarok-2020], Table 5).
- `Reported`: the meshing method used curvature refinement, transition ratio 0.272, growth rate 1.2, up to 5 near-wall layers, and minimum edge length 3.2 mm ([mubarok-2020], p.7).
- `Missing`: orthogonal quality and skewness thresholds are not reported.

### Mondal and Sharma 2024 Annular Flow
- `Reported`: a three-mesh independence study was performed for annular-flow entrainment fraction; Mesh 2 was accepted because Mesh 2 and Mesh 3 gave almost the same outlet entrainment fraction ([mondal-2024], p.2886-2887).
- `Reported`: node/element counts were Mesh 1: 95,559 nodes / 91,640 elements, Mesh 2: 148,526 nodes / 143,500 elements, Mesh 3: 224,231 nodes / 217,000 elements ([mondal-2024], Table 4).
- `Reported`: the accepted mesh was multi-block hexahedral and wall-refined ([mondal-2024], p.2883).
- `Missing`: orthogonal quality and skewness thresholds are not reported.

### Skoog 2020 Annular-Flow Thesis
- `Reported`: the cross-sectional mesh had about 1300 cells and was refined near the wall to capture local changes ([skoog-2020], p.14).
- `Reported`: prior work was cited as having confirmed grid independence for that mesh ([skoog-2020], p.14).
- `Missing`: full 3D total cell count and Fluent quality metrics are not centrally reported.

## Cross-Paper Pattern
- `supports`: papers commonly report mesh density, refinement locations, and independence/sensitivity evidence.
- `supports`: papers rarely report Fluent orthogonal quality or skewness values directly.
- `supports`: stronger papers justify the mesh by output stability, not by one raw mesh metric.
- `gap-for-project`: for geothermal separator reconstruction, the lack of reported quality metrics means the current project must create its own quality and independence record.

## Practical Interpretation for Orthogonal Quality 6.73e-2
- `Inferred`: orthogonal quality ranges from 0 to 1, where higher is better. A minimum value of 0.0673 is low enough to inspect, especially if those cells sit in the inlet, wall-film, vortex-core, outlet, or phase-interface regions.
- `Inferred`: if the low-quality cells are isolated in a dynamically unimportant region, the mesh may still be usable for a first debug run.
- `Inferred`: if low-quality cells are near the inlet transition, sharp bends, separator wall, steam outlet, or brine outlet, they can distort swirl, pressure recovery, phase separation, and convergence.
- `Inferred`: for the current geothermal separator problem, a 1.8M-node mesh is now consistent with the separator paper's reported "order of millions" scale. The remaining mesh risk is therefore not global node count but local element quality, refinement placement, and output sensitivity.

## Recommended Audit Workflow
1. Run Fluent mesh check and record minimum orthogonal quality, maximum skewness, negative volumes, and cell count.
2. Locate the worst 0.1-1% cells visually.
3. Classify whether bad cells are in critical flow regions: inlet bend, wall boundary layer, vortex core, steam outlet, brine outlet, or interface-sensitive zones.
4. If bad cells are critical, repair or locally refine before judging solver physics.
5. Run at least three meshes: current/coarse, medium, and refined.
6. Compare pressure drop, outlet steam quality/carryover proxy, mass imbalance, and vortex-core pressure/velocity trends.
7. Treat the mesh as acceptable only when key outputs change by a small chosen tolerance and convergence behavior does not degrade.

## Quick Decision Rule
- `Proceed for setup debugging`: minimum orthogonal quality is low but no negative volumes exist, bad cells are non-critical, and residual/monitor behavior is stable enough to diagnose settings.
- `Repair before production`: bad cells are in inlet/swirl/outlet regions, phase fields show local noise, DPM tracks go incomplete near bad cells, or pressure/velocity monitors change strongly with refinement.
- `Do not use for report-quality results`: no mesh-independence evidence exists, cell count is far below literature scale for comparable vessel geometry, or quality problems coincide with the variables used for conclusions.

## Links
- Source: [purnanto-2013-cfd-geothermal-separator](../sources/purnanto-2013-cfd-geothermal-separator.md)
- Source: [mubarok-2020-cfd-geothermal-flow-meters](../sources/mubarok-2020-cfd-geothermal-flow-meters.md)
- Source: [mondal-sharma-2024-air-water-annular-flow-cfd](../sources/mondal-sharma-2024-air-water-annular-flow-cfd.md)
- Source: [skoog-2020-annular-flow-three-field-cfd-thesis](../sources/skoog-2020-annular-flow-three-field-cfd-thesis.md)
- Setup: [geothermal-boc-separator-fluent-2013-baseline](../setups/geothermal-boc-separator-fluent-2013-baseline.md)
