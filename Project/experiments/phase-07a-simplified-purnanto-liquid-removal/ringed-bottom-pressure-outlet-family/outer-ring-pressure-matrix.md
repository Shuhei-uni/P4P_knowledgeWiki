# E6 initial outer-band pressure matrix

## Fixed spatial pattern

```text
R01-inner wall | R02 wall | R03 wall | R04 wall | R05-outer pressure-outlet
```

`R05-outer` is the outermost existing bottom face row identified by the
read-only mesh survey (`r ≥ 0.99 m`, 67 faces, `0.276031 m²` in the source
mesh). The actual post-split face count and area are authoritative.

## Initial settings

| Setup ID | Gauge pressure | Horizon | Purpose |
| --- | ---: | ---: | --- |
| `P7-E6-RING-OUTER-PO-P1120` | `1.120 MPa` | 500 iterations | lowest reused E1 point; first smoke/response anchor |
| `P7-E6-RING-OUTER-PO-P1160` | `1.160 MPa` | 500 iterations | centre reused E1 point; pressure-response comparison |
| `P7-E6-RING-OUTER-PO-P1200` | `1.200 MPa` | 500 iterations | highest reused E1 point; failure-boundary probe |

The points are deliberately reused from E1 to separate pressure response from
the new spatial topology. They do not inherit E1’s interpretation: E1 P1120
was vapor-dominated, while corrected P1160/P1200 failed their smoke horizons.
Each E6 child must set backflow state first, set pressure last, and prove the
pressure before save and after reopen.

## Common gates

- The mesh catalogue capability setup must pass first.
- Each child must start from the same verified E0 initialized state and the
  same ringed mesh.
- A 50-iteration smoke horizon is mandatory before the 500-iteration screen.
- Failed children are failure-boundary evidence only and cannot be ranked as
  completed endpoints.
- Any continuation, additional pressure, alternate ring mask, or remesh needs
  a separate recorded design decision.
