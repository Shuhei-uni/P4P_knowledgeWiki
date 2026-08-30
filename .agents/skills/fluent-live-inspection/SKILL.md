---
name: fluent-live-inspection
description: Inspect an uncertain live Fluent/PyFluent session, Settings branch, object name, allowed value, or case state before implementing or analysing a change.
---

# Fluent live inspection

Use this skill when a PyFluent path, object identity, allowed value,
model/phase/domain state, or loaded-session identity is uncertain. Do not guess
deep Settings paths from memory.

## Workflow

1. Connect using the server ID only as transport routing.
2. Inspect the loaded case/data and current session state.
3. Inspect the smallest relevant Settings branch, children, commands, and
   allowed values.
4. If a parent/model/type change is required, perform it through the
   implementation workflow, then reacquire affected objects.
5. Inspect again and read back critical state after mutation.

Use the live tree as authority for the current case and Fluent version. A
missing expected path means inspect/adapt; it does not prove that the model is
disabled or that an old recipe should be forced.

If the live tree cannot safely resolve the setting's meaning, documented
prerequisites, activation order, or a verifiable Settings API/TUI mutation
path, escalate automatically to `fluent-manual-researcher`. That skill must
consult the version-matched official Fluent manual, translate the documented
GUI/model state into a disposable live implementation attempt, and return only
a save/reopen-verified recipe or a bounded research blocker. Do not keep
probing or inventing paths once the uncertainty is semantic rather than merely
structural.

## Known working code

Prefer reusable `src` code, then a generic script, then a campaign pattern;
prose/API memory is last and the live tree wins.

- `PyAnsys/scripts/inspection/inspect_fluent_session.py`
- `PyAnsys/scripts/inspection/inspect_case.py`
- `PyAnsys/scripts/inspection/explore_settings_space.py`
- `PyAnsys/scripts/inspection/compare_case_setup.py`
- `PyAnsys/scripts/inspection/load_case_data.py`
- `PyAnsys/src/pyansys_fluent/dependency_workflow.py`

Inspect known-working repository code before constructing an equivalent
PyFluent access pattern from memory. Reuse the access pattern, not case-specific
names, values, paths, or branch assumptions. If the current live Fluent tree
differs, inspect and adapt.
