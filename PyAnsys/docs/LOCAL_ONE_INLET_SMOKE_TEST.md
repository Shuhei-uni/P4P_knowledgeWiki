# Local One-Inlet PyFluent Smoke Test

This note is the local reusable workflow for the current one-inlet Purnanto-style reconstruction script.

Use it with:

- `scripts/setup/reconstruct_purnanto_trial3.py`
- local Fluent installation
- local mesh export such as `trial4.msh`

## Current Proven Scope

The current short parity run already proves that the script can:

- launch local Fluent
- load a mesh-only `.msh`
- detect inlet/outlet/wall boundaries
- convert the inlet to `mass-flow-inlet`
- create manual water vapor and liquid water materials
- apply the one-inlet mass-flow package
- set `Operating Pressure = 0 Pa`
- apply the confirmed 2026 R1 numerics path
- hybrid initialize
- run a short `10`-iteration smoke test
- print mixture and phase mass-flow sanity checks
- write both `.cas.h5` and `.dat.h5`

It is not yet meant for long solves or final convergence claims.

## Extended Diagnostic Scope

The current script also supports a controlled longer diagnostic on the same one-steam-outlet branch:

- chunked reporting every `50` iterations
- optional checkpointing every `250` iterations
- interpreted phase-flow summaries
- final case/data output for a `500`-iteration diagnostic run

Important interpretation:

- this branch has one steam outlet only
- liquid is intentionally not expected to leave through that outlet
- do not treat nonzero total mixture imbalance as an automatic failure for this branch
- the key checks are:
  - vapor outlet flow staying close to vapor inlet flow
  - liquid outlet flow through the steam outlet staying near zero
  - vapor recovery ratio close to `1`
  - liquid carryover ratio close to `0`

## Current Command

From the repository root:

```powershell
.\PyAnsys\.venv\Scripts\python.exe .\PyAnsys\scripts\reconstruct_purnanto_trial3.py --iterations 10
```

Controlled `500`-iteration diagnostic:

```powershell
.\PyAnsys\.venv\Scripts\python.exe .\PyAnsys\scripts\reconstruct_purnanto_trial3.py `
  --iterations 500 `
  --report-interval 50 `
  --checkpoint-interval 250 `
  --processor-count 2 `
  --output-case "C:\Users\Shuhei Yokkaichi\Documents\CFD\Trial extended outlet pipe\Major Files\trial4-purnanto-recon-500.cas.h5" `
  --output-data "C:\Users\Shuhei Yokkaichi\Documents\CFD\Trial extended outlet pipe\Major Files\trial4-purnanto-recon-500.dat.h5"
```

## Current Mesh And Outputs

Default current hardened path:

- mesh: `C:\Users\Shuhei Yokkaichi\Documents\CFD\Trial extended outlet pipe\Major Files\trial4.msh`
- case: `C:\Users\Shuhei Yokkaichi\Documents\CFD\Trial extended outlet pipe\Major Files\trial4-purnanto-recon.cas.h5`
- data: `C:\Users\Shuhei Yokkaichi\Documents\CFD\Trial extended outlet pipe\Major Files\trial4-purnanto-recon.dat.h5`

Current controlled diagnostic outputs:

- case: `C:\Users\Shuhei Yokkaichi\Documents\CFD\Trial extended outlet pipe\Major Files\trial4-purnanto-recon-500.cas.h5`
- data: `C:\Users\Shuhei Yokkaichi\Documents\CFD\Trial extended outlet pipe\Major Files\trial4-purnanto-recon-500.dat.h5`
- log: `C:\Users\Shuhei Yokkaichi\Documents\CFD\Trial extended outlet pipe\Major Files\trial4-purnanto-recon-500-log.txt`
- checkpoint case: `C:\Users\Shuhei Yokkaichi\Documents\CFD\Trial extended outlet pipe\Major Files\trial4-purnanto-recon-500.cas-iter250.h5.cas.h5`
- checkpoint data: `C:\Users\Shuhei Yokkaichi\Documents\CFD\Trial extended outlet pipe\Major Files\trial4-purnanto-recon-500.dat-iter250.h5.dat.h5`
- residual plot: `C:\Users\Shuhei Yokkaichi\Documents\CFD\Trial extended outlet pipe\Major Files\trial4-purnanto-recon-500-residuals.png`

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

## What To Check After The Run

Look for:

- `Operating Conditions` showing `operating_pressure: 0`
- `Solution Methods` showing the confirmed 2026 R1 paths and after-state
- `Flux Sanity Checks` for:
  - `mixture`
  - `phase-1`
  - `phase-2`
- interpreted chunk summaries with:
  - vapor recovery ratio
  - liquid carryover ratio
- successful `write_case`
- successful `write_data`

For the current `500`-iteration diagnostic, the final interpreted values were approximately:

- vapor recovery ratio: `1.009186`
- liquid carryover ratio: `3.968579e-25`
- phase-2 outlet flow: effectively zero through the steam outlet

## If The Run Fails Early

Check these first:

1. Fluent and Workbench are fully closed before launch
2. the mesh path exists
3. the venv interpreter is the one under `PyAnsys\.venv`
4. the script is still using the hardened `trial4` defaults unless you intentionally changed them

## Related Project Note

For the project-facing history and interpretation of the local smoke-test passes, see:

- `..\..\ResearchProject_wiki\wiki\technical\pyfluent-trial3-one-inlet-reconstruction-smoke-test.md`
