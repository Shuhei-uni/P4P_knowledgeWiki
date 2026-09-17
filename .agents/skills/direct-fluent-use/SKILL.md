---
name: direct-fluent-use
description: "Directly launch and control Ansys Fluent 2025 R2 Student Edition through terminal/PyFluent on the designated Windows workstation."
disable-model-invocation: true
---

# Direct Fluent Use

This is a deliberately machine-bound, user-invoked skill for direct Fluent
control. It is valid only on the designated Windows workstation and only for
the installed Ansys Fluent Student Edition 2025 R2 executable.

## Hard scope gate

Run the following checks before launching, connecting to, or mutating Fluent:

```powershell
$fluentExe = 'C:\Program Files\ANSYS Inc\ANSYS Student\v252\fluent\ntbin\win64\fluent.exe'
$fluentWorkDir = 'C:\Users\Shuhei Yokkaichi\Documents\CFD\FluentDirectUse'
$repoRoot = 'C:\Users\Shuhei Yokkaichi\Documents\CFD\P4P_knowledgeWiki'
$machineOk = $env:OS -eq 'Windows_NT' -and [System.Environment]::MachineName -eq 'HOME-DESKTOP-SH'
$pathOk = (Test-Path -LiteralPath $fluentExe) -and (([System.IO.FileInfo]$fluentExe).FullName -eq $fluentExe)
$versionOk = $pathOk -and ((Get-Item -LiteralPath $fluentExe).VersionInfo.ProductVersion -eq '25.2.0')
$workDirOk = $fluentWorkDir -ne $repoRoot -and -not $fluentWorkDir.StartsWith($repoRoot + '\', [System.StringComparison]::OrdinalIgnoreCase)
if (-not ($machineOk -and $pathOk -and $versionOk -and $workDirOk)) {
    throw 'BLOCKED: direct-fluent-use is restricted to HOME-DESKTOP-SH with Fluent 2025 R2 Student Edition at the pinned path.'
}
New-Item -ItemType Directory -Force -Path $fluentWorkDir | Out-Null
Set-Location -LiteralPath $fluentWorkDir
```

If any check fails, stop and report `BLOCKED`. Do not use this skill through
WSL, Linux, a remote host, another Windows computer, a different Fluent
installation, or GUI/computer-use automation.

## Dedicated working directory

`C:\Users\Shuhei Yokkaichi\Documents\CFD\FluentDirectUse` is the dedicated
Fluent runtime directory. Launch Fluent and its persistent Python driver with
that directory as the current working directory. Keep transcripts, server-info
handoffs, journals, scratch scripts, and generated case/data outputs there or
below it. A repository helper may be invoked by absolute path, but the Fluent
process must inherit the dedicated directory as its working directory.

## Terminal and gRPC workflow

Use the locally installed Python environment that can import
`ansys.fluent.core`. From the dedicated working directory, launch Fluent from
a persistent Python driver and keep the authenticated `solver` object alive for
the whole interaction:

```python
import os
from pathlib import Path
import ansys.fluent.core as pyfluent

fluent_work_dir = Path(r"C:\Users\Shuhei Yokkaichi\Documents\CFD\FluentDirectUse")
fluent_work_dir.mkdir(parents=True, exist_ok=True)
os.chdir(fluent_work_dir)

solver = pyfluent.launch_fluent(
    mode="solver",
    dimension=3,
    precision="double",
    processor_count=4,
    ui_mode="no_gui",
    cleanup_on_exit=False,
    start_transcript=True,
)
```

The driver must remain alive while follow-up commands are sent. Preserve the
server-info/credential handoff created by the launch and use the authenticated
gRPC connection rather than trying to infer an endpoint from internal Fluent
ports. The PyFluent launcher may remove temporary server-info files when its
controller exits, making later attachment unreliable.

After connecting or launching, inspect the live session before acting. When the
preserved server-info handoff is configured for P4P, use MCP `session_status`,
`solver_status`, and targeted state for generic status and unfamiliar-tree
inspection; keep the authenticated driver for the explicitly approved direct
operation. Record the reported Fluent version and the actually loaded case/data
identity when available; never infer case identity from a server id, process id,
or an old session.

## Common direct operations

For a paired case/data artifact, replace the case in the current authenticated
session with:

```python
solver.settings.file.read_case_data(file_name=r"C:\path\case.cas.h5")
```

For separate files, use the dependency-ordered sequence:

```python
solver.settings.file.read_case(file_name=r"C:\path\case.cas.h5")
solver.settings.file.read_data(file_name=r"C:\path\case.dat.h5")
```

Verify that the read completed by inspecting the live session and, when the
operation is consequential, save/reopen or perform an equivalent readback
check before reporting success. Inspect the live Settings tree before changing
an unfamiliar setting; escalate version or activation uncertainty to the
Fluent-specific inspection/manual workflow instead of guessing an API path.

## Lifecycle and failure handling

Keep a launched Fluent session running across normal follow-up operations,
including case replacement and simple setting changes. On a solver error, use
MCP status when the preserved handoff is configured, then reconcile the direct
operation's receipt/readback before deciding whether recovery is possible.

End a Fluent session only after the user explicitly requests it. When ending
one, identify the exact pinned Fluent process tree first, stop only that tree,
and verify that its Fluent, Cortex, solver, MPI, and licensing helper
processes have exited. Never use a broad name-only kill that could affect an
unrelated Fluent installation or session.

## Completion contract

Report the scope-gate results, the exact Fluent process/session acted on, the
operation performed, and an observable readback or process-state result. If a
gate, connection, read, or verification fails, report `BLOCKED` or `FAILED`
with the evidence and leave unrelated processes and files unchanged.
