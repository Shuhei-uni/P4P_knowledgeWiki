# PyAnsys / PyFluent Remote Fluent Ready Kit

Use this kit to prepare your laptop now, before you have access to the PC with Ansys Fluent.

The folder has been reorganized around one rule: Fluent automation is a dependency-ordered state machine, not a flat Python API. If syntax, nesting, or call-order problems appear, start with the execution contract below rather than editing the case scripts ad hoc.

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

For the complete Purnanto enthalpy/DPM workflow, recovery procedure, output
contract, and mesh-convergence handoff, use
[`docs/PURNANTO_ENTHALPY_DPM_AUTOMATION_RUNBOOK.md`](./docs/PURNANTO_ENTHALPY_DPM_AUTOMATION_RUNBOOK.md).

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

### Guarded remote runs

Remote Fluent can fail in two different ways:

- the TCP port is closed/refused, which the connection preflight catches quickly;
- the TCP port stays open but Fluent gRPC stops answering, which can make a local
  PyFluent client hang.

Use the guarded runner for remote checks and long runs so a stuck client is
terminated locally instead of waiting indefinitely:

```bash
.venv/bin/python scripts/connection/run_guarded.py --idle-timeout-seconds 90 -- \
  .venv/bin/python -u scripts/connection/check_connection.py \
    --connect-timeout-seconds 60 \
    --health-timeout-seconds 15
```

For a one-case smoke run, keep the idle timeout short enough to catch a wedged
RPC but long enough for case loading:

```bash
.venv/bin/python scripts/connection/run_guarded.py --idle-timeout-seconds 600 -- \
  .venv/bin/python -u scripts/setup/run_purnanto_enthalpy_sweep.py \
    --apply \
    --case-filter 1600 \
    --iterations 1 \
    --report-interval 1 \
    --checkpoint-interval 0
```

For overnight sweeps, use `caffeinate` and a larger idle timeout:

```bash
caffeinate -dimsu .venv/bin/python scripts/connection/run_guarded.py --idle-timeout-seconds 1800 -- \
  .venv/bin/python -u scripts/setup/run_purnanto_enthalpy_sweep.py \
    --apply \
    --iterations 1500 \
    --report-interval 100 \
    --checkpoint-interval 500
```

If the TCP check succeeds but `check_connection.py` times out, the Mac can reach
the port but the Fluent gRPC session is likely wedged. Restart Fluent or the
Fluent gRPC server on the Windows PC before starting a sweep.

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
-> load mesh/case/data
-> enable parent model
-> reacquire object
-> inspect children/options
-> set child value
-> read back value
-> classify failure
-> choose settings API / TUI / manual fallback
```

## Current script layout

- `scripts/connection/check_connection.py`: connection health check only
- `scripts/inspection/inspect_fluent_session.py`: non-mutating tree inspection
- `src/pyansys_fluent/common.py`: shared remote/session/path helpers
- `src/pyansys_fluent/dependency_workflow.py`: dependency-aware step runner and failure classifier
- `src/pyansys_fluent/setup_common.py`: shared setup-name, boundary, and remap helpers
- `scripts/setup/setup07_rebuild_run.py`: rebuild setup 07 on a target mesh
- `scripts/setup/setup09a_dpm_split_inlet_carryover.py`: build setup 09a from the setup 07 carrier-field scaffold
- `scripts/setup/setup_vof_ewf_from_existing_case.py`: derive a VOF + EWF case from an existing case/data pair
- `scripts/setup/rebuild_setup_from_reference_case.py`: clone a reference setup onto another mesh

## Extractor tracks

Two separate extractor paths are now scaffolded:

- `extractors/python/`: offline `.cas.h5` / `.dat.h5` inspection with `h5py`
- `extractors/python/`: offline legacy `.cas` and `.dat` inspection, plus HDF5 support where available
- `extractors/fluent/`: live Fluent/PyFluent export skeleton for on-site use

Recommended order:

1. use `extractors/python/` now on any HDF5 case/data files you already have;
2. review the candidate strings and tree layout;
3. use `extractors/fluent/` later on the Fluent machine to export the real active setup tree and reconcile gaps.
