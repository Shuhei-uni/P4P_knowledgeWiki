# F2 26.81 m/s base preparation

F2 was derived from the verified F1 26.81 m/s case/data pair by changing the four phase mass-flow inlet commands only. It was then freshly Hybrid initialized, saved, and reopened on `student`.

- Case: `C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase8\F2\F2-split-26p81-base.cas.h5` (SHA-256 `a38ab50038551124b5e22ec501f94dbc03ca306cde0c601225c7d6967b4d63d5`).
- Data: `C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase8\F2\F2-split-26p81-base.dat.h5` (SHA-256 `a3acc8e538f8b33937c65831d82f93d0f29074e039b99725308ea55d5d01e4e3`).
- Machine builder: [`build_phase8_f2_from_f1.py`](../../../../PyAnsys/scripts/setup/build_phase8_f2_from_f1.py). [Readback receipt](../../../../PyAnsys/output/phase8_f2_base_20260926.json).

Readback after reopening: `liquidinlet` supplies `116.93872650 kg/s` phase-2 liquid and zero vapor; `steaminlet` supplies `80.70292372 kg/s` phase-1 vapor and zero liquid. The shared materials, other boundaries, cell sources, DPM/EWF state, solver methods, and controls matched F1 in the builder's before/after comparison. Mesh check passed. This is an initialized setup base, not a developed carrier; common Phase 8 report definitions and post-development 09cV3 diagnostic injections remain to be installed before any F1/F2 comparison run.

F2 inherits F1's Mixture model and therefore has **no active bulk interfacial surface-tension coefficient or force**. `0.0411 N/m` is recorded as the Purnanto reference property, not as an active Fluent setting; see the F1 surface-tension audit.
