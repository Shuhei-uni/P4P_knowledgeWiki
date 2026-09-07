# Concept: Mesh Inflation and Boundary-Layer Layers

## Plain Meaning
`Inflation` means adding thin, stacked prism/wedge-like cells next to wall surfaces so the mesh resolves the near-wall boundary layer instead of jumping straight from the wall into large tetrahedral cells.

In simple terms: inflation creates several smooth layers hugging the wall.

## Why It Exists
- `Inferred`: wall-bounded turbulent flows have steep velocity gradients near walls.
- `Inferred`: in cyclone/separator CFD, wall-adjacent flow matters because liquid is pushed toward the wall by swirl and separation performance depends strongly on near-wall behavior.
- `Reported`: related geothermal flow-meter CFD used up to 5 near-wall layers in its mesh setup ([mubarok-2020], p.7).

## What Inflation Controls Usually Mean
- `First layer height`: thickness of the first cell touching the wall.
- `Number of layers`: how many stacked near-wall layers are created.
- `Growth rate`: how quickly each layer gets thicker away from the wall.
- `Total thickness`: total wall-normal thickness covered by all inflation layers.

## When Inflation Helps
- Boundary layers and wall shear need better resolution.
- Near-wall swirl, recirculation, or liquid accumulation is important.
- Turbulence model wall treatment requires controlled near-wall spacing.
- Wall-adjacent gradients are causing unstable or noisy results.

## When Inflation Can Hurt
- `Inferred`: if inflation is forced around sharp corners, tiny inlet/outlet gaps, or abrupt curvature, layers can collapse, fold, or become highly skewed.
- `Inferred`: bad inflation can reduce orthogonal quality even when the total node count is high.
- `Inferred`: in separator inlets/outlets, poor inflation near sharp transitions can be worse than no inflation because it creates sliver cells exactly where pressure and velocity gradients are strongest.

## Practical Separator Guidance
1. Use inflation mainly on physical walls, not necessarily on inlet/outlet boundary faces themselves.
2. Avoid aggressive first-layer height or too many layers around tight inlet/outlet transitions.
3. Keep growth rate gentle, commonly around 1.2 as a starting point when feasible.
4. Inspect inflation layers visually near the spiral inlet, outlet tube, and brine outlet.
5. If low orthogonal quality is caused by collapsed inflation layers, reduce layer count, reduce total thickness, relax first-layer height, or suppress inflation locally.

## Cyclone ICEM Exemplar Link
- A cyclone separator tutorial uses a hexahedral ICEM blocking strategy with wall-layer-style edge refinement: 22 wall-normal nodes, initial spacing 0.03, and growth ratio 1.1 or 1.2 (`Reported`; spacing units not specified) ([youtube-cyclone-icem-fluent], user-provided notes).
- Relation: `supports` the practical rule that cyclone/separator wall regions need deliberate near-wall resolution, while the missing spacing units keep exact reuse risk high.

## Quick Diagnostic
- If worst cells form a thin band along the wall: inflation settings may be the cause.
- If worst cells cluster at inlet/outlet face edges: face sizing, edge cleanup, local curvature sizing, or local inflation suppression may be more useful than global refinement.
- If worst cells sit at sharp transitions: fix geometry/sliver faces before adding more layers.

## Links
- Synthesis: [mesh-quality-and-resolution-patterns](../synthesis/mesh-quality-and-resolution-patterns.md)
- Setup: [geothermal-two-phase-flow-meter-fluent-sst-mixture-2020](../setups/geothermal-two-phase-flow-meter-fluent-sst-mixture-2020.md)
- Setup: [cyclone-separator-icem-hexa-rsm-dpm-exemplar](../setups/cyclone-separator-icem-hexa-rsm-dpm-exemplar.md)
