---
name: fluent-report-histories
description: Recover and analyse Fluent Report Plot or Report File histories when live PyFluent monitor buffers may not contain the samples.
---

# Fluent report histories

Use this skill when the experiment needs report-monitor history and the evidence
may be stored in Fluent Report Files rather than the current live monitor
buffer.

## Rules

- Inspect configured report definitions and report files first.
- Do not assume a relative `.out` path is beside the `.cas/.dat` pair; use the
  actual remote report directory.
- Do not treat an absent or unreadable file as a zero-valued history.
- Preserve the native iteration/time coordinate, definition, source path,
  units, scope, and point count.
- If the history was never recorded and cannot be reconstructed, classify it as
  `unavailable` or `requires rerun`.

Inspect known-working repository code before constructing an equivalent
PyFluent access pattern from memory. Reuse the access pattern, not case-specific
names, values, paths, or branch assumptions. If the current live Fluent tree
differs, inspect and adapt.

## Known working code

Prefer the reusable or proven parser before a campaign-specific adaptation;
live Fluent/file evidence wins over prose/API memory.

- `PyAnsys/scripts/inspection/extract_report_plot_histories.py`

Inspect its Fluent file-read and parsing behaviour, pass the actual remote
directory, and preserve an explicit parser failure when a Fluent release
serializes data differently. Do not change Fluent's working directory merely to
make a relative path resolve.
