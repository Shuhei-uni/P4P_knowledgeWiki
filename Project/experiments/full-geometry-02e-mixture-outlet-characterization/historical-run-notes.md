> **Retired source:** ResearchProject_wiki/wiki/progress/experiments.md
> **Migration note:** These excerpts preserve the historical run-note record; no status or interpretation has been rewritten. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# Historical run notes

> **Retired source:** ResearchProject_wiki/wiki/progress/experiments.md
> **Migration note:** Selected run entries are preserved verbatim as historical project memory; they are not a new status or findings system.

### Run 02e-STAGE2-Y010-2026-08-16
- Run ID: `02e-STAGE2-Y010-2026-08-16`
- Date: 2026-08-16
- Objective: Characterize the targeted Stage-2 Pressure Outlet and Outlet Vent brine-outlet controls selected from the Setup 02e Stage-1 evidence, using independent children and one native 500-iteration attempt per case.
- Geometry: Setup 02e spiral separator with the Y010 lower-region register and unchanged split velocity inlets, steam outlet, and brine-outlet geometry from the frozen initialized Y010 parent.
- Mesh: `Full-geomV2-231kcells.msh.h5`, `231,376` cells; Y010 register `33,315` cells.
- Physics model: steady pressure-based Mixture model; RNG k-epsilon; gravity `[0, -9.81, 0]`; energy off/preserved; DPM and EWF off; frozen Stage-1 model stack.
- Solver settings: unchanged Stage-1 numerics; Fluent-native journal owns the 500-iteration solve and endpoint write. Python created the case artifacts and submitted native journals; it did not loop solver iterations.
- Boundary and initial conditions: all four children loaded independently from `02e-Y010-parent-initialized-20260816T063000Z`; PO brine outlet `1.175` and `1.190 MPa` gauge; OV brine outlet `K=3` and `K=7`; steam outlet and both velocity-inlet conditions unchanged. Liquid density `881.77 kg/m³`.
- Iteration budget: four independent native attempts at `500` steady iterations.
- Convergence monitors: Y010/Y030 liquid mass; total-domain `∫ alpha_l dV`; phase-separated liquid and vapour inlet/brine-outlet/steam-outlet fluxes; native Fluent scaled residuals. Complete-run statistics use iterations `401–500`; failed cases retain last-valid evidence only.
- Outcome: `Partially Complete / Numerically Unresolved`. `02e-PO-S2-A` failed with FPE at `453`; `02e-PO-S2-B` failed with FPE at `415`; `02e-OV-S2-A` and `02e-OV-S2-B` completed `500` and wrote paired endpoints.
- Key result: complete OV final-100 liquid balances were `−545.702 kg/s` (`K=3`) and `−480.950 kg/s` (`K=7`). The corresponding Y010 final-100 means were `2.123514 m³` and `2.974293 m³`; total-domain liquid-volume final-100 means were `3.287270 m³` and `4.629215 m³`.
- Failure cause: the PO transcripts show reversed-flow and turbulent-viscosity-limiting warnings, many-orders-of-magnitude residual growth, AMG epsilon divergence, and terminal floating-point exceptions. Outlet flux reports were numerically corrupted at failure and are not used as physical endpoints.
- Evidence-use label: diagnostic directional evidence only. Reaching 500 for the OV cases is execution survivability, not convergence or physical validation; no automatic winner is selected.
- Evidence: [02e Stage-2 report](stage-02/results.md), Stage-2 build snapshot (historical machine artifact path: `../../../PyAnsys/output/02e_stage2_build_20260816.json`; not migrated), and recovered histories/transcripts (historical machine artifact path: `../../../PyAnsys/output/02e_stage2_recovered_20260816`; not migrated).
- Next action: require user interpretation of whether any further refinement should prioritize numerical survivability, reduced liquid drainage, retained total-domain inventory, or physically justified outlet calibration; retain the total-domain monitor for any follow-up.
