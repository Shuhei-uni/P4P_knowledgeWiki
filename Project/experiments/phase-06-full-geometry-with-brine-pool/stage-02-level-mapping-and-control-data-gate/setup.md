# Phase 06 / Stage 02 — level mapping and control-data gate

## Stage question

Can the F11 full-geometry field be converted into a pool-level observable that
is traceable to a real measurement location and can therefore support a
physically specified brine-pool control condition?

This stage reduces the observable/control-data prerequisite of the fixed
Phase-06 question. It does not select a new outlet coefficient, controller, or
multiphase model.

## Carried Stage-01 evidence

The completed reference and matched `K=10` outlet-vent screens show that the
existing lower-region phase-2 liquid-mass histories respond consistently to
boundary changes. They are explicitly **inventory proxies**, not pool level.
The `K=10` test worsened drainage and closure, so it is not continued as a
candidate outlet condition.

## What is available in the live F11-derived case

**Observed by read-only inspection after `P6-S1-O`.** The active full-geometry
fluid zone is `simple-spiral-separator--brine-outlet-`. It carries two existing
cell-register selections:

| Register | Box bounds | Existing use | Evidential status |
|---|---|---|---|
| `codex_y010_pool_below_y_0p10m` | x=[−2.067034, 1.066098], y=[−1.484584, 0.10], z=[−1.469893, 2.0] m | lower-region liquid-mass inventory | geometry-specific, not an instrument location |
| `codex_y030_monitor_below_y_0p30m` | x=[−2.067034, 1.066098], y=[−1.484584, 0.30], z=[−1.469893, 2.0] m | wider lower-region liquid-mass inventory | geometry-specific, not an instrument location |

Volume-report definitions exist for these registers, including geometric and
phase-2 liquid-volume forms. Their file-backed histories were not retained
through the prior settings/save-reopen path, so they cannot yet establish a
durable volume-to-elevation curve.

## Required evidence before a physical level mapping

1. Instrument type and measurement reference: e.g. interface elevation,
   differential pressure, or calibrated vessel volume.
2. Instrument centreline/elevation and the mapping from plant datum to the CFD
   coordinate system.
3. Normal setpoint and admissible operating band.
4. Confirmation that the lower vessel geometry and brine outlet in the CFD
   mesh represent the relevant real pool region.
5. A durable calculation/export path for selected-cell geometric volume and
   phase-2 volume/fraction at a set of elevations.

Without items 1–4, a CFD volume-elevation curve is a generic mesh coordinate
map only. It cannot be labelled the separator's indicated level or control
target.

## Execution boundary

The next mapping action may inspect report definitions and calculate geometric
or phase-integrated volumes without changing the loaded case. It must not
patch liquid, alter boundaries, initialize, iterate, or save a case/data pair
unless a separate selected experiment requests those actions. Pool patching is
an initial-condition operation, not a substitute for a level measurement.

## Decision gate

- If authoritative instrument and control data are found, construct a
  geometry/phase-specific volume-to-level mapping and advance to a specified
  quasi-steady control representation test.
- If no such data are available, return to the human for the missing physical
  boundary rather than inventing a setpoint, sensor location, valve curve, or
  controller law.
