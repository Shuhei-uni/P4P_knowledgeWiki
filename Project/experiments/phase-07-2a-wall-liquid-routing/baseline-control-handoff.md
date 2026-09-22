# Phase 7.2A baseline control handoff

## Scientific identity

- Phase designation: `P72A-R0-SMOOTH-CONTROL-COUPLED-GLOBAL-TIME`
- Source record: Phase 7.1A `R0-SMOOTH-CONTROL-LAST1000`
- Source run: `PyAnsys/output/phase71a_r0_control_run4`
- Phase 7.2A parent coordinate: final native report/transcript state `5586`
- Historical R0 comparison window: expected checkpoint coordinates `4580–5580`;
  restarted transcript rows `4586–5586`
- Solver formulation: steady pressure-based Coupled with Global Time Step
  pseudo-time
- Wall/EWF state: smooth wall, `k_s=0`, EWF off
- Physical model: v2 phase-2-only throughput-controlled virtual outlet;
  matching liquid momentum and shared `k`/`epsilon` removal; no direct phase-1
  mass source

## Verified final pair

Case:

```text
C:\Users\syok443\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase71A\FamilyR\finals\P71A-R0-SMOOTH-CONTROL-COUPLED-GLOBAL-TIME-PLUS1000\20260922T162500Z\P71A-R0-SMOOTH-CONTROL-COUPLED-GLOBAL-TIME-PLUS1000-full-loading-plus1000.cas.h5
```

Case SHA-256: `4fd493972839929f1f0922ad42679456d1f4aea294da86e4b13d6b7c32f754fc`

Data:

```text
C:\Users\syok443\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase71A\FamilyR\finals\P71A-R0-SMOOTH-CONTROL-COUPLED-GLOBAL-TIME-PLUS1000\20260922T162500Z\P71A-R0-SMOOTH-CONTROL-COUPLED-GLOBAL-TIME-PLUS1000-full-loading-plus1000.dat.h5
```

Data SHA-256: `b2261fac8626b2e338c3a9c80c334c8a910d1bfb536f782ef9234623f00e1a72`

The pair, loaded at its final native state `5586`, is the authoritative starting
parent for 7.2A. The expected `5580` checkpoint is retained as a historical
ledger coordinate; children must use the final `5586` state rather than rolling
back to that checkpoint. Children must not overwrite the parent. Each server
receives its own local copy, and each child records the path and hash of that
copy before applying a family delta.

## Parent readback required before mutation

The child preflight must verify, at minimum:

- case/data pair opens and the loaded mesh is the 60k v2 mesh with the virtual
  outlet zone;
- native iteration is recorded from transcript/report evidence, not a stale
  Fluent RP variable;
- Coupled / Global Time Step settings are present;
- full-loading inlet targets are present;
- the v2 absorber command, native applied phase-2 source, zero phase-1 source,
  and matching momentum/source terms are present;
- `steamoutlet` remains the pressure outlet and all bottom boundaries remain
  walls;
- EWF is off and intended roughness is zero for the R0 parent;
- required reports can be written and incrementally read; and
- a paired checkpoint can be saved and reopened before the family solve.

No child may hybrid-initialize, patch a liquid pool, replay the old inlet ramp,
change the absorber law, or change the solver scaffold as part of a wall-family
delta.
