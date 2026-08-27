> **Retired source:** Setups/archived/12-carrier-mesh-convergence-plan.md
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# Setup 12 — Carrier-Field Mesh-Convergence Plan

## Setup metadata

| Field | Value |
|---|---|
| Setup ID | `12` |
| Lifecycle | `future` |
| Role | controlled carrier-field mesh-sensitivity family |
| Parent setup | [08b — Purnanto parity split-inlet rebuild](../purnanto-08b-parity-split-inlet/setup.md), unless the operator explicitly selects a different frozen carrier baseline |
| Controlled change | mesh resolution only |
| Evidence-use label | numerical-verification plan; no mesh-independence result yet |
| Outcome | needs execution |
| Linked report | none until mesh statistics and solved outputs are captured |

## Objective

Determine whether the carrier-flow quantities used to compare the separator are insensitive enough to mesh resolution for the selected operating point. This is a carrier-field study: do not enable, disable, or retune EWF, DPM coupling, injections, or inlet loading while the mesh is being varied.

The current exact reference is the `08b` live checkpoint with `1,309,312` nodes and `7,601,261` tetrahedral cells (`Observed`; see [08b results](../purnanto-08b-parity-split-inlet/results.md)). It is retained as an additional fine-reference comparison, not assumed to be converged.

## Planned mesh ladder

| Level | Target nodes | Role | Approx. linear refinement ratio to next coarser level | Status |
|---|---:|---|---:|---|
| M0 | `~400,000` | coarse | — | planned |
| M1 | `~900,000` | medium | `1.31` from M0 | planned |
| M2 | `1,309,312` | current reference | `1.13` from M1 | existing checkpoint; solve/comparison state must be confirmed |
| M3 | `~1,600,000` | fine candidate | `1.07` from M2 | planned |

`Inferred`: ratios are estimated as `(N_fine / N_coarse)^(1/3)` for similar 3D tetrahedral meshes. M0 to M1 has an approximately `1.31` ratio, while the final intervals are tighter. This plan is therefore a stronger practical sensitivity comparison than the earlier proposed ladder, but a formal Richardson/GCI uncertainty still requires the actual mesh sizes, topology, and output sequence to justify it; add a more evenly spaced mesh if required.

## Frozen controls

Before creating M0, save a read-back-verified parent case/data copy. Across M0–M3, keep identical:

- geometry, named zones, and boundary-zone types;
- operating pressure, gravity, material properties, phase model, turbulence model, and energy-model state;
- inlet/outlet values, phase split, initialization method, and reference values;
- solver coupling, discretization, relaxation settings, transient/steady controls, and monitor definitions;
- wall conditions and all non-mesh setup settings;
- local refinement locations and the relative sizing/inflation strategy. Change the common sizing scale only; do not trade global coarsening for a different inlet, vortex-core, outlet, or wall treatment.

Do the carrier study with the same DPM/EWF state as the frozen parent, but do not use DPM fate or wall-film metrics as mesh-selection outputs until the carrier mesh is selected. If the selected parent has active EWF or DPM interaction, create a carrier-only parity copy first; otherwise the mesh study changes coupled physics as well as resolution.

## Per-mesh build and acceptance checks

1. Export a uniquely named Fluent mesh and case/data pair, for example `12-m0-400k`, `12-m1-900k`, `12-m2-1309k-reference`, and `12-m3-1600k`.
2. Reopen each exported mesh in Fluent and verify the exact parent zone contract before solving.
3. Record nodes, faces, cells, cell types, minimum orthogonal quality, maximum skewness, and fractions below the selected quality thresholds. Also locate the worst cells and classify whether they are at the inlet/spiral, vortex core, steam outlet, liquid outlet/bottom, or a non-critical region.
4. Hybrid-initialize each case from the same state. Do not initialize one mesh from a more mature solution of another mesh for the primary comparison.
5. Run each case until the same residual and physical-monitor acceptance window is met. A fixed iteration count alone is not convergence evidence.
6. Save the final case/data and export the same monitor histories and report values for every level.

Reject a mesh from comparison if it changes zones, has negative volumes, cannot meet the same numerical-state gate, or introduces poor-quality cells in a critical flow region. Record the rejection rather than silently replacing it.

## Required comparison outputs

Freeze the exact Fluent report definitions before M0 is run. Capture at least:

1. separator pressure drop, with the same inlet/outlet pressure reduction and phase scope;
2. steam-outlet liquid mass flow (carryover), plus steam-outlet vapour mass flow;
3. inlet and outlet phase-flow reports needed to interpret the carryover result;
4. outlet dryness/quality only when its numerator and denominator are captured from the same report scope;
5. one vortex-sensitive local quantity, such as a fixed-point/core pressure or tangential-velocity monitor;
6. residual histories and the final-window variation of each physical monitor;
7. solve cost: iterations to the acceptance window and wall-clock time.

Do not use a whole-domain phase imbalance as the primary acceptance metric when it lies outside the Purnanto scope boundary. Retain it as contextual diagnostic evidence. Do not average results across meshes or compare contour appearance alone.

## Decision rule

Compare adjacent levels and M2 against M3 using the same final-state reports. Record absolute and relative differences for every output.

- A proposed starting screen is `<= 2%` change in pressure drop and in robust outlet-flow quantities between M2 and M3, with stable local-monitor behaviour and no critical quality regression.
- For very small carryover values, relative percent change can be misleading. Judge it using the absolute carryover difference normalized by inlet liquid mass flow; the acceptable band must be declared before results are interpreted.
- If M2 and M3 agree within the declared bands, select M2 only as the economical mesh for this frozen carrier configuration. If they do not, retain M3 or add a finer mesh.
- If values are non-monotonic, a mesh has different local refinement behaviour, or the M1–M3 ratios are too tight for an asymptotic trend, report the outcome as **mesh-sensitive / inconclusive**, not mesh-independent.

The selected mesh is valid only for this geometry, operating point, phase-model state, and numerics stack. Run DPM or EWF sensitivities only after documenting this carrier-field selection, then check that their added physics does not reintroduce mesh sensitivity.

## Evidence and cross-references

- Project V&V index: [verification and validation limits](../../vnv.md)
- Reusable method: [separator CFD verification and validation workflow](../../../CFD_wiki/wiki/synthesis/separator-cfd-verification-and-validation-workflow.md)
- Mesh-quality interpretation: [mesh quality and resolution patterns](../../../CFD_wiki/wiki/synthesis/mesh-quality-and-resolution-patterns.md)
- Reopen/quality procedure: [Workbench meshdat semi-automated improvement](../../../CFD_wiki/wiki/guidance/workbench-meshdat-semi-automated-improvement.md)
