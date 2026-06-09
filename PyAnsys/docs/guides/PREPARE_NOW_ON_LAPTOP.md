# Prepare Everything Now on Your Laptop

You are not with the Fluent PC yet, so do these steps now.

## 1. Create a project folder

```bash
mkdir fluent_remote_agent
cd fluent_remote_agent
```

Copy this kit into that folder.

## 2. Preferred setup: run the bootstrap script

From inside `PyAnsys/`:

```bash
python3 scripts/bootstrap_local_env.py
```

This does all of the following:

```text
- creates PyAnsys/.venv
- prefers Python 3.12
- installs requirements-minimal.txt
- creates .env from .env.example if needed
- runs scripts/local_preflight.py
```

Why this matters:

```text
- this laptop currently has Python 3.14 available by default
- PyAnsys/PyFluent support is typically smoother on Python 3.12
- the bootstrap script avoids you accidentally building the wrong environment
```

## 3. Manual fallback: create a virtual environment yourself

macOS/Linux:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
```

If you do not have Python 3.12 installed locally, another fallback is:

```bash
uv venv .venv --python 3.12 --seed
source .venv/bin/activate
```

## 4. Install the focused PyAnsys stack

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements-minimal.txt
```

This installs:

```text
ansys-fluent-core
ansys-fluent-visualization
pyvista
matplotlib
pandas
numpy
python-dotenv
PyYAML
```

Install the extended meshing/DPF stack only later if needed:

```bash
python -m pip install -r requirements-extended.txt
```

## 5. Run local preflight

```bash
python scripts/local_preflight.py
```

Expected:

```text
[OK] PyFluent / ansys-fluent-core
[OK] PyFluent-Visualization
[OK] PyVista
...
```

Optional packages may show missing. That is okay unless you specifically installed the extended stack.

## 6. Create `.env`

```bash
cp .env.example .env
```

Leave it mostly blank for now. When you are with the Fluent PC, you will fill in either:

```text
FLUENT_SERVER_INFO_FILE=./server_info.txt
```

or:

```text
FLUENT_IP=...
FLUENT_PORT=...
FLUENT_PASSWORD=...
```

## 7. Prepare Codex

Add this file to your project:

```text
docs/guides/CODEX_REMOTE_FLUENT_WORKFLOW.md
```

Then when you are ready, tell Codex:

```text
Read docs/guides/CODEX_REMOTE_FLUENT_WORKFLOW.md and docs/guides/ON_SITE_FLUENT_PC_CHECKLIST.md. We are preparing to connect this laptop to a remote Ansys Fluent session using PyFluent gRPC. Do not use launch_fluent. Use connect_to_fluent. First run scripts/local_preflight.py and inspect the connection scripts.
```

## 8. What you cannot test yet

Until you are with the Fluent PC, you cannot fully test:

```text
- Fluent gRPC server startup
- IP/port/password connection
- firewall access
- case loading
- boundary/model inspection
- running solver commands
```

That is normal. Your goal now is just to make the laptop ready.
