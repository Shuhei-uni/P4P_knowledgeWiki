# Phase 10 — Proposed design evidence

| Design | Verified retained evidence | Interpretation limit |
| --- | --- | --- |
| Vertical blocker — matched basic EWF | N34661 / 50.000 ms; native save/reopen and OneDrive hashes in [follow-up results](vertical-slit154k/basic-ewf-10us/results.md) | Frozen bulk; earlier enhanced-film history and parent film age differ |
| Vertical blocker — extended basic EWF | N44661 / 150.000 ms; 10,000 additional fixed 10 µs updates; [completion](vertical-slit154k/basic-ewf-10us/results.md) | Frozen bulk; common-age 50 ms pair remains preserved for comparison |
| Vertical blocker — preserved enhanced EWF | N84000 / 50.9 ms; [earlier case results](vertical-slit154k/results.md) | Earlier reference; not the matched basic-EWF endpoint |
| Angled ramp | N33492 / 50.000 ms; paired save/reopen and OneDrive hashes verified in [case results](angled-slit213k/results.md) | Frozen-bulk basic EWF; steady film and design benefit not established |
| Angled ramp — extended basic EWF | N43492 / 150.000 ms; 10,000 additional fixed 10 µs updates; [completion](angled-slit213k/results.md) | Original angle settings and frozen bulk retained; 50 ms pair preserved |
| Design comparison | Both proposed geometries now share this phase owner | Mesh and initial field/history differences prevent attribution to geometry alone |

| Earlier vertical enhanced-EWF endpoint metric | Value | Definition / limit |
| --- | --- | --- |
| Bulk liquid inventory | 123.196 kg | Frozen bulk field |
| Bulk vapour inventory | 130.328 kg | Frozen bulk field |
| Wall-film inventory | 3.675 kg | Separate EWF inventory |
| Steam-outlet liquid flux | 12.648 kg/s | Phase-resolved outward flux without sources; 10.82% of liquid feed |
| Steam-outlet vapour flux | 80.387 kg/s | Phase-resolved outward flux without sources |
| Numerical absorber removal | 79.129 kg/s | Volumetric source; not physical bottom boundary drainage |
| Physical bottom boundary flux | 0 kg/s | Without sources |
| Inlet minus outlet static pressure | 21.679 kPa | Difference of area-mean static pressures |
| Angled endpoint bulk metrics | Not yet extracted | No quantitative improvement comparison selected |

*Source: [vertical native bulk metrics](../../../PyAnsys/output/phase10-proposed-design/20261012/slit154k-50p9ms-reference/bulk-flow-metrics.json). These quantities do not form a full mass ledger or establish separation efficiency.*

| Spatial evidence | Location | Limit |
| --- | --- | --- |
| Vertical inlet liquid fraction, turbulence, velocity and slit vectors | [Native PNG exports](vertical-slit154k/figures/slit154k-50p9ms/) | Final visual QA and derived graphics-case save/reopen were interrupted; all export candidates retained |
| Historical matched-ramp startup comparison | [Vertical startup results and figures](vertical-slit154k/startup-stage3/results.md) | Geometry and resolution changed together; early startup only |
| Angle spatial and bulk comparison | Matching fields still needed | Available endpoint proves completion, not improved liquid routing |

| Next analysis | Purpose |
| --- | --- |
| Compare common views and liquid destinations with settings differences visible | Establish observed changes before testing a feature-specific interpretation |
| Distinguish physical collection from numerical removal and liquid carryover | Avoid interpreting reduced storage as improved separation |

[Three-case inlet-region comparison: 58.050 ms baseline and near-50 ms designs, with matched top-down views and claim limits](inlet-comparison-50ms.md).

## Paused endpoint: bulk fields and flow

| Source / scope | Verified basis |
| --- | --- |
| Pair | Preserved human-pause N30862 pair; 23.705 ms film clock; SHA-256 and reopen verified |
| State | Bulk flow and turbulence held during frozen-film development; solve remains paused |
| Top-down view | X–Z cut at mean liquid-inlet height, Y = 2.066011 m; viewed along −Y |
| Inlet-facing view | Central Y–Z cut at X = 0 m; viewed along +X, normal to the inlet faces; this is an internal cut, not the inlet boundary |
| Scalars | Phase-2 liquid volume fraction, range 0–1; mixture turbulent kinetic energy, shared range 0–100 m²/s² |
| Vectors | Top-down cut; all vectors, projected in plane, fixed arrow length; colour indicates 3D mixture speed, 0–40 m/s |
| Machine evidence | [Native bulk reports and figure provenance](../../../PyAnsys/output/phase10-proposed-design/20261011/paused-bulk-export.json); [vector settings](../../../PyAnsys/output/phase10-proposed-design/20261011/paused-top-vectors.json) |

| Bulk quantity | Value | Reduction |
| --- | ---: | --- |
| Domain volume | 22.7619 m³ | Both fluid cell zones |
| Mixture inventory | 209.174 kg | Volume integral |
| Liquid inventory | 77.7250 kg | Phase-2 mass |
| Liquid volume | 0.0882025 m³ | Integrated liquid volume fraction |
| Mean liquid volume fraction | 0.3875% | Volume weighted |
| Mean / maximum speed | 26.7346 / 83.3367 m/s | Volume weighted / cell maximum |
| Mean / maximum turbulent kinetic energy | 9.19793 / 98.0509 m²/s² | Volume weighted / cell maximum |
| Mean turbulence dissipation | 263.065 m²/s³ | Volume weighted |
| Inlet-to-steam-outlet pressure drop | 22.0283 kPa | Difference of area-weighted static-pressure reports |

| Mass flow term | Magnitude | Accounting basis |
| --- | ---: | --- |
| Liquid feed | 116.920 kg/s | Boundary flux, excludes cell sources |
| Vapour feed | 80.6900 kg/s | Boundary flux |
| Liquid through steam outlet | 1.35071 kg/s | Boundary flux, excludes cell sources |
| Vapour through steam outlet | 80.5096 kg/s | Boundary flux |
| Collector liquid-removal source | 127.085 kg/s | Volumetric absorber source; separate from boundary outflow |
| Bulk balance residual | −11.3354 kg/s | Inflow minus steam-outlet boundary flow minus removal source |

The held bulk balance does not close. These spatial fields and fluxes describe the saved finite state; they do not establish a converged steady separator. Bulk liquid volume fraction is distinct from EWF film thickness. Colour ranges are fixed across the two scalar views.

| View | Liquid volume fraction | Turbulent kinetic energy | Velocity vectors |
| --- | --- | --- | --- |
| Top-down at inlet height | [Native contour](figures/paused-23p705ms/top-down-inlet-height-liquid-volume-fraction.png) | [Native contour](figures/paused-23p705ms/top-down-inlet-height-turbulent-kinetic-energy.png) | [Native vectors](figures/paused-23p705ms/top-down-inlet-height-velocity-vectors.png) |
| Inlet-facing central cut | [Native contour](figures/paused-23p705ms/inlet-facing-central-liquid-volume-fraction.png) | [Native contour](figures/paused-23p705ms/inlet-facing-central-turbulent-kinetic-energy.png) | — |
