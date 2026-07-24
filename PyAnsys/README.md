# PyAnsys / PyFluent Remote Fluent Ready Kit

Use this kit to prepare your laptop now, before you have access to the PC with Ansys Fluent.

The folder has been reorganized around one rule: Fluent automation is a dependency-ordered state machine, not a flat Python API. If syntax, nesting, or call-order problems appear, start with the execution contract below rather than editing the case scripts ad hoc.

The current operating split is strict:
- setup scripts create or modify only `.cas.h5`
- `scripts/setup/save_data_after_iterations.py` is the standard path for loading that case, hybrid-initializing it, running iterations, and writing only `.dat.h5`

Recommended local target:

```text
- CPython 3.12 virtual environment in PyAnsys/.venv
- PyFluent core + visualization installed locally
- connect_to_fluent workflow only
```

Your target workflow:

```text
Laptop:
- Codex
- Python
- PyFluent / PyAnsys packages
- scripts in this repo

      connects over gRPC

Fluent PC:
- Ansys Fluent installed and licensed
- Fluent running
- Fluent gRPC server started
- server_info.txt generated
```

What you can do now:

```bash
python3 scripts/connection/bootstrap_local_env.py
```

This script prefers Python 3.12. If `python3.12` is not already installed, it can
also use `uv` to create a local 3.12 environment automatically.

When you are at the Fluent PC:

1. Start Fluent.
2. Start the gRPC server.
3. Copy IP/port/password or `server_info.txt`.
4. Fill `.env`.
5. Run:

```bash
.venv/bin/python scripts/connection/check_connection.py
.venv/bin/python scripts/inspection/inspect_fluent_session.py
```

## Canonical workflow

Read these in order before changing any setup script:

1. [`knowledge/fluent-settings/agent_start_prompt.md`](./knowledge/fluent-settings/agent_start_prompt.md)
2. [`docs/PYANSYS_OVERHAUL_BLUEPRINT.md`](./docs/PYANSYS_OVERHAUL_BLUEPRINT.md)
3. [`docs/AUTONOMOUS_FLUENT_LOOP_PLAN.md`](./docs/AUTONOMOUS_FLUENT_LOOP_PLAN.md) for the staged path from the current tools to a recoverable agent-operated loop
4. [`src/pyansys_fluent/common.py`](./src/pyansys_fluent/common.py)
5. [`src/pyansys_fluent/dependency_workflow.py`](./src/pyansys_fluent/dependency_workflow.py)
6. [`src/pyansys_fluent/setup_common.py`](./src/pyansys_fluent/setup_common.py)

Execution sequence:

```text
connect
-> verify remote inputs
-> load mesh or source case
-> enable parent model
-> reacquire object
-> inspect children/options
-> set child value
-> read back value
-> classify failure
-> choose settings API / TUI / manual fallback
-> write `.cas.h5`
```

Run sequence after setup creation:

```text
connect
-> verify remote `.cas.h5`
-> load case only
-> hybrid initialize
-> iterate
-> write derived `name_X.dat.h5`
-> verify Fluent can see the written data file
```

## Current script layout

- `scripts/connection/check_connection.py`: connection health check only
- `scripts/orchestration/fluent_host_worker.py`: Windows-host Fluent process ownership, heartbeat, and bounded relaunch smoke-test worker
- `scripts/inspection/inspect_fluent_session.py`: non-mutating tree inspection
- `src/pyansys_fluent/common.py`: shared remote/session/path helpers
- `src/pyansys_fluent/host_worker.py`: reusable host-worker process, gRPC health, restart-budget, and atomic-status mechanics
- `src/pyansys_fluent/dependency_workflow.py`: dependency-aware step runner and failure classifier
- `src/pyansys_fluent/extraction.py`: shared read-mostly extraction helpers for live/offline setup capture
- `src/pyansys_fluent/setup_common.py`: shared setup-name, boundary, and remap helpers
- `src/pyansys_fluent/setup_io.py`: shared setup/run file IO helpers including case-only loading
- `scripts/setup/save_data_after_iterations.py`: focused runner from `.cas.h5` to `name_X.dat.h5`
- `scripts/setup/setup07_rebuild_run.py`: rebuild setup 07 on a target mesh
- `scripts/setup/setup09a_dpm_split_inlet_carryover.py`: build setup 09a from the setup 07 carrier-field scaffold
- `scripts/setup/setup_vof_ewf_from_existing_case.py`: derive a VOF + EWF case from an existing case/data pair
- `scripts/setup/rebuild_setup_from_reference_case.py`: clone a reference setup onto another mesh

Host-worker trial instructions:

- [`docs/FLUENT_HOST_WORKER.md`](./docs/FLUENT_HOST_WORKER.md)

## Extractor tracks

Two separate extractor paths are now scaffolded:

- `extractors/python/`: offline `.cas.h5` / `.dat.h5` inspection with `h5py`
- `extractors/python/`: offline legacy `.cas` and `.dat` inspection, plus HDF5 support where available
- `extractors/fluent/`: live Fluent/PyFluent export tools, including a fuller hybrid live+offline bundle exporter

Recommended order:

1. use `extractors/python/` now on any HDF5 case/data files you already have;
2. review the candidate strings and tree layout;
3. use `extractors/fluent/` later on the Fluent machine to export the real active setup tree and reconcile gaps.
