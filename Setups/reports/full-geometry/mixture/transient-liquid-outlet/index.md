# Full Geometry — Mixture Transient Liquid-Outlet Reports

Corresponding setup campaign: [Mixture transient liquid-outlet setups](../../../../full-geometry/mixture/transient-liquid-outlet/index.md).

**Current status:** Stage 1 execution is complete; Stage 2 startup-state case construction is complete and the user accepted the small physical INIT-S/INIT-H difference. The original Stage 3 initialization sweep failed, and the sequential no-patch recovery `NP-DT1` also failed with a floating-point exception before its requested `200` transient steps completed. No Stage 3 endpoint or complete physical-time history exists.

## Experiment folders

- [Stage 1 — candidate screen](stage-01/index.md)
- [Stage 2 — startup-state construction](stage-02/index.md)
- [Stage 3 — initialization and transient controls](stage-03/index.md)

## Planned report sequence

As the setup stages run, create evidence packets inside the matching stage folder, for example:

```text
stage-01/
  stage-01-candidate-screen-results.md
stage-02/
  stage-02-start-states-results.md
stage-03/
  stage-03-initialization-comparison-results.md
stage-04/
  stage-04-transient-numerical-qualification-results.md
```

These are experiment folders, not additional setup IDs. A stage can use a different descriptive report filename when that better reflects the actual evidence produced.

## Report contract

Each report must link to the setup/stage plan that defined the run and record:

- actual case/data identity;
- what was actually run and any deviations;
- relevant measured/derived evidence;
- numerical limitations;
- neutral observations;
- interpretation status, defaulting to pending user direction.

Do not place stage plans or build instructions in this folder.
