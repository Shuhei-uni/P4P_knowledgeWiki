# PyAnsys Overhaul Blueprint

This folder now has one canonical mental model:

1. connection and remote-file mechanics live in `src/pyansys_fluent/common.py` and `src/pyansys_fluent/connection.py`
2. dependency-aware execution logic lives in `src/pyansys_fluent/dependency_workflow.py`
3. shared setup-specific boundary and remap helpers live in `src/pyansys_fluent/setup_common.py`
3. case-specific scripts should be thin orchestration layers on top of those two modules

## Why this overhaul exists

The recurring failures were not random:

- syntax drift between one-off scripts
- deep nesting without a clear execution contract
- setting children before parent models were enabled
- using stale object handles after model/type changes
- inconsistent fallback decisions between Settings API, TUI, and manual GUI cleanup

The fix is to stop treating each setup script as a standalone experiment.

## Canonical call order

Every non-trivial Fluent mutation should follow this sequence:

1. connect
2. verify remote inputs exist
3. load case or mesh
4. enable parent model or create parent object
5. refresh and reacquire the live object
6. inspect child names, command names, and allowed values
7. set the child value
8. refresh and reacquire again if the parent changed
9. read back the value
10. classify any failure before deciding the fallback

## Script layering

- `check_connection.py`
  Purpose: connectivity only
- `inspect_fluent_session.py`
  Purpose: non-mutating live discovery
- `src/pyansys_fluent/common.py`
  Purpose: shared remote/session mechanics
- `src/pyansys_fluent/dependency_workflow.py`
  Purpose: reusable step runner and failure classifier
- `src/pyansys_fluent/setup_common.py`
  Purpose: reusable boundary naming, remapping, and setup-state helpers
- `scripts/setup/setup07_rebuild_run.py`, `scripts/setup/setup09a_dpm_split_inlet_carryover.py`, `scripts/setup/setup_vof_ewf_from_existing_case.py`, `scripts/setup/rebuild_setup_from_reference_case.py`
  Purpose: case-specific orchestration only

## Failure routing

Use these buckets consistently:

- `order/dependency issue`
- `path/version issue`
- `invalid value/format issue`
- `PyFluent wrapper limitation`
- `requires TUI fallback`
- `requires manual GUI cleanup`

If a step fails, do not restart the whole setup immediately. Isolate the failing parent/child branch first.

## What to refactor next

The current overhaul centralizes shared helpers, but the large case scripts still contain long procedural sections. The next cleanup pass should split those scripts into:

- input collection
- case loading and role mapping
- model enablement blocks
- boundary application blocks
- solve/write blocks

That should be done without changing the dependency-order contract above.
