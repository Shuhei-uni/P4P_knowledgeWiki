# Local PyFluent Meshing Starter

This note is the local reusable starting point for generating a mesh from CAD or
geometry with Python.

Use this path when:

- Fluent is installed locally on the machine that runs the script
- you want Fluent Meshing to create the mesh from geometry
- your geometry is reasonably clean or close to watertight

Use the existing mesh-loading scripts when:

- you already have a `.msh`, `.msh.h5`, or `.cas.h5`
- you only want solver setup and run automation

Do not confuse the two PyAnsys meshing routes:

- `PyFluent` meshing mode:
  - launches Fluent in meshing mode
  - runs Watertight Geometry or Fault-Tolerant Meshing workflows
  - best first choice for your current Fluent-centered workflow
- `PyPrimeMesh`:
  - uses `ansys-meshing-prime`
  - talks to Prime Server
  - not installed in the current local `.venv`
  - keep this as a later-stage option

## Current Starter Script

From the repository root:

```powershell
.\PyAnsys\.venv\Scripts\python.exe .\PyAnsys\scripts\local_watertight_meshing_starter.py `
  --geometry-file "C:\path\to\your\geometry.step" `
  --length-unit mm `
  --surface-max-size 80 `
  --volume-fill poly `
  --write-case "C:\path\to\meshed-case.cas.h5"
```

If the geometry is cleaner and you want a hexcore-style interior:

```powershell
.\PyAnsys\.venv\Scripts\python.exe .\PyAnsys\scripts\local_watertight_meshing_starter.py `
  --geometry-file "C:\path\to\your\geometry.step" `
  --length-unit mm `
  --surface-max-size 80 `
  --volume-fill poly-hexcore `
  --hex-max-cell-length 120 `
  --write-case "C:\path\to\meshed-case.cas.h5"
```

## What the starter does

The script:

1. launches Fluent in `MESHING` mode
2. imports the geometry
3. creates a coarse global surface mesh
4. marks the setup as a fluid region
5. updates regions
6. creates a volume mesh
7. switches to solver mode
8. optionally writes a mesh or case file

This is intentionally a first-pass automation path, not a final production
meshing recipe.

## Recommended way to chase sub-1M cells

For your separator geometry, first treat meshing as a repeatable coarse-to-fine
study rather than a single perfect run.

Suggested first sweep:

- `surface-max-size = 120`
- `volume-fill = poly`
- no boundary layers

Then compare against:

- `surface-max-size = 80`
- `surface-max-size = 60`

Only add boundary layers after the basic core mesh is stable. Boundary layers are
often where cell count and orthogonal quality both get worse at the same time.

## When to stop using this starter

Switch away from this watertight starter when:

- import fails because the CAD is not clean enough
- you have leaks, overlaps, or disconnected surfaces
- boundary extraction is unreliable
- the geometry needs capping or cleanup before region creation

That is the point where `Fault-Tolerant Meshing` is the better PyFluent path.

## Practical expectation

Python automation will help you:

- repeat the same meshing settings reliably
- run size sweeps faster
- keep a record of what changed between meshes

It will not automatically make a difficult geometry produce a good mesh. If the
problem is local geometric detail, narrow gaps, tiny sliver faces, sharp
transitions, or over-aggressive boundary layers, those issues still have to be
handled in the geometry or in the meshing controls.
