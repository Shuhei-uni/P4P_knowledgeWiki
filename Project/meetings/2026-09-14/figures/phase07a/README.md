# Phase 07A figure package

The intended message is a matched lower-plane comparison: corrected E0
reference versus the selected lower cell-zone absorber. Both views use the
same native Fluent `ZX` plane at `Y = 0.05 m`, phase-2 volume fraction as a
contour-only field, fixed display range `0–1`, orthographic normal-to-plane
camera, and `2400 × 1800` colour export. No vectors are included in the
contour figures.

## Source identities

| Figure | Exact paired source | Checkpoint status |
|---|---|---|
| E0 reference | `C:\Users\syok443\Documents\FluentRuns\Phase07\P7-E0-REF\rerun-20260908T170000Z\final-iter2000.cas.h5` plus matching `.dat.h5` | Corrected reference, final active 2000 |
| E5 absorber | `C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase07\CellZoneAbsorberColdContinuation\20260910T211158Z\P7-E5-CZ-ABSORB-COLD-RAMP11692-CONT5000\checkpoint-1900-1-01900.cas.h5` plus matching `.dat.h5` | Last durable paired state at active 1900; history valid through approximately active 1960, divergence around active 1970 |

## Current exports

- [E0 lower phase-2 contour](P07A-E0-FINAL2000-lower-phase2-vof-contour.png)
  is a native Fluent contour-only export and passed the initial visual check.
- [E5 absorber lower phase-2 contour](P07A-E5-ACTIVE1900-lower-phase2-vof-contour.png)
  is also a native Fluent contour-only export. Its current native view is
  too tightly cropped and does not yet have the same framing as E0, so it is
  **provisional and should not be inserted as the final matched pair** until
  the student/server endpoint is recovered for one camera re-export.

The E5 surface readback was effectively zero phase-2 volume fraction across
the sampled plane (`min = max = 0`), which is consistent with the intended
selectivity message: implementing the absorber source and delivering liquid
to the absorber region are separate questions. This is not evidence of
successful removal.

No patch/reset was used in this E5 experiment, so a post-patch comparison is
not required for this figure pair.
