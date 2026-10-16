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
