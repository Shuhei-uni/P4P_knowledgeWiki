# Setup 02c — Mixture Brine-Outlet Pressure Sensitivity, Unprimed

## Canonical metadata

| Field | Value |
|---|---|
| Programme | `full-geometry` |
| Physics family | `mixture` |
| Campaign | `steady-liquid-outlet` |
| Legacy setup ID | `02c` |
| Lifecycle | `active` |
| Investigation mode | diagnostic / pressure sensitivity |
| Controlled variable | brine-outlet gauge pressure only |
| Historical parent | [02 — split two-zone velocity-inlet brine outlet](../../../past/archived/02-split-two-zone-velocity-inlet-brine-outlet.md) |
| Detailed frozen source | [02c compatibility snapshot](../../../compatibility-snapshots/02c-mixture-brine-outlet-pressure-sensitivity-unprimed.md) |
| Numerical evidence | [02c full-geometry results](../../../reports/full-geometry/mixture/steady-liquid-outlet/02c/results.md) |

## Intent

Determine whether the physical tangential brine-outlet pipe can remove continuous liquid from the full separator domain while keeping vapour preferentially routed to the steam outlet.

`02c` is the intentionally **unprimed** pressure-outlet control. It does not patch a lower-vessel liquid pool. The scientific comparison varies brine-outlet gauge pressure while preserving the verified split velocity inlets, Mixture model, turbulence model, steam-outlet condition, gravity, geometry, and numerical context of the selected parent.

## Current pressure-screen scope

The retained case identities are:

| Case | Brine gauge pressure | Role |
|---|---:|---|
| `02c-A` | `1.115 MPa` | lower-pressure drainage / vapour-short-circuit reference |
| `02c-B` | `1.120 MPa` | matches steam-outlet pressure |
| `02c-C` | `1.125 MPa` | first positive-backpressure point |
| `02c-D` | `1.1225 MPa` | intermediate bracket |
| `02c-E` | `1.1275 MPa` | positive-backpressure screen |
| `02c-F` | `1.130 MPa` | positive-backpressure screen |
| `02c-G` | `1.135 MPa` | upper-bracket screen |
| `02c-H` | `1.140 MPa` | Student-surrogate inlet-reference test |

The detailed source snapshot remains the authority for the exact build/readback procedure, historical Student-smoke notes, monitor package, case artifacts, and execution caveats. This canonical record exists so `02c` now belongs physically and semantically to the full-geometry Mixture steady-liquid-outlet campaign rather than the global `active/` namespace.

## Evidence and interpretation

The recorded pressure sweep is diagnostic evidence, not a validated operating-pressure selection. Use the linked report for actual measured results. Keep interpretation user-led unless a later experiment defines an explicit decision rule.
