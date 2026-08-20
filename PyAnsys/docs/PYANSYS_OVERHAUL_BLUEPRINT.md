# PyAnsys Overhaul Blueprint

This file records the intended architecture, not a second copy of `PyAnsys/AGENTS.md`.

## Core structure

- `src/pyansys_fluent/` contains reusable mechanics.
- `scripts/connection/` contains bootstrap/preflight work.
- `scripts/inspection/` contains read-only discovery/analysis.
- `scripts/setup/` contains thin case-specific setup/run orchestration.
- `knowledge/fluent-settings/` contains dependency/path/run knowledge.

Case-specific scripts should stay thin; repeated mechanics belong in `src/`.

## Fluent mutation rule

Most setup failures come from wrong dependency order, stale handles, or version-specific paths.

Use:

```text
connect -> verify input -> load -> enable/create parent -> reacquire -> inspect -> set -> read back
```

If a setting fails, isolate the smallest branch and classify the failure before choosing a Settings API, TUI, or manual fallback.

## Three workflow responsibilities

Keep these separate:

1. **Setup building** — produce and verify the Fluent case.
2. **Run planning** — choose the execution mode and recovery strategy.
3. **Run execution** — execute and hand off status/evidence.

Run-mode choice:

- **Simple TUI** for one uninterrupted prepared case.
- **Fluent journal** for independent/fixed batches.
- **Agent-owned Python** for staged/adaptive workflows where intermediate evidence controls the next step.

Complex Python runs should be recoverable state machines and must include an exact launch command plus supervisor/resume guidance.

Detailed run guidance lives in `../knowledge/fluent-settings/native_run_and_autosave.md`.

## Visibility rule

Shared helpers must not hide known Fluent-state uncertainty. For version-sensitive or unstable paths:

- preserve the intended physics;
- inspect/read back the live state;
- expose failure clearly;
- record verified paths/order dependencies when discovered.

## Storage rule

`PyAnsys/output/` is generated evidence/scratch space, not an archive. Keep outputs that support checks, analysis, result reports, plots or reproducibility; prune temporary and superseded bulk once it is no longer needed.
