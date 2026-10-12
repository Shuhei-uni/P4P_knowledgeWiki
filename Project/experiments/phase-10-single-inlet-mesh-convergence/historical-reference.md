# Historical tet-lineage study reference

| Item | Verified record |
| --- | --- |
| Study ID | `split_inlet_mesh_convergence_20260801` |
| Logged experiment | [Phase 2 — 08b mesh-convergence checkpoint](../phase-02-parity-reset-and-pre-v2-qualification/purnanto-08b-parity-split-inlet/mesh-convergence-checkpoint-20260803.md) |
| Later disposition | Same record's 5 August closure addendum: all seven nominal N3000 endpoints; no accepted mesh independence |
| Tet evidence | [08b parent readback](../phase-02-parity-reset-and-pre-v2-qualification/purnanto-08b-parity-split-inlet/historical-run-notes.md): 7,601,261 tetrahedral cells; per-level mesh-type readback still requires the archived files |
| Original supplied reference | [Purnanto live audit](../phase-01-purnanto-baseline-and-inlet-exploration/purnanto-00a-live-setup-audit/technical-live-setup-reference.md): 572,556 nodes and 2,964,593 tetrahedral cells |
| Physics scope | Carrier comparison; DPM and EWF excluded from the formal historical refinement study |
| Inlet scope | Historical `liquidinlet` and `steaminlet`; new family has one `inlet` |
| Machine evidence | Historical `PyAnsys/output/split_inlet_mesh_convergence_20260801` not present in this checkout |
| Archive locator | [Prior exact-artifact proof](../phase-07b-full-geometry-liquid-removal/geometry-proof.md#exact-artifacts) identifies the historical 900k-labelled case on Extreme SSD |
| Timing evidence | No per-mesh elapsed-time or memory table found in the preserved checkpoint |
| Quality evidence | [Recovered archived study report](https://github.com/Shuhei-uni/P4P_knowledgeWiki/blob/archive/andy-local-20260908/Setup%20report/07a-split-inlet-carrier-mesh-convergence.md) gives minimum OQ and maximum aspect ratio for all seven; skewness and size change remain unrecovered |
| Current use | Historical diagnostic reference; no old solver session is resumed by this phase |

## Recorded mesh ladder

| Historical label | Actual cells | Verified nodes | Min OQ | Max aspect ratio | Pressure drop at nominal N3000, kPa | Runtime |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 300k | 1,688,678 | Not recovered | 0.200732 | 20.3226 | 31.0510 | Not recovered |
| 600k | 3,609,102 | Not recovered | 0.191653 | 18.4352 | 29.0005 | Not recovered |
| 900k | 5,335,623 | 923,066 | 0.202194 | 20.1267 | 27.6593 | Not recovered |
| 1600k | 9,720,194 | Not recovered | 0.200348 | 19.5466 | 25.2610 | Not recovered |
| 1900k | 10,756,635 | Not recovered | 0.200177 | 18.7413 | 24.0141 | Not recovered |
| 2000k | 11,959,759 | Not recovered | 0.198112 | 17.8078 | 24.1355 | Not recovered |
| 2300k | 13,370,267 | Not recovered | 0.200535 | 18.9096 | 23.7092 | Not recovered |

Source: preserved checkpoint and closure addendum; transcribed observations, not a new calculation. Historical labels are not cell counts.

Quality values are from the recovered archive report, git blob `a644e9a2e92aba0510f538fd6bb8f46f4ee9c20f`. The 900k node count is from the [saved HDF5 geometry proof](../../../PyAnsys/output/phase07b_preparation/geometry-proof-20260908.json). [Count/quality extraction](../../../PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/phase2-mesh-statistics.json).

| Count comparison | Observation | Limit |
| --- | --- | --- |
| Similar node count | Historical 900k: 923,066 nodes, 5,335,623 cells; current M01: 981,016 nodes, 357,145 cells | Current M01 has 6.3% more nodes and 14.94 times fewer cells; equal node counts do not establish equal accuracy |
| Similar cell count | Historical 900k: 5,335,623 cells; current M07: 5,479,605 cells | Current M07 has 2.7% more cells and 10.88 times more nodes; topology and refinement placement differ |
| Full cell ranges | Historical ladder: 1.689–13.370M; current ladder: 0.357–5.480M | Ordered ladder positions are not matched-resolution pairs |

## Limits on the comparison

| Observation | Effect |
| --- | --- |
| Final pressure/velocity windows still drifted | Historical endpoints cannot be used as a qualified steady reference |
| 900k continuation reached N6000 with rising inventory and pressure | Equal iteration count does not isolate spatial mesh error |
| Historical split inlet versus current single inlet | Verify spatial phase/flow loading and document the boundary representation before attributing differences to mesh type |
| Current mesh recipe is poly-hexcore | Label it precisely; it is not a uniform polyhedral-only mesh |
| Original archived mesh files and timing records unavailable here | Exact lineage, full mesh metrics and measured speedup remain open |
