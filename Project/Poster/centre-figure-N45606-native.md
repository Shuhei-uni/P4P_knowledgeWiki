# N45606 — native Fluent poster centre figure

| Selection | Value |
| --- | --- |
| Current figure | Native Fluent composite below; supersedes the rejected offline-rendered version |
| Renderer | Fluent 2025 R2 native mesh, contour, pathline and scene graphics on Server 6 |
| Source | Archived, hash-verified N45606 case/data pair; [case history](../experiments/phase-07-2a-wall-liquid-routing/stage-02-combined-ewf-roughness/case-history-N45606.md) |
| Poster canvas | 2400 × 4000 pixels; orthographic view; no labels, axes, legends, shadows, reflections or floor grid |
| Field preservation | No solver iterations, initialization or physical model changes; native iteration, film clock and selected inventory/thickness reports agree before and after export |
| Session preservation | Previous 997k Server 6 N10642 pair saved, hash-verified and reopened before replacement; [receipt](../../PyAnsys/output/poster-N45606-native/20261010/previous-endpoint.json) |

![Native Fluent centre figure: steam pathlines, wet wall, inlet and absorber footprint](../../PyAnsys/output/poster-N45606-native/20261010/selected/native-composite.png)

| Visible component | Native definition / display choice |
| --- | --- |
| Steam flow pattern | Native pathlines from `steaminlet`, steam domain `phase-1`; colour by `phase-1-velocity-magnitude`, fixed 0–65 m/s range |
| Developed wall film | Rear-half native wall surface with saved film thickness above 10 nm; uniform pastel cyan, 40% transparency |
| Body | Front-half native wall surface, light grey, 95% transparency; separate front/rear surfaces avoid coincident-surface artefacts |
| Absorber in centre figure | Orange native `bottom` boundary footprint; separate full-boundary export retained |
| Split inlet | Actual `steaminlet` and `liquidinlet` faces; native close-up resolves the 6.75 mm liquid strip |
| Film-thickness alternative | Native contour on the wet rear wall, fixed 0–0.31 mm range; separate figure and combined-view alternative |
| Claim limit | This is the saved model-development field. Film storage remains; the figure does not establish a steady film or validated separator performance. The absorber is a numerical removal region, not a resolved physical drain |

| Asset | Use |
| --- | --- |
| [Complete figure pack](../../PyAnsys/output/poster-N45606-native/20261010/N45606-native-poster-figure-pack.zip) | Combined PNGs, five transparent layers, alternatives, inlet close-up and provenance |
| [Native composite](../../PyAnsys/output/poster-N45606-native/20261010/selected/native-composite.png) | White-background figure with Fluent's scene depth handling |
| [Transparent composite](../../PyAnsys/output/poster-N45606-native/20261010/selected/native-composite-transparent.png) | Same figure for a coloured poster background |
| [Five layers](../../PyAnsys/output/poster-N45606-native/20261010/selected/) | `layer-geometry`, `layer-film`, `layer-flow`, `layer-absorber`, `layer-inlets`; place at the same position and size, then adjust opacity |
| [Thickness-coloured composite](../../PyAnsys/output/poster-N45606-native/20261010/selected/native-quantitative-composite.png) | Spatial film-thickness variation |
| [Inlet close-up](../../PyAnsys/output/poster-N45606-native/20261010/selected/native-inlet-detail.png) | Actual steam/liquid boundary split, viewed normal to the inlet plane |
| [Full absorber boundary](../../PyAnsys/output/poster-N45606-native/20261010/selected/native-absorber-full.png) | Actual cell-zone exterior, including the interface |
| [Graphics settings](../../PyAnsys/output/poster-N45606-native/20261010/configured.json) | Native field selections, surfaces, palette, transparency and display state |
| [Saved-view check status](../../PyAnsys/output/poster-N45606-native/20261010/saved-graphics.json) | Native images complete; later saved-view check blocked. Saved graphics pair identity and final live scene state remain unverified |
| [Native export receipt](../../PyAnsys/output/poster-N45606-native/20261010/latest-export.json) | Native local/remote hardcopy identities, camera and state checks |
| [Transparency checks](../../PyAnsys/output/poster-N45606-native/20261010/selected/layer-provenance.json) | White/black native background separation and recomposition checks |

All geometry, field contours and pathlines were rendered by Fluent. Transparent PNGs use matching native white/black exports to remove the background. This step changes the background alpha only; it does not render or reconstruct CFD fields. Separate layers have no mutual depth occlusion, so use the native combined figure when depth is important.

| Reproduction | Implementation |
| --- | --- |
| Native graphics creation/export | [Server 6 exporter](../../PyAnsys/scripts/inspection/export_phase72a_poster_native.py); `configure`, `preview`, `export`, `save` stages |
| Transparent packaging | [Background separation script](../../PyAnsys/scripts/analysis/package_native_poster_layers.py) |
| Superseded offline attempt | Original outputs retained in `PyAnsys/output/poster-N45606/20261010`; not the selected figure |
