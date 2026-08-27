---
name: ewf-analysis
description: Extract and assess Eulerian Wall Film evidence for confirmed active film walls and mechanisms when EWF is relevant to the experiment question.
---

# EWF analysis

Run this skill only when EWF is active and relevant to the setup question.

## Rules

- Verify actual film walls, active mechanisms, phase coupling, and extraction
  scope before reading a result.
- Preserve exact wall/surface scope.
- Keep inventory/cumulative quantities (`kg`) distinct from rates/sources
  (`kg/s`).
- Keep local, maximum, and area-weighted reductions distinct.
- A final data file is a snapshot; it cannot establish time-integrated closure
  without the required histories.
- Missing fields do not prove an inactive mechanism or zero contribution;
  check state and live evidence.

Inspect known-working repository code before constructing an equivalent
PyFluent access pattern from memory. Reuse the access pattern, not case-specific
names, values, paths, or branch assumptions. If the current live Fluent tree
differs, inspect and adapt.

## Known working code

Prefer reusable `src` code before a campaign-specific script; live EWF state
wins over prose/API memory.

- `PyAnsys/src/pyansys_fluent/ewf_core.py`
- `PyAnsys/src/pyansys_fluent/ewf_audit.py`
- `PyAnsys/src/pyansys_fluent/ewf_flux.py`
- `PyAnsys/src/pyansys_fluent/ewf_reports.py`
- `PyAnsys/src/pyansys_fluent/ewf_report_specs.py`
- `PyAnsys/src/pyansys_fluent/ewf_diagnostics.py`
- `PyAnsys/scripts/inspection/run_ewf_dpm_diagnostics.py`

Use live inspection when wall names, mechanisms, phases, or available fields
differ from the proven implementation.
