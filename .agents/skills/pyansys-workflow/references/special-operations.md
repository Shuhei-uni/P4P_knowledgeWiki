# Special operations

Use this file for narrow Fluent operations that do not deserve their own skill.

## Pool patch / liquid inventory initialization

Treat a pool as an initial-condition cell selection, not a claim about the final
liquid level.

- inspect the live mesh/zone and coordinate convention;
- create or reuse an explicit cell register for the requested bounds;
- verify the selected cells/volume before patching;
- initialize only when the case requires it;
- patch only the requested liquid phase/state;
- report selected geometric/phase volume and the exact register/bounds.

If the selection intersects unintended zones or the requested geometry is
ambiguous, derive a safer zone-restricted/register definition from the case
rather than patching blindly.

### Method

First inspect mesh extents, fluid-cell zones, phase domains, existing cell
registers, and phase mapping. A height-defined pool normally uses current mesh
extents in the unconstrained directions and a verified vertical cutoff. Check
that the resulting hexahedron intersects the intended fluid region rather than
a solid, pipe, or outlet-only volume.

Create or reuse one named cell register and read it back explicitly. A typical
Settings state is equivalent to:

```python
{
    "type": "option hexahedron",
    "min_point": [xmin, ymin, zmin],
    "max_point": [xmax, y_cut, zmax],
    "inside": True,
}
```

Reacquire `solution.cell_registers` after creation. Obtain marked-cell count
from Fluent or a validated cell query; box dimensions alone do not prove which
cells were selected.

If initialization is necessary, use the minimum required initialization method
and record it. Patch only the inspected liquid phase/domain and requested
variable. `mp` is often the phase-volume-fraction patch variable, but phase
names and mappings must be inspected in the live case. A successful patch call
is not enough: calculate/register a post-patch phase-volume-fraction reduction.

Measure geometric selected-cell volume and liquid phase volume separately. When
the release supports register locations, use a register-scoped cell-volume
integral for `V_geom` and a liquid-VOF integral for `V_liq`; inspect the actual
field name because it may be exposed as `phase-2-vof`. Where complementary
phase volume is available, check `V_liq + V_vapour ≈ V_geom`, report the fill
fraction, and retain any mismatch for investigation. Never relabel geometric
volume as liquid inventory without that phase readback.

For optional pressure diagnostics, state the field's gauge/absolute meaning,
reference, density, gravity direction, and case state. A freshly initialized
pool supports only an initialization diagnostic or rough hydrostatic estimate,
not an operational pressure conclusion. Existing repository examples live in
`PyAnsys/scripts/setup/build_02d_vof_ic0_ic1_ic2_from_loaded_mesh.py` and
`PyAnsys/scripts/setup/prepare_02d_fine_patch_cases_and_queue.py`.

### Receipt

Return register bounds and selected-cell count, liquid phase/domain and patched
variable, `V_geom`, `V_liq`, fill fraction, initialization state, and whether
iterations/timesteps or boundary changes occurred. Keep outlet priming and pool
initialization as separate operations.

Other one-off operations belong here when they are implementation details of an
active experiment and do not need independent invocation.
