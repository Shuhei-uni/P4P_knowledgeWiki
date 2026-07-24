# Codex Remote Fluent Workflow Reference

For the current self-healing architecture and complete operating procedure,
read these first:

- [`LAPTOP_CONTROLLED_FLUENT.md`](./LAPTOP_CONTROLLED_FLUENT.md)
- [`SETUP_TO_RESULTS_WORKFLOW.md`](./SETUP_TO_RESULTS_WORKFLOW.md)

The laptop remains the controller. The Fluent computer supplies a watchdog and
an optional narrow run worker; it does not compile setup Markdown or select
scientific recovery state.

This project uses the PyAnsys ecosystem focused on:

```text
- PyFluent / ansys-fluent-core for Fluent CFD control
- PyFluent-Visualization / PyVista / Matplotlib for post-processing
- PyPrimeMesh only later if meshing automation is needed and available
```

The target architecture is:

```text
Codex + Python on laptop
        connects via gRPC
Ansys Fluent running on licensed workstation
```

## Use connect_to_fluent, not launch_fluent

The laptop may not have Fluent installed. Fluent runs remotely.

Use:

```python
import ansys.fluent.core as pyfluent

solver = pyfluent.connect_to_fluent(
    ip=ip,
    port=port,
    password=password,
    allow_remote_host=True,
    cleanup_on_exit=False,
    start_transcript=True,
)
```

or:

```python
solver = pyfluent.connect_to_fluent(
    server_info_file_name="server_info.txt",
    allow_remote_host=True,
    cleanup_on_exit=False,
    start_transcript=True,
)
```

## Current setup files

```text
requirements-minimal.txt
requirements-extended.txt
.env.example
scripts/connection/local_preflight.py
scripts/connection/check_connection.py
scripts/connection/parse_server_info.py
scripts/inspection/inspect_fluent_session.py
scripts/inspection/inspect_case.py
scripts/inspection/probe_remote_paths.py
scripts/inspection/load_case_data.py
docs/PREPARE_NOW_ON_LAPTOP.md
docs/ON_SITE_FLUENT_PC_CHECKLIST.md
```

## Suggested sequence

1. Run local preflight:

```bash
.venv/bin/python scripts/connection/local_preflight.py
```

2. Once Fluent PC is available, fill `.env`.
3. Run connection check:

```bash
.venv/bin/python scripts/connection/check_connection.py
```

4. Inspect Fluent session:

```bash
.venv/bin/python scripts/inspection/inspect_fluent_session.py
```

5. Probe the Fluent-PC project folders:

```bash
.venv/bin/python scripts/inspection/probe_remote_paths.py
```

6. Build project-specific scripts only after connection works.

## First useful project-specific scripts

```text
scripts/inspection/inspect_case.py
scripts/inspection/load_case_data.py
scripts/list_boundaries.py
scripts/list_models.py
scripts/inspection/export_residuals.py
scripts/export_report_definitions.py
scripts/setup/save_data_after_iterations.py
```

## Notes

- Keep the laptop-side Python pinned to the local `PyAnsys/.venv`, preferably on Python 3.12.
- File paths in Fluent commands are usually interpreted on the Fluent PC, not on the laptop.
- Store Fluent-PC paths in `.env` using `FLUENT_REMOTE_PROJECT_DIR`,
  `FLUENT_REMOTE_CASE_DATA_DIR`, `FLUENT_REMOTE_GEOM_DIR`, and
  `FLUENT_REMOTE_MESH_DIR`.
- Store concrete active assets in `.env` using `FLUENT_REMOTE_CASE_FILE`,
  `FLUENT_REMOTE_DATA_FILE`, `FLUENT_REMOTE_GEOM_FILE`, and
  `FLUENT_REMOTE_MESH_FILE`.
- Default setup deliverable: `.cas.h5` only.
- Default run/save deliverable: derived `name_X.dat.h5` from `scripts/setup/save_data_after_iterations.py`.
- Keep initialization, iteration, and data writing out of complex setup-building scripts unless the user explicitly requests a combined flow.
- Keep `server_info.txt` and `.env` out of git.
- If connection fails, check IP, port, password, firewall, VPN, and whether server_info contains 127.0.0.1.
