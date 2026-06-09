# PyAnsys / PyFluent Remote Fluent Ready Kit

Use this kit to prepare your laptop now, before you have access to the PC with Ansys Fluent.

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
python3 scripts/bootstrap_local_env.py
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
.venv/bin/python scripts/check_connection.py
.venv/bin/python scripts/inspect_fluent_session.py
```

## Extractor tracks

Two separate extractor paths are now scaffolded:

- `extractor_python/`: offline `.cas.h5` / `.dat.h5` inspection with `h5py`
- `extractor_python/`: offline legacy `.cas` and `.dat` inspection, plus HDF5 support where available
- `extractor_fluent/`: live Fluent/PyFluent export skeleton for on-site use

Recommended order:

1. use `extractor_python/` now on any HDF5 case/data files you already have;
2. review the candidate strings and tree layout;
3. use `extractor_fluent/` later on the Fluent machine to export the real active setup tree and reconcile gaps.

If you want to create a mesh from geometry locally with Python instead of only
loading an existing mesh, start here:

- `docs/guides/LOCAL_PYFLUENT_MESHING_STARTER.md`
- `scripts/local_watertight_meshing_starter.py`

If you want a repeatable trial harness that compares partially worked meshes or
cases under a cell-count cap, start here:

- `docs/findings/MESH_TRIAL_HARNESS.md`
- `scripts/run_mesh_trial_harness.py`
- `docs/troubleshooting/TROUBLESHOOTING.md`

For the Student-license local workflow, prefer `--processor-count 1` when
launch stability matters more than speed.

Docs layout:

- `docs/findings/`: observed runs, workflow findings, and reusable trial notes
- `docs/troubleshooting/`: failure patterns and quick fixes
- `docs/guides/`: operator guides, setup guides, and checklists

Practical first-choice artifact order from the local trial work is:

```text
.cas.h5
.msh
.meshdat (partial fallback only)
```
