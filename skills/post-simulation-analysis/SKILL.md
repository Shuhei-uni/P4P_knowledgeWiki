---
name: post-simulation-analysis
description: Analyse existing Fluent results for a P4P experiment from its question, using proven extraction code and explicit evidence limits.
---

# Post-simulation analysis

Use this workflow for:

```text
DATA → ANALYSE → REPORT → results.md
```

Start from the experiment question, not from whichever script happens to
exist. Do not change physics, setup, or initialization in this skill; if the
checkpoint cannot answer the question, describe the evidence needed for the
setup/run workflow.

## Recover intent

Read the selected experiment `setup.md`, its existing `results.md`, and a
parent/comparison record only when needed. Identify the primary question,
controlled change, frozen comparison context, requested evidence, and actual
run/checkpoint available.

## Discover before choosing

Perform cheap, read-only discovery before committing to an analysis:

- case/data identity, Fluent/PyFluent version, and run horizon;
- active models, phases, zones, injections, film walls, and report definitions;
- residual/report histories, checkpoint files, field variables, and existing
  PyAnsys artifacts;
- comparison cases or checkpoints named by the setup.

`server_id`, hostname, port, version, and iteration count are routing or
diagnostic metadata, not case identity. If an open session cannot be mapped to
an explicit case/data identity, mark identity `unavailable` and do not make a
setup-linked claim.

## Choose the smallest relevant analysis

Choose analyses because they answer the setup question, not because a module
is available. When a generic request has materially different options, show a
compact menu with question, data source, method, cost/risk, and recommendation
then ask the user to choose. A cheap supporting check is allowed; a rerun,
new monitor, or setup change must be flagged first.

Use the focused specialist when relevant:

- uncertain live state → `fluent-live-inspection`;
- Report Plot/Report File history → `fluent-report-histories`;
- staged/restarted residuals → `residual-history-analysis`;
- DPM evidence → `dpm-analysis`;
- EWF evidence → `ewf-analysis`;
- liquid-pool register/patch/volume → `pool-patch-volume`.

## Proven-code rule

Inspect known-working repository code before constructing an equivalent
PyFluent access pattern from memory. Reuse the access pattern, not case-specific
names, values, paths, or branch assumptions. If the current live Fluent tree
differs, inspect and adapt.

Working code is stronger implementation evidence than prose. Do not copy old
case-specific report names, phases, directories, signs, or branch values
without verifying them against the current case.

## Analyse and preserve evidence

Preserve the native iteration or physical-time coordinate, units, exact scope,
sign convention, actual horizon, and status. Do not replace missing evidence
with zero, interpolate unknown gaps, or infer completion from filenames.

Classify each analysis as `complete`, `partial`, `unavailable`,
`not applicable`, `requires rerun`, or `blocked`. Separate extraction
completeness from scientific adequacy: a complete transcript can be irrelevant,
and a partial history can still be useful exploratory evidence.

## Report

Write evidence to the selected experiment's `Project/experiments/.../results.md`
and link raw JSON/CSV/plot/transcript artifacts. Keep these sections distinct:

```text
what ran | identity/horizon | measured values | numerical/evidence state
missing/incomplete evidence | neutral observations | findings/interpretation
```

Report evidence before meaning. Do not automatically choose a preferred model,
declare validation, or create the next experiment. `project-loop` owns the
findings/next-direction handoff; interpretation defaults to the user unless
explicitly delegated or governed by pre-agreed criteria.

## Known working code

- `PyAnsys/scripts/inspection/inspect_fluent_session.py`
- `PyAnsys/scripts/inspection/inspect_case.py`
- `PyAnsys/scripts/inspection/compare_case_setup.py`
- `PyAnsys/scripts/inspection/explore_settings_space.py`
- `PyAnsys/scripts/inspection/export_residuals.py`
- `PyAnsys/scripts/inspection/extract_report_plot_histories.py`

Use the specialist skills for the non-obvious rules around residual, report,
DPM, EWF, and pool evidence.
