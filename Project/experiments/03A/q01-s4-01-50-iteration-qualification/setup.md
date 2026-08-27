# 03A-Q01 — S4-01 50-iteration qualification

## Setup metadata

| Field | Value |
|---|---|
| Experiment ID | `03A-Q01` |
| Parent branch | `03A` Stage-4 `S4-01` |
| Role | bounded continuation qualification |
| Investigation mode | diagnostic/model-development; not convergence or validation |
| Selected by | human selection in the current research loop |
| Controlled scientific delta | none |
| Requested run budget | exactly `50` Fluent steady iterations |
| Interpretation owner | user-led; pending review of the evidence packet |

## 1. Question and selection rationale

Does the exact named S4-01 endpoint remain numerically and physically
interpretable over a short, controlled continuation when every scientific
setting is held fixed?

This is the human-selected `03A-Q01` proposal, with its original continuation
cap reduced to exactly `50` iterations. The short cap is intentional: it is a
bounded qualification/readback run, not a replacement for the Stage-4
long-continuation evidence or a claim of stationarity.

## 2. Exact parent and start-state contract

Load this case/data pair explicitly on Fluent Server 2 before preparation:

```text
Case: C:\Users\syok443\Documents\FluentRuns\03A-stage4\S4-01\run-20260822T123011Z\03A-stage4-S4-01-plus030000-end-20260822T123011Z.cas.h5
Data: C:\Users\syok443\Documents\FluentRuns\03A-stage4\S4-01\run-20260822T123011Z\03A-stage4-S4-01-plus030000-end-20260822T123011Z.dat.h5
```

The pre-run remote SHA-256 readback is:

| Member | SHA-256 |
|---|---|
| parent case | `dfbc0109e910f11f71d9c15956f49a3ab81a015e2d5d7a43f7d366e75aec1126` |
| parent data | `f52a7f91cbadaa276eab851bde16a0f1c2a92dfa39c7c005517d28f2f8706249` |

The parent report-history preflight recovered the named S4-01 relative-mass-
imbalance history with `30,001` points, from cumulative iteration `3,000` to
`33,000`. That native history, rather than Fluent's stale RP
`current-iteration` value after a case/data load, is the parent coordinate
authority.

The parent must read back as:

- Fluent `2025 R2`, 3-D double precision, with the Stage-4 18-rank route;
- steady pressure-based Mixture;
- RNG `k-epsilon`, SIMPLE, momentum under-relaxation `0.3`;
- active Mixture and drift equations;
- the inherited 03A boundary/model/material/mesh state unchanged;
- no DPM injections and the existing `1.120 MPa` steam and brine pressure
  outlet settings.

The parent and its written Stage-4 rationale remain linked in the [Stage-4
setup contract](../stage-04/setup.md) and [Stage-4 results](../stage-04/results.md).

## 3. Controlled delta and invariants

There is no scientific setup delta. Do not change the mesh, phases, materials,
boundaries, turbulence model, pressure outlets, solver methods, under-
relaxation, initialization, DPM/EWF state, or physical model controls.

The implementation may change only evidence destinations needed for this
selected run: a new case-only prepared artifact, a new native monitor
directory, a 50-iteration native autosave root, a transcript/residual export,
and a new paired endpoint. These are execution/evidence controls, not a
scientific comparison variable.

Do not reinitialize. The native journal must read the prepared case, read the
exact S4-01 parent data, and issue one Fluent-owned `/solve/iterate 50`
command. Python must not loop over iterations, write periodic checkpoints, or
replay the journal after an uncertain client return.

## 4. Evidence required before interpretation

Capture the following, preserving native iteration coordinates, units, signs,
scope, and completeness:

- exact parent and new endpoint case/data paths and SHA-256 values;
- parent/prepared/endpoint scientific readbacks and the no-delta audit;
- native transcript and post-run residual export;
- all configured Stage-4 physical report histories: total/liquid/vapour
  fluxes, liquid inventories, mass imbalance, routing, and brine hydraulics;
- native autosave case/data pair(s), if written during the 50-iteration run;
- actual observed native residual coordinates and the final paired endpoint
  reload/readback.

An endpoint file or a single residual snapshot is not sufficient to claim
stationarity, convergence, separator performance, or parent eligibility.

## 5. Source and handoff

- Scientific parent authority: [03A Stage-4 setup authority](../stage-04/setup.md)
- Selected experiment contract: [Project experiment contract](../../README.md)
- Implementation: [Q01 native runner](../../../../PyAnsys/scripts/setup/run_03a_q01_s4_01_50.py)
- Results packet: [Q01 results](results.md)

Interpretation status before execution: pending execution and user-led review.
