---
name: pool-patch-volume
description: Create or verify a Fluent liquid-pool cell register, patch the requested liquid phase, and measure geometric and phase-integrated pool volume.
---

# Pool patch volume

Treat the pool as an initial condition, not a claim about the eventual steady
liquid level. Always distinguish:

```text
V_geom = geometric volume of selected cells
V_liq  = liquid phase-volume-fraction integral over those cells
```

## Workflow

1. Inspect the live mesh, phase/domain names, and existing registers.
2. Define or verify the register from the current mesh and requested
   cutoff/bounds; read back its type, bounds, and selected-cell scope.
3. Initialize only if patching requires initialized fields.
4. Patch only the requested liquid phase.
5. Measure `V_geom` and `V_liq` through a verified Fluent/report path.
6. Report fill fraction when useful and investigate a material discrepancy.

Do not alter unrelated boundaries, run iterations/timesteps, or save artifacts
unless the task requires it. Re-read current mesh bounds, phase mapping,
register names, and patch variables; do not import old case defaults.

Inspect known-working repository code before constructing an equivalent
PyFluent access pattern from memory. Reuse the access pattern, not case-specific
names, values, paths, or branch assumptions. If the current live Fluent tree
differs, inspect and adapt.

## Known working code

- `PyAnsys/scripts/setup/build_02d_vof_ic0_ic1_ic2_from_loaded_mesh.py`
- `PyAnsys/scripts/setup/prepare_02d_fine_patch_cases_and_queue.py`

Use these as access-pattern evidence only. If pressure over the pool is
requested, handle it as an additional analysis branch rather than expanding
the default workflow with pressure theory.
