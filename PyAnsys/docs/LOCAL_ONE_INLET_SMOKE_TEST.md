# Local One-Inlet PyFluent Smoke Test

This note is the local reusable workflow for the case-only one-inlet Purnanto-style
reconstruction script. The script prepares the setup and writes a `.cas.h5`; Fluent owns
initialization, iteration, autosave, and the final case/data save.

Use it with:

- `scripts/setup/reconstruct_purnanto_trial3.py`
- local Fluent installation
- local mesh export such as `trial4.msh`

## Current Proven Scope

The builder can:

- launch local Fluent
- load a mesh-only `.msh`
- detect inlet/outlet/wall boundaries
- convert the inlet to `mass-flow-inlet`
- create manual water vapor and liquid water materials
- apply the one-inlet mass-flow package
- set `Operating Pressure = 0 Pa`
- apply the confirmed 2026 R1 numerics path
- write a case-only `.cas.h5` setup artifact

The script does not initialize, iterate, poll, or write client-side checkpoints. It is not a
long-run driver.

## Current Command

From the repository root:

```powershell
.\PyAnsys\.venv\Scripts\python.exe .\PyAnsys\scripts\reconstruct_purnanto_trial3.py `
  --processor-count 2 `
  --output-case "C:\Users\Shuhei Yokkaichi\Documents\CFD\Trial extended outlet pipe\Major Files\trial4-purnanto-recon.cas.h5"
```

## Current Mesh And Outputs

Default current hardened path:

- mesh: `C:\Users\Shuhei Yokkaichi\Documents\CFD\Trial extended outlet pipe\Major Files\trial4.msh`
- case: `C:\Users\Shuhei Yokkaichi\Documents\CFD\Trial extended outlet pipe\Major Files\trial4-purnanto-recon.cas.h5`

Configure the native autosave root and retained case/data pair in Fluent's Calculation
Activities before starting the run. Keep at least two recent checkpoints so one complete pair
remains available while Fluent replaces the other.

## Confirmed 2026 R1 Settings Paths

### Operating conditions

Use:

```python
op = solver.settings.setup.general.operating_conditions
op.operating_pressure = 0
op.gravity.enable = True
op.gravity.components = [0.0, -9.81, 0.0]
```

Important:

- do not pass `operating_pressure` as the earlier dictionary-style value form for this local 2026 R1 path

### Solution methods

Probe and then set:

```python
methods = solver.settings.solution.methods
methods.p_v_coupling.flow_scheme = "SIMPLE"
methods.spatial_discretization.gradient_scheme = "green-gauss-node-based"
methods.spatial_discretization.discretization_scheme.set_state(
    {
        "pressure": "presto!",
        "mom": "second-order-upwind",
        "mp": "quick",
        "k": "second-order-upwind",
        "epsilon": "second-order-upwind",
    }
)
```

## Current Known Caveat

Pressure-outlet momentum/turbulence subsettings may still report as inactive at assignment time. The short parity run still succeeds, so treat this as a cleanup target rather than a current blocker.

Also note:

- the direct Fluent residual write command produced an empty file on this run
- the rough residual plot was recovered from the Fluent transcript instead

## What To Check During And After The Run

From a fresh client connection, inspect the Fluent-native calculation status and current
iteration/residual monitors. Do not issue iteration or checkpoint commands from the monitoring
client. Confirm that:

- Fluent remains healthy and the calculation is either active or idle as expected;
- the newest autosave has a matching case/data pair;
- the saved iteration is at or below the live iteration count;
- the case/data pair can be reloaded only after Fluent is idle;
- final flux and DPM-fate reports are collected after the run, as offline/post-run analysis.

## If The Run Fails Early

Check these first:

1. Fluent and Workbench are fully closed before launch
2. the mesh path exists
3. the venv interpreter is the one under `PyAnsys\.venv`
4. the script is still using the hardened `trial4` defaults unless you intentionally changed them

## Related Project Note

For the project-facing history and interpretation of the local smoke-test passes, see:

- `..\..\ResearchProject_wiki\wiki\technical\pyfluent-trial3-one-inlet-reconstruction-smoke-test.md`
