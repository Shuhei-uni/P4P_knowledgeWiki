> **Legacy source:** ResearchProject_wiki/wiki/progress/experiments.md  
> **Migration note:** These excerpts preserve the historical run-note record; no status or interpretation has been rewritten. Raw and machine-generated artifacts remain at their legacy paths.

# Historical run notes

> **Legacy source:** ResearchProject_wiki/wiki/progress/experiments.md
> **Migration note:** Selected run entries are preserved verbatim as historical project memory; they are not a new status or findings system.

### Run 03A-08B-PARITY-FULL-GEOMETRY-ITER1000-2026-08-17
- Run ID: `03A-08B-PARITY-FULL-GEOMETRY-ITER1000-2026-08-17`
- Date: 2026-08-17
- Objective: execute the requested `1,000`-iteration native steady checkpoint from the verified 03A case-only artifact.
- Input and transport: `C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\03A-08b-parity-full-geometry-steady-preinit-20260817T103746Z.cas.h5`; all submission, remote-file checks, endpoint reload, and post-processing used Fluent gRPC on Student Fluent 2025 R2.
- Native sequence: Fluent read the case, Hybrid Initialized, ran one native `/solve/iterate 1000` command, wrote the paired `.cas.h5`/`.dat.h5` endpoint, exported residuals, and closed the transcript while leaving Fluent open. No liquid patch, DPM/EWF action, Python iteration loop, or client-side checkpoint was used.
- Endpoint: `C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\03A-08b-parity-full-geometry-steady-preinit-20260817T103746Z-iter1000-20260817T110345Z.cas.h5/.dat.h5`; both files, journal, transcript, and residual artifact were visible through gRPC and the endpoint was explicitly reloaded.
- Numerical result: final continuity `1.6043e-1`, `vf-phase-2 = 6.5142e-3`, velocity residuals approximately `1.5–1.7e-4`, `k = 5.2127e-3`, epsilon `2.2262e-1`; reverse flow remained on `334` pressure-outlet faces and viscosity limiting was observed. The full-domain phase-flux balance using both pressure outlets was `164.4105 kg/s` outlet magnitude versus `198.4863 kg/s` inlet, a `34.0758 kg/s` (`17.17%`) diagnostic residual.
- Outcome: `RUN_COMPLETED_ENDPOINT_VERIFIED; NOT_CONVERGED`. The endpoint is not an accepted 03A parent and must not seed 03B without further diagnosis. The generic post-processing fallback was corrected to include all discovered pressure outlets when a physical brine outlet is present.
- Artifacts: run manifest (historical machine artifact path: `../../../PyAnsys/output/03a_08b_parity_full_geometry_iter1000_20260817T110345Z.json`; not migrated), flux check (historical machine artifact path: `../../../PyAnsys/output/post_simulation_analysis/03a_08b_parity_full_geometry_iter1000_20260817T110345Z-flux-check.json`; not migrated), and residual check (historical machine artifact path: `../../../PyAnsys/output/post_simulation_analysis/03a_08b_parity_full_geometry_iter1000_20260817T110345Z-residual-check.json`; not migrated).

### Run 03A-08B-PARITY-FULL-GEOMETRY-CASE-ONLY-2026-08-17
- Run ID: `03A-08B-PARITY-FULL-GEOMETRY-CASE-ONLY-2026-08-17`
- Date: 2026-08-17
- Objective: reconstruct the requested full-geometry steady liquid-outlet carrier case from the audited 00a/Purnanto and 08b split-inlet lineage, then verify a case-only artifact on Student without advancing the solution.
- Geometry and mesh: `Full-geomV2-231kcells.msh.h5` on server `student`; Fluent read back `231,376` cells, `697,078` nodes, and `1,096,333` faces. Boundary topology was `liquidinlet`, `steaminlet`, `steamoutlet`, `brineoutlet`, and `wall`; measured inlet areas were `0.0048896664` and `0.51928634 m2`.
- Physics model: steady, pressure-based Mixture with primary `water-vapor-at-psep` and secondary `water-liquid-at-psep`, RNG k-epsilon, Differential Viscosity and Swirl Dominated Flow enabled, Energy/DPM/EWF off. The current setup's explicit pure-phase split Velocity Inlets were followed even though the later archived 08b saved-case report describes its inlet zones as Mass-Flow Inlets; that representation discrepancy is recorded rather than silently blended.
- Boundary and numerical conditions: inlet reference gauge pressure `1,140,000 Pa`, normal velocity `27.118 m/s`, liquid/steam phase fractions `1/0`, steam pressure outlet `1,120,000 Pa` with phase-2 backflow `0`, brine pressure outlet `1,120,000 Pa` with phase-2 backflow `1`, SIMPLE, Green-Gauss Node Based, PRESTO!, second-order momentum/k/epsilon, QUICK volume fraction, and the target under-relaxation factors.
- Verification: case `C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\03A-08b-parity-full-geometry-steady-preinit-20260817T103746Z.cas.h5` was written and reloaded by full path through the Fluent gRPC session. A gRPC `remote_file_exists` readback confirmed the case exists and the matching `.dat.h5` does not; the reloaded contract matched the requested build contract, and no initialization, iteration, patch, or solve occurred.
- Outcome: `CASE_ONLY_VERIFIED`; mesh quality readback recorded minimum orthogonal quality `0.200006` and maximum aspect ratio `82.6482`. Surface areas and cell counts are recorded in the build manifest.
- Limitations and next action: Student's operating-temperature and Mixture phase-interaction branches were inactive, so no value was guessed or claimed as applied. Outlet wetted perimeters/hydraulic diameters still require native preflight readback; the provisional Dh values only allowed case materialization. Keep the case at preflight until those gates and the interaction readback are resolved.
