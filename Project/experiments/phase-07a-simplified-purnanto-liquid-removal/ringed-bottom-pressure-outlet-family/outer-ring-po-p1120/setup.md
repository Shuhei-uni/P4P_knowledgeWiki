# E6 outer-ring pressure outlet — P1120

## Setup identity

| Item | Setup identity |
| --- | --- |
| Setup ID | `P7-E6-RING-OUTER-PO-P1120` |
| Candidate | `E6-RING-PO` |
| Role | discovery child, outermost radial band pressure outlet |
| Status | `DESIGN_READY_NOT_PLACED` |
| Controlled pressure | `1.120 MPa` gauge on `p7-bottom-ring-r05-outer` |
| Discovery horizon | 500 steady iterations after the mandatory 50-iteration smoke |
| Parent | exact verified E0 initialized parent, not a modified E1 result |

## Boundary topology

| Item | Boundary topology |
| --- | --- |
| reusable mesh catalogue must pass before this setup | is placed: |

```text
p7-bottom-ring-r01-inner  wall
p7-bottom-ring-r02        wall
p7-bottom-ring-r03        wall
p7-bottom-ring-r04        wall
p7-bottom-ring-r05-outer  pressure-outlet @ 1.120 MPa gauge
```

| Boundary topology |
| --- |
| The post-split face count, area, centroid range, plane, and adjacency of each zone must be read back from Fluent |
| The source-mesh survey expects 67 faces and `0.276031 m²` for the outer row, but the post-split result is authoritative |

## Boundary-condition sequence

| Item | Boundary-condition sequence |
| --- | --- |
| — | Prove exact parent and ringed-mesh identity |
| Read back all five ring types; confirm R01–R04 | are walls |
| — | Set pressure-outlet backflow phase state first, using the case’s existing mixture-boundary convention; do not interpret backflow fractions as a liquid-only outward condition |
|  | Set the R05 gauge pressure to `1,120,000 Pa` last |
|  | Read back type, pressure, secondary-phase backflow state, and ring area |

<details>
<summary>Supporting detail — Boundary-condition sequence</summary>

| Item | Boundary-condition sequence |
| --- | --- |
| — | Save, reopen, and repeat the same readback |
|  | Run the 50-iteration smoke gate |
|  | Stop and preserve evidence on divergence, floating-point exception, severe reverse flow, or nonfinite phase fields |
|  | If smoke passes, run the declared 500-iteration discovery horizon with the required histories and paired checkpoint |

</details>

## Evidence contract

| Evidence contract |
| --- |
| Record per-ring and steam-outlet total/liquid/vapor mass flux, net direction, reverse-flow fraction, pressure/velocity near each ring junction, lower and total liquid inventories, phase-resolved mass balance including storage, residuals, continuity/imbalance, warnings, and turbulent-viscosity limiting |
| The result must distinguish liquid removal from vapor loss and from mere reduction in stored inventory |

## Claim limit

| Item | Claim limit |
| --- | --- |
| Even a finite, stable child | is a localized pressure-routing diagnostic |
| It | is not a proof that the outer ring is liquid-selective or that `1.120 MPa` is the physical pressure at the separator bottom |
