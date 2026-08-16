# Full Geometry — Mixture Transient Liquid-Outlet Reports

Corresponding setup campaign: [Mixture transient liquid-outlet setups](../../../../full-geometry/mixture/transient-liquid-outlet/index.md).

**Current status:** Stage 1 execution is complete; Stage 2 startup-state case construction is complete and the user accepted the small physical INIT-S/INIT-H difference. The original Stage 3 initialization sweep failed, and the sequential no-patch recovery `NP-DT1` also failed with a floating-point exception before its requested `200` transient steps completed. No Stage 3 endpoint or complete physical-time history exists.

## Available evidence

- [Stage-1 candidate screen](stage-01-candidate-screen-20260816.md)
- [Stage-2 startup-state construction](stage-02-start-states-20260816.md)
- [Stage-3 initialization comparison and cancellation record](stage-03-initialization-comparison-20260816.md)
- [Stage-3 NP-DT1 no-patch transient control](stage-03-no-patch-NP-DT1-20260817.md)

## Planned report sequence

As the setup stages run, create evidence packets here, for example:

```text
stage-01-02-steady-parent-and-transient-start-results.md
stage-03-initialization-comparison-results.md
stage-04-transient-numerical-qualification-results.md
stage-05-outlet-family-preflight-results.md
stage-06-six-case-screen-results.md
```

These are report filenames, not setup IDs. A stage can use a different descriptive report filename when that better reflects the actual evidence produced.

## Report contract

Each report must link to the setup/stage plan that defined the run and record:

- actual case/data identity;
- what was actually run and any deviations;
- relevant measured/derived evidence;
- numerical limitations;
- neutral observations;
- interpretation status, defaulting to pending user direction.

Do not place stage plans or build instructions in this folder.
