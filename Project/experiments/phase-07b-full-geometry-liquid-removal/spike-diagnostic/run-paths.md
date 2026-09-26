# E3 execution paths

**Complete:** E3 reached N5000 via `p7b-s40-t020-diag-resume-20260922T122811Z`. Its final paired endpoint and full G3 evidence are preserved; [results](results.md) owns the disposition. There is no active E3 controller.

- Case: `S40-T020-DIAG`.
- Initial run: `p7b-s40-t020-diag-20260922T071533Z`.
- Runner: `PyAnsys/scripts/setup/run_phase07b_screen.py --spike-diagnostics`.
- Exact argv, working directory, task and controller identity:
  `PyAnsys/output/p7b-s40-t020-diag-20260922T071533Z/launch-command.json`.
- Original manifest and local transcript/flux evidence:
  `PyAnsys/output/p7b-s40-t020-diag-20260922T071533Z/`.
- Diagnostic manifest, every-iteration speed/trigger history, geometry and
  sampled cell fields: that run's `spike-diagnostics/` directory.
- PC paired files, native report and transcript: the live manifest is the
  authority; all are below
  `C:/Users/qtra338/P4P/experiments/phase-07b-full-geometry-liquid-removal`.
- Original T020 comparison:
  `PyAnsys/output/p7b-s40-t020-resume-20260921T231240Z/`.
- Existing current-task automation `phase-7b-e2-weaker-sink-supervision` is
  **Phase 7b autonomous convergence investigation**, every 15 minutes.
  It finishes E3/G3 before the later research and controlled-experiment loop.

## Controller-loss recovery

The original local controller disappeared after its complete N4283 callback,
without a terminal record. Its process was absent and its lock free; Fluent
was responsive at N4284 with the N4284 native scalar record, waiting inside
the pending chunk. This is an execution interruption of unknown local cause,
not a demonstrated numerical failure. The current pair was preserved as
`p7b-s40-t020-diag-20260922T071533Z-preserve-n04284-20260922T1210.cas.h5`
and matching data in the same PC case-data directory. Fluent's end-of-iteration
interrupt returned, but its `iterating` query alone did not establish that the
departed callback's pause was released. Live symbol/monitor inspection
identified native registration 12 separately from the replacement worker's
13; only 12 was unregistered and released. No physical iteration advanced.

Recovery evidence is under the original run's `recovery-20260922T1202/`.
The replacement implementation is `PyAnsys/scripts/setup/resume_phase07b_diagnostic.py`.
It verifies the unchanged live case, inherits the full prefix and snapshots,
recovers N4284 native flux/speed, and requires a five-iteration recording check
before proceeding to the original N4500/N5000 checkpoints. The native N4284
residual had not printed before interruption; recovery must obtain its native
boundary print rather than interpolate it. Exact recovery status and current
worker/manifest are owned by `phase-state.yaml`.

The first replacement precheck, `p7b-s40-t020-diag-resume-20260922T121727Z`,
issued zero iterations and stopped on that unprinted boundary row. The revised
worker `p7b-s40-t020-diag-resume-20260922T121952Z` recovered N4284 flux/speed,
but a callback keyword-signature error stopped its event thread at the same
iteration. Only this local failed controller was gracefully interrupted;
Fluent remained open and its registration 13 was retired and released.
The repaired callback passed the installed PyFluent adapter check. The active
worker is `p7b-s40-t020-diag-resume-20260922T122811Z`, with its job receipt at
the original recovery directory's `resume3-job-manifest.json`. The existing
heartbeat supervises it; no new automation or simultaneous controller exists.

Recovery passed at N4289: the pair was saved, Fluent's native boundary print
supplied all seven N4284 residuals, and continuous residual/flux/speed histories
were verified through N4301. Native scalar and speed parity checks passed
through N4289, with zero source-lag error across 4288 consecutive pairs and
all 19 earlier snapshots retained. The controller then entered the unchanged
N4289-to-N4500 chunk. The receipt is the active run's
`supervision/20260922T123007Z-recovery-pass.json`; no reload, initialization or
scientific/numerical setting change occurred.

Do not start another client or controller while this controller advances.
Check local evidence first. `phase-state.yaml` owns any reconciled recovery
that changes the active run. Stop scientific execution at N5000; complete
G3 analysis, then follow the [later autonomous investigation](../convergence-investigation/plan.md).
