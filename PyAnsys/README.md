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
