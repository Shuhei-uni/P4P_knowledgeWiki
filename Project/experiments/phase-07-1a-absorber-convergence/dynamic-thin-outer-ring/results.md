# Independent C8 dynamic thin-outer-ring results — INCORRECT ABSORBER (v1)

## Scope and result status

**Historical/superseded on 2026-09-22.** This record covers the independent
Server-3 C8 family only. It reports a
complete all-wall C8-D0 development run and a **paused, non-terminal** C8-P0
pressure-child partial history. It does not claim a completed pressure ladder,
a useful outlet pressure, a C8 Stage-2 result, convergence, or physical
separator performance.

| Item | Status | Evidence |
| --- | --- | --- |
| C8-D0 all-wall development | Complete, active 5,000 | `independent-c8-d0-resume2-20260921T062500Z/run-manifest.json`, `reports.json`, `residuals.json` |
| C8 trigger receipt | Complete | `c8-d0-trigger-receipt-20260921T062500Z.json` |
| C8-P0 1.120 MPa | Paused/non-terminal; monitor history through active 2,800 | `c8-p0-retry-20260921T074500Z/run-manifest.json`, Server-3 monitor files, transcript |
| C8-P10 / P30 / P60 | Not run | No child manifest or terminal pair |
| Stage 2 | Not eligible | Stage-1 ladder is incomplete |

## C8-D0: completed all-wall parent

C8-D0 completed all 5,000 requested active iterations after recovery from an
earlier client transport interruption. Its selected terminal case/data pair is
the C8-only OneDrive parent identified in
[`deffered.md`](deffered.md). The terminal audit records all five named bottom bands
as walls, base inlet commands of 116.92 kg/s liquid and 80.69 kg/s vapor, and
the lower phase-2-only absorber at -116.92 kg/s integrated command.

The raw lower-liquid-mass samples over active 4,000--5,000 have median
**28.67767752217757 kg**. The predeclared C8 rule therefore fixed the opening
threshold at **22.942142017742057 kg**, sampled every 10 active iterations,
with 20 consecutive samples required. This is a monitor-selection result; it
does not itself demonstrate a viable pressure-outlet route.

## C8-P0: observed partial history

The initial P0 runner stopped before iteration because its three ring-flux
report-file objects were not available after the generic monitor reset. The
corrected retry recreated and bound all 21 required outputs, read the C8-D0
parent with the all-wall/source invariants intact, and passed the active-50
monitor gate.

At C8-P0 active 200, the lower-liquid mass was 37.91127124285271 kg and the
persistence counter reached 20. The runner saved local pre-switch and
post-switch paired states and changed only the thin outer ring to a pressure
outlet. Readback recorded 1,120,000 Pa gauge and phase-2 backflow volume
fraction 0; the remaining four bottom bands remained walls.

The runner was intentionally stopped by the human while non-terminal. Its
manifest has durable controller events through active 2,700. The Server-3
file-backed monitor histories contain a later, completed native row at 7,800
(C8-D0 native 5,000 + C8-P0 active 2,800), so that row is the last observed
P0 state; it is not a saved C8-P0 terminal checkpoint.

| P0 monitor, last 100 file rows at native 7,800 | Mean | Last row |
| --- | ---: | ---: |
| Lower-zone liquid mass | 23.7454 kg | 23.7120 kg |
| Total liquid mass | 6,441.49 kg | 6,477.04 kg |
| Ring mixture mass flux | -1,587.39 kg/s | -1,728.46 kg/s |
| Ring phase-1 mass flux | -9.012 kg/s | -8.321 kg/s |
| Ring phase-2 mass flux | -1,578.37 kg/s | -1,720.11 kg/s |
| Steam-outlet mixture mass flux | -154.84 kg/s | -189.64 kg/s |
| Steam-outlet phase-1 mass flux | -60.50 kg/s | -59.81 kg/s |
| Steam-outlet phase-2 mass flux | -94.25 kg/s | -129.75 kg/s |

Flux sign convention has not been independently normalized in this partial
record. The ring values show that the partial history is overwhelmingly
phase-2 in magnitude under Fluent's reported convention, while the steam
outlet retains a substantial phase-1 component. This is an observation only:
the run lacks the requested 5,000-active horizon, complete residual report,
storage/source balance analysis, and terminal paired artifact, so it cannot
support a claim of preferential liquid routing, acceptable balance, or a
selected pressure.

## Server-3 pause verification

A read-only Server-3 check after the stop found Ansys Fluent 2025 R2
non-iterating, with the P0 outer ring still present as a 1.120 MPa pressure
outlet, phase-2 backflow fraction 0, and the other four bottom bands still
walls. No case was loaded, changed, saved, or resumed during this check.

## Requested spatial contours: verified source, export gap

The requested contours have a verified source and presentation specification,
but no image is claimed or embedded because the Server-3 Fluent graphics
hardcopy service did not return a PNG. This is a postprocessing/export gap,
not a missing field or a substitute visualization.

| Requested native Fluent figure | Verified source | Surface and field | Intended scale | Export status |
| --- | --- | --- | --- | --- |
| Pressure contour | Stopped C8-P0 live state, native iteration 7,800 / active 2,800 | Existing `plane-14`, Y-Z plane at x = 0 m; `pressure` | Single-state Fluent range | Graphics display/hardcopy stalled before file creation |
| Phase-2 volume-fraction contour | Same stopped C8-P0 state | Same `plane-14`; `phase-2-vof` | Fixed physical range 0--1 | Graphics display/hardcopy stalled before file creation |

The live Fluent readback proved that `plane-14` is the x = 0 m Y-Z plane and
that both `pressure` and `phase-2-vof` are valid contour fields in Ansys
Fluent 2025 R2. A 2560 × 1440 native-PNG export was configured and sent to a
Server-3-local C8 figures path. No output file appeared before the graphics
call stalled; the owned postprocessing clients were terminated without
iterating, saving, loading, or changing the paused case. No HTML, plotting,
image-generation, or other non-Fluent substitute has been made.

This does not alter the C8-P0 numerical interpretation above. A future
authorized postprocessing pass needs a responsive Fluent graphics/hardcopy
endpoint to export the two exact native figures under the stated provenance.

A second fresh-session export attempt used the same verified live state and
plane, a new Server-3-local figures directory, and explicit 2048 × 1536 PNG
hardcopy settings. It exited without either requested PNG appearing. This
confirms that the obstacle is the current attached endpoint's graphics/hardcopy
availability, not the selected field names, plane, or an inherited graphics
object. The paused C8 solver state was not iterated, saved, loaded, or changed.

## Decision trail and claim limit

| Decision | Evidence | Result |
| --- | --- | --- |
| Select C8-D0 parent | Complete all-wall 5,000-active C8-D0 pair with audited source/boundaries | Parent is usable and identified; retained unchanged |
| Derive switch trigger | Raw C8-D0 active-4,000--5,000 lower-liquid history | Fixed threshold/persistence receipt |
| Switch C8-P0 ring | P0 active-200 persistence reached 20 samples | Local pre/post switch pairs and boundary readback preserved |
| Stop campaign | Direct human instruction | No further C8 solve or recovery is authorized |

The smallest future action, only after explicit human restart authority, is to
choose a verified local P0 checkpoint as a parent or begin a fresh P0 child
from C8-D0; that is not performed here.
