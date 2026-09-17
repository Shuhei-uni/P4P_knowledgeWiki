---
name: direct-fluent-use
description: "Start and close the pinned local Ansys Fluent 2025 R2 Student Edition session from its dedicated runtime directory."
disable-model-invocation: true
---

# Direct Fluent Use

Use this skill only on `HOME-DESKTOP-SH` with Fluent 2025 R2 Student Edition.

## Start Fluent

Run this gate first:

```powershell
$fluentExe = 'C:\Program Files\ANSYS Inc\ANSYS Student\v252\fluent\ntbin\win64\fluent.exe'
$fluentWorkDir = 'C:\Users\Shuhei Yokkaichi\Documents\CFD\FluentDirectUse'
$repoRoot = 'C:\Users\Shuhei Yokkaichi\Documents\CFD\P4P_knowledgeWiki'
$machineOk = $env:OS -eq 'Windows_NT' -and [System.Environment]::MachineName -eq 'HOME-DESKTOP-SH'
$pathOk = (Test-Path -LiteralPath $fluentExe) -and (([System.IO.FileInfo]$fluentExe).FullName -eq $fluentExe)
$versionOk = $pathOk -and ((Get-Item -LiteralPath $fluentExe).VersionInfo.ProductVersion -eq '25.2.0')
$workDirOk = $fluentWorkDir -ne $repoRoot -and -not $fluentWorkDir.StartsWith($repoRoot + '\', [System.StringComparison]::OrdinalIgnoreCase)
if (-not ($machineOk -and $pathOk -and $versionOk -and $workDirOk)) {
    throw 'BLOCKED: this skill is restricted to HOME-DESKTOP-SH with Fluent 2025 R2 Student Edition.'
}
New-Item -ItemType Directory -Force -Path $fluentWorkDir | Out-Null
Set-Location -LiteralPath $fluentWorkDir
```

Start a persistent Python process from `$fluentWorkDir` and keep the returned `solver` object alive:

```python
import os
from pathlib import Path
import ansys.fluent.core as pyfluent

fluent_work_dir = Path(r"C:\Users\Shuhei Yokkaichi\Documents\CFD\FluentDirectUse")
fluent_work_dir.mkdir(parents=True, exist_ok=True)
os.chdir(fluent_work_dir)

solver = pyfluent.launch_fluent(
    product_version="25.2",
    fluent_path=r"C:\Program Files\ANSYS Inc\ANSYS Student\v252\fluent\ntbin\win64\fluent.exe",
    cwd=str(fluent_work_dir),
    mode="solver",
    dimension=3,
    precision="double",
    processor_count=1,
    ui_mode="no_gui",
    py=True,
    cleanup_on_exit=False,
    start_transcript=True,
)
```

## Close Fluent

You can close Fluent through the live controller, close and start a fresh session when you encounter an error.

```python
solver.exit()
```

If the controller is unavailable, stop only the uniquely identified pinned Fluent process tree:

```powershell
$root = @(Get-CimInstance Win32_Process | Where-Object {
    $_.Name -eq 'fluent.exe' -and
    $_.CommandLine -like '"C:\Program Files\ANSYS Inc\ANSYS Student\v252\fluent\ntbin\win64\fluent.exe"*'
})
if ($root.Count -ne 1) { throw 'BLOCKED: exact pinned Fluent root was not uniquely identified.' }
$all = @(Get-CimInstance Win32_Process)
$ids = [System.Collections.Generic.HashSet[int]]::new()
[void]$ids.Add([int]$root[0].ProcessId)
$changed = $true
while ($changed) {
    $changed = $false
    foreach ($p in $all) {
        if ($ids.Contains([int]$p.ParentProcessId) -and -not $ids.Contains([int]$p.ProcessId)) {
            [void]$ids.Add([int]$p.ProcessId)
            $changed = $true
        }
    }
}
foreach ($p in ($all | Where-Object { $ids.Contains([int]$_.ProcessId) } | Sort-Object { [int]$_.ProcessId } -Descending)) {
    Stop-Process -Id ([int]$p.ProcessId) -Force
}
Start-Sleep -Seconds 2
if (Get-CimInstance Win32_Process | Where-Object { $ids.Contains([int]$_.ProcessId) }) {
    throw 'FAILED: a pinned Fluent process remains.'
}
```
