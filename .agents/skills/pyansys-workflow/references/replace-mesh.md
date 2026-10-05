# Replace Mesh

Use this branch when asked to run the same existing Fluent setup on a supplied
mesh, transfer a baseline to another mesh, or use Fluent's Replace Mesh feature.
The parent case owns the settings; the active experiment owns the permitted
changes and whether to continue saved data or start fresh. Use Fluent's native
transfer rather than reconstructing the parent models in Python.

For session authority and checkpoint destinations, follow
[fleet and artifacts](fleet-and-artifacts.md). For uncertain commands in another
release, follow [manual fallback](manual-fallback.md).

## Establish the transfer contract

Record these before loading the target mesh:

| Input | Required evidence |
| --- | --- |
| Source | Exact case and, for continuation, matching data pair; paths and hashes |
| Target | Supplied mesh identity and hash; native cell count, mesh check, physical extents |
| Intent | Continued fields or a recorded fresh-start initialization; allowed geometry/mesh changes |
| Invariants | Models, materials, boundary values, source hooks, numerical controls, injection definitions, reports, iteration/time state |
| Zone map | Target name/type/physical role to source name/type/role; evidence from geometry and adjacency |
| Session | Owned endpoint; valuable current endpoint preserved as a paired local save before replacement |

Keep raw inputs unchanged. Use local Fluent disk for conversion, ordinary
checkpoints, transcripts, and reports; use shared storage for selected input and
final pairs. Resolve paths on the Fluent computer, not on the client computer.

## Prepare the target, then reload the source

1. Inspect the target in an owned, preserved session. Reading it replaces the
   active mesh/case state. Verify native physical extents; file coordinate units
   alone are insufficient grounds to scale it again.
2. Establish the zone map. Rename equivalent zones for native matching. Create
   required source subzones only when the experiment requires them, using its
   verified selection rule. Prove generated faces by adjacency/topology rather
   than assuming that numeric suffixes identify a wall or an interface.
3. Make a local replacement input supported by the live Fluent release. The
   2025 R2 manual requires legacy `.msh` or `.cas`, excludes CFF inputs, and
   requires removing non-conformal interfaces from a replacement `.cas`.
   A replacement case supplies mesh information only. See the
   [2025 R2 mesh manual, section 7.12.12](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_GridModify.html).
4. Reload the exact source case and matching data. Resolve verified UDF
   libraries and other dependencies on this host, and prove hooks/settings and
   starting fields before replacing the mesh. Export DPM injections as a native
   backup when present. Capture setup, report, field, and injection inventories.

For the verified 2025 R2 API, a mesh-bearing legacy case can be written after
target preparation as follows. Use a new absolute server-local destination;
inspect these paths for another release and restore the previous file mode:

```python
previous_cff = solver.settings.file.cff_files.get_state()
try:
    solver.settings.file.cff_files = False
    solver.settings.file.write_case(file_name=target_legacy_case)
finally:
    solver.settings.file.cff_files = previous_cff
```

## Perform native replacement

Fluent maps conditions by matching names; unmatched boundaries receive defaults.
Loaded data is interpolated automatically. Across-zone interpolation does not
enforce global conservation; parallel Fluent may enable it implicitly. The
2025 R2 manual provides partition-per-zone to avoid that fallback. Select the
mapping policy from the verified zone correspondence and record it.
[Source: mesh manual, section 7.12.12](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_GridModify.html).

The same-zone route used successfully on Fluent 2025 R2 was:

```python
# Inspect argument_names/help on the live command before using this example.
solver.scheme.eval("(rpsetvar 'dynamesh/replace-mesh/partition-per-zone? #t)")
solver.settings.mesh.replace(file_name=target_legacy_case, zones=False)
```

Reacquire Settings objects after replacement. Record the native transcript,
mesh identity, resulting zone list, and the actual interpolation policy. An
accepted command alone is not transfer proof.

## Audit and repair only the declared differences

| Item | Readback and repair |
| --- | --- |
| Setup | Compare parent and child models, materials, expressions, methods, controls, and UDF hooks; allow only recorded differences |
| Zones | Verify names, types, adjacency, phase conditions, film walls, roughness, sources, and interfaces; for a new equivalent wall, copy the complete verified reference boundary state and record the mapping |
| DPM | Check object-name counts as well as state dictionaries, then compare surfaces, materials, flow, diameters, interactions, laws, and hooks |
| Reports | Remap obsolete surfaces to verified physical equivalents; retain report definitions and frequency; redirect files and inherited autosaves before solving |
| Fields | Check finite values, inventories and expected spatial distribution; record source-to-mapped changes, film state, iteration coordinate and time/film clock |

For missing DPM definitions, use native injection export/import only after the
audit establishes the need. Imported name collisions are renamed; materials
and laws need a check. See the
[2025 R2 injection manual, section 25.3.17.7](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_discrete_initial.html).
The verified native API pattern is:

```python
# Export while the verified source is loaded; import only if repair is needed.
names = solver.settings.setup.models.discrete_phase.injections.get_object_names()
solver.tui.file.write_injections(injection_backup_path, *names, "()")
solver.settings.file.read_injections(file_name=injection_backup_path)
```

In the slit154k transfer, import created several objects with the same collision
name. A state dictionary hid this multiplicity, and one delete call removed
only one copy. Use before/after object inventories to identify imported copies,
bound cleanup by the known import count, and verify the final definitions.
Never remove objects solely because their names start with `imported-`.

The repository's
[settings-transfer helper](../../../../PyAnsys/src/pyansys_fluent/settings_transfer.py)
implements a settings-file route; it does not provide Replace Mesh field
interpolation. In the slit154k attempt, reading settings after transfer left an
empty bulk field and did not repair injections. Recover an unrun child from the
verified parent pair and repeat native replacement when needed. Preserve any
solved child before recovery. Never reinitialize a continuation to conceal lost
fields.

## Prove a usable child

1. Save a new paired case/data endpoint locally. Reopen it and repeat the setup,
   zone, DPM, report, field and coordinate audits.
2. Compare mapped inventories separately from reopen stability. Interpolation
   can change inventory; settings equality does not prove field equality.
3. If first reopen changes face-flux diagnostics, prove that inventories,
   sources and settings remain stable and record the exact changes. A second
   paired save/reopen must reproduce the required readback. Do not waive broad
   field differences as cache refreshes.
4. Run the smallest useful smoke test required by the experiment. Verify native
   progress and complete report histories. Count smoke updates within the
   requested horizon when its protocol requires that.

Return source/target identities, Fluent version and native command receipt,
zone map and allowed differences, before/after/reopen audit, inventory changes,
paired artifact paths, and smoke/instrumentation evidence. Continue the requested
run only after the child passes these checks. This branch does not choose new
physics, startup schedules, run lengths, or scientific acceptance thresholds.

## Verified implementation and evidence

Use these to inspect API patterns and observed recovery behaviour. Derive zone
names, geometry selections, source hooks, and numerical values from the current
case contract rather than copying this campaign's values.

- [Slit154k native runner](../../../../PyAnsys/scripts/setup/run_phase72a_stage3_slit154k.py)
- [Transfer contract](../../../../Project/experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/slit154k/setup.md)
- [Machine transfer and smoke receipt](../../../../PyAnsys/output/phase72a-stage3-slit154k-server3/20261005/run-manifest.json)
- [Prepared pair reopen readback](../../../../PyAnsys/output/phase72a-stage3-slit154k-server3/20261005/prepared-reopen.json)
