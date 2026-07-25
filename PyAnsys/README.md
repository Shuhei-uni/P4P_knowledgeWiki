# PyAnsys / PyFluent Laptop-Controlled Fluent Kit

The laptop agent is the controller and researcher. The licensed Fluent computer
is a self-healing Fluent host with one optional, narrow run worker.

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

Target workflow:

```text
Laptop:
- Codex
- Python
- PyFluent / PyAnsys packages
- setup plan, scientific decisions, and step ledger
- direct inspection, Settings API, and TUI commands

      connects over gRPC

Fluent PC:
- Ansys Fluent installed and licensed
- watchdog launches and restarts Fluent
- latest connection generation is published out of band
- narrow worker can load/run/checkpoint/save when explicitly requested
```

The watchdog never builds a case or chooses a checkpoint. The run worker never
restarts Fluent or automatically resumes an interrupted request.

What you can do now:

```bash
python3 scripts/connection/bootstrap_local_env.py
```

This script prefers Python 3.12. If `python3.12` is not already installed, it can
also use `uv` to create a local 3.12 environment automatically.

For the self-healing workflow:

1. Configure a private shared `FLUENT_BRIDGE_DIR` on both computers.
2. Set `FLUENT_ADVERTISED_HOST` on the Fluent PC.
3. Start `scripts/orchestration/fluent_watchdog.py` on the Fluent PC.
4. Optionally start `scripts/orchestration/fluent_run_worker.py`.
5. Connect from the laptop; the helper rereads `latest_connection.json`.

```bash
.venv/bin/python scripts/connection/check_connection.py
.venv/bin/python scripts/inspection/inspect_fluent_session.py
```

See [`docs/LAPTOP_CONTROLLED_FLUENT.md`](./docs/LAPTOP_CONTROLLED_FLUENT.md)
for deployment, request schemas, recovery, and forced-crash validation.
See [`docs/SETUP_TO_RESULTS_WORKFLOW.md`](./docs/SETUP_TO_RESULTS_WORKFLOW.md)
for the complete setup Markdown → direct agent build → run → recovery →
analysis → result-package workflow.

## Canonical workflow

Read these in order before changing any setup script:

1. [`knowledge/fluent-settings/agent_start_prompt.md`](./knowledge/fluent-settings/agent_start_prompt.md)
2. [`docs/PYANSYS_OVERHAUL_BLUEPRINT.md`](./docs/PYANSYS_OVERHAUL_BLUEPRINT.md)
3. [`src/pyansys_fluent/common.py`](./src/pyansys_fluent/common.py)
4. [`src/pyansys_fluent/dependency_workflow.py`](./src/pyansys_fluent/dependency_workflow.py)
5. [`src/pyansys_fluent/setup_common.py`](./src/pyansys_fluent/setup_common.py)

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
laptop saves verified `.cas.h5`
-> laptop submits strict run request
-> worker validates the expected Fluent generation
-> replay the agent-verified initialization TUI sequence once,
   or load an explicit laptop-selected resume pair with no initialization
-> iterate in chunks and write recovery pairs
-> retain only the newest recovery pair and its predecessor
-> save final `.dat.h5`
-> return a secret-free receipt
```

## Current script layout

- `scripts/connection/check_connection.py`: connection health check only
- `scripts/orchestration/fluent_watchdog.py`: Fluent lifecycle, health, restart, and connection publication only
- `scripts/orchestration/fluent_run_worker.py`: narrow load/run/checkpoint/save worker only
- `scripts/orchestration/submit_run_request.py`: laptop-side strict run-request submission
- `scripts/orchestration/laptop_workflow.py`: laptop-owned setup-plan, ledger, run handoff, recovery, analysis, and result-package state
- `scripts/inspection/inspect_fluent_session.py`: non-mutating tree inspection
- `src/pyansys_fluent/agent_ledger.py`: laptop-owned build/recovery state
- `src/pyansys_fluent/laptop_workflow.py`: verified phase transitions from setup Markdown to result manifest
- `src/pyansys_fluent/bridge.py`: private connection/status bridge contracts
- `src/pyansys_fluent/run_worker.py`: strict request, receipt, and checkpoint mechanics
- `src/pyansys_fluent/common.py`: shared remote/session/path helpers
- `src/pyansys_fluent/dependency_workflow.py`: dependency-aware step runner and failure classifier
- `src/pyansys_fluent/extraction.py`: shared read-mostly extraction helpers for live/offline setup capture
- `src/pyansys_fluent/setup_common.py`: shared setup-name, boundary, and remap helpers
- `src/pyansys_fluent/setup_io.py`: shared setup/run file IO helpers including case-only loading
- `scripts/setup/save_data_after_iterations.py`: focused runner from `.cas.h5` to `name_X.dat.h5`
- `scripts/setup/setup07_rebuild_run.py`: rebuild setup 07 on a target mesh
- `scripts/setup/setup09a_dpm_split_inlet_carryover.py`: build setup 09a from the setup 07 carrier-field scaffold
- `scripts/setup/setup_vof_ewf_from_existing_case.py`: derive a VOF + EWF case from an existing case/data pair
- `scripts/setup/rebuild_setup_from_reference_case.py`: clone a reference setup onto another mesh

## Extractor tracks

Two separate extractor paths are now scaffolded:

- `extractors/python/`: offline `.cas.h5` / `.dat.h5` inspection with `h5py`
- `extractors/python/`: offline legacy `.cas` and `.dat` inspection, plus HDF5 support where available
- `extractors/fluent/`: live Fluent/PyFluent export tools, including a fuller hybrid live+offline bundle exporter

Recommended order:

1. use `extractors/python/` now on any HDF5 case/data files you already have;
2. review the candidate strings and tree layout;
3. use `extractors/fluent/` later on the Fluent machine to export the real active setup tree and reconcile gaps.
