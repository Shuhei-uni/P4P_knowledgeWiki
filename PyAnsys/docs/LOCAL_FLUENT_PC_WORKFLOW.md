# Local Fluent-PC Workflow

Run all Fluent automation on the Windows computer where Fluent is installed.
Python/PyFluent is the local client; it controls Fluent through its local gRPC
server. Network IP/port/password connections are not supported by this
repository.

## Connection choices

Use one of these local-only paths:

1. Start Fluent with `-sifile=<local path>` and set
   `FLUENT_SERVER_INFO_FILE` to that private local file.
2. Set `FLUENT_LOCAL_EXE` and let `src/pyansys_fluent/connection.py` launch a
   disposable Fluent process.
3. Prefer `scripts/orchestration/fluent_host_worker.py` for any run that needs
   checkpoints, restart recovery, or a durable receipt.

The server-info file contains credentials. Keep it in a private local runtime
directory; do not print, copy, commit, or paste it into chat.

## Standard sequence

In PowerShell on the Fluent PC:

```powershell
Set-Location "C:\path\to\P4P_knowledgeWiki\PyAnsys"
& ".\.venv\Scripts\python.exe" -c "import sys; import ansys.fluent.core as p; print(sys.executable); print(p.__version__)"
& ".\.venv\Scripts\python.exe" ".\scripts\connection\check_connection.py"
& ".\.venv\Scripts\python.exe" ".\scripts\inspection\inspect_fluent_session.py"
```

For a recoverable run, start `fluent_host_worker.py` in one terminal and use
`submit_fluent_job.py` from a second terminal. See `FLUENT_HOST_WORKER.md`.

## Case handling

- Treat an existing source case as immutable.
- Create a worker-owned disposable copy before loading or running it.
- Write setup derivatives and case/data checkpoints to a new scratch directory.
- Verify readbacks and output artifacts before treating a Fluent action as
  successful.
