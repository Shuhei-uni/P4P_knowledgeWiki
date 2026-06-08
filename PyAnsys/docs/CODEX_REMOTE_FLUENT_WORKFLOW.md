# Codex Remote Fluent Workflow Reference

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
scripts/local_preflight.py
scripts/check_connection.py
scripts/parse_server_info.py
scripts/inspect_fluent_session.py
scripts/inspect_case.py
scripts/probe_remote_paths.py
scripts/load_case_data.py
docs/PREPARE_NOW_ON_LAPTOP.md
docs/ON_SITE_FLUENT_PC_CHECKLIST.md
```

## Suggested sequence

1. Run local preflight:

```bash
.venv/bin/python scripts/local_preflight.py
```

2. Once Fluent PC is available, fill `.env`.
3. Run connection check:

```bash
.venv/bin/python scripts/check_connection.py
```

4. Inspect Fluent session:

```bash
.venv/bin/python scripts/inspect_fluent_session.py
```

5. Probe the Fluent-PC project folders:

```bash
.venv/bin/python scripts/probe_remote_paths.py
```

6. Build project-specific scripts only after connection works.

## First useful project-specific scripts

```text
scripts/inspect_case.py
scripts/load_case_data.py
scripts/list_boundaries.py
scripts/list_models.py
scripts/export_residuals.py
scripts/export_report_definitions.py
scripts/run_iterations.py
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
- Use timestamped output files.
- Keep `server_info.txt` and `.env` out of git.
- If connection fails, check IP, port, password, firewall, VPN, and whether server_info contains 127.0.0.1.
