# Mesh and liquid volume fraction comparison

The top-down figures show the inlet-centre horizontal slice. These exports use an orthographic camera, a 3.9 × 2.9 m field of view, and 2400 × 1800 pixels. The 08b geometry is translated relative to Phase 8; each slice is placed at its own inlet midpoint. The separator side views below show a vertical centre cut.

## Mesh views

| 08b: tetrahedral, 7,601,261 cells | Phase 8: 60,964 cells | Purnanto V2: 342,609 cells |
| --- | --- | --- |
| ![08b: tetrahedral, 7,601,261 cells](<poster mesh assets/08b-tetrahedral-mesh-inlet-section.png>) | ![Phase 8: 60,964 cells](<poster mesh assets/mesh60k-inlet-section.png>) | ![Purnanto V2: 342,609 cells](<poster mesh assets/mesh342k-inlet-section.png>) |

The 08b cut shows a much denser mesh. The two smaller meshes show larger interior cells and thin layers near the walls. These views compare mesh structure; they do not establish mesh independence.

## Liquid volume fraction

The contour field is phase-2 liquid volume fraction. F0, F1, F2, and F4 use the 60,964-cell mesh at the 26.81 m/s reference point. The 08b field uses its historical split-inlet setup and 7.6 million-cell mesh.

| Case | Mesh cells | Saved iteration | Inlet / model |
| --- | ---: | ---: | --- |
| 08b | 7,601,261 | 10,000 | Historical split two-phase inlet |
| F0 | 60,964 | 10,000 | Mixed feed on both inlet faces; SIMPLE |
| F1 | 60,964 | 10,000 | Mixed feed on both inlet faces; Coupled |
| F2 | 60,964 | 10,000 | Split inlet; Coupled |
| F4 | 60,964 | 16,000 | Split inlet; coupled DPM and wall film; 2.5% DPM allocation |

### Colour range 0–1

| 08b — N10,000 | F0 — N10,000 | F1 — N10,000 | F2 — N10,000 | F4 — N16,000 |
| --- | --- | --- | --- | --- |
| ![08b liquid volume fraction, 0-1, N10000](<poster mesh assets/08b-N10000-inlet-liquid-volume-fraction.png>) | ![F0 liquid volume fraction, 0-1, N10000](<poster mesh assets/F0-26.81-N10000-inlet-liquid-volume-fraction-range-0-1.png>) | ![F1 liquid volume fraction, 0-1, N10000](<poster mesh assets/F1-26.81-N10000-inlet-liquid-volume-fraction-range-0-1.png>) | ![F2 liquid volume fraction, 0-1, N10000](<poster mesh assets/F2-26.81-N10000-inlet-liquid-volume-fraction-range-0-1.png>) | ![F4 liquid volume fraction, 0-1, N16000](<poster mesh assets/F4-26.81-2.5pct-N16000-inlet-liquid-volume-fraction-range-0-1.png>) |

### Colour range 0–0.5

| 08b — N10,000 | F0 — N10,000 | F1 — N10,000 | F2 — N10,000 | F4 — N16,000 |
| --- | --- | --- | --- | --- |
| ![08b liquid volume fraction, 0-0.5, N10000](<poster mesh assets/08b-N10000-inlet-liquid-volume-fraction-range-0-0.5.png>) | ![F0 liquid volume fraction, 0-0.5, N10000](<poster mesh assets/F0-26.81-N10000-inlet-liquid-volume-fraction-range-0-0.5.png>) | ![F1 liquid volume fraction, 0-0.5, N10000](<poster mesh assets/F1-26.81-N10000-inlet-liquid-volume-fraction-range-0-0.5.png>) | ![F2 liquid volume fraction, 0-0.5, N10000](<poster mesh assets/F2-26.81-N10000-inlet-liquid-volume-fraction-range-0-0.5.png>) | ![F4 liquid volume fraction, 0-0.5, N16000](<poster mesh assets/F4-26.81-2.5pct-N16000-inlet-liquid-volume-fraction-range-0-0.5.png>) |

The 0–0.5 scale makes the lower liquid fractions easier to see. Values above 0.5 use the upper-end colour. In these cuts, F0 shows a broader liquid-rich region than the other cases. The 08b, F2, and F4 views show liquid enrichment near the outer wall.

The figures show the Eulerian liquid field. The F4 contour does not include DPM droplet mass or wall-film inventory. F4 has a later iteration horizon; inlet representation and numerical settings also differ across families. These images show spatial differences, not an isolated mesh effect or proof of equal convergence.

No solved volume-fraction field was supplied for the 342,609-cell mesh. It is included only in the mesh comparison.

## Separator side view — liquid volume fraction

The existing vertical centre-cut figures use the same 0–1 colour range and N10,000 horizon. F0 and F1 are the 26.81 m/s reference cases. Each image is 1800 × 2400 pixels. Display styles and legend sizes differ because these are existing native exports.

| 08b — split inlet, tetrahedral mesh                                                                              | F0 — mixed inlet, SIMPLE, 60k mesh                                                                                   | F1 — mixed inlet, Coupled, 60k mesh                                                                                  |
| ---------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| ![08b side-view liquid volume fraction, N10000](<poster mesh assets/08b-N10000-side-liquid-volume-fraction.png>) | ![F0 side-view liquid volume fraction, N10000](<poster mesh assets/F0-26.81-N10000-side-liquid-volume-fraction.png>) | ![F1 side-view liquid volume fraction, N10000](<poster mesh assets/F1-26.81-N10000-side-liquid-volume-fraction.png>) |

F0 shows broad liquid-rich regions along the outer walls. F1 has narrower wall enrichment and a liquid-rich lower region. The 08b centre cut is mostly at low liquid fraction, with thin wall enrichment. These are observations from one saved state; the inlet, mesh, and numerical-package differences prevent attributing the changes to mesh alone.

Sources: [08b field-export manifest](../../../PyAnsys/output/08b-mesh-20261005/field-export-manifest.json) and [Phase 8 native-view export receipt](../../../PyAnsys/output/phase8-storyline-20260930/export-receipt.json). The F0 side-view source retains its historical filename `F1-26.81-simple-n10000-liquid.png` in the [F0 results](../../experiments/phase-08-storyline-reconstruction/f0-simple/results.md); the Coupled view is recorded in the [F1 results](../../experiments/phase-08-storyline-reconstruction/f1-one-inlet/results.md).

## Sources

The mesh and top-down views are native Fluent exports from Server 3. Source pairs, camera settings, colour ranges, and figure hashes are recorded in these export manifests:

- [08b-mesh-20261005](<../../../PyAnsys/output/08b-mesh-20261005/export-manifest.json>)
- [mesh60k-inlet-20261005](<../../../PyAnsys/output/mesh60k-inlet-20261005/export-manifest.json>)
- [mesh342k-inlet-20261005](<../../../PyAnsys/output/mesh342k-inlet-20261005/export-manifest.json>)
- [08b-inlet-vof-20261005](<../../../PyAnsys/output/08b-inlet-vof-20261005/export-manifest.json>)
- [f0-inlet-vof-20261005](<../../../PyAnsys/output/f0-inlet-vof-20261005/export-manifest.json>)
- [f124-inlet-vof-20261005](<../../../PyAnsys/output/f124-inlet-vof-20261005/export-manifest.json>)
