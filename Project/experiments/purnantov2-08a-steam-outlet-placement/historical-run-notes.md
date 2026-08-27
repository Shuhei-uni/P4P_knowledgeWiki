> **Retired source:** ResearchProject_wiki/wiki/progress/experiments.md
> **Migration note:** These excerpts preserve the historical run-note record; no status or interpretation has been rewritten. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# Historical run notes

> **Retired source:** ResearchProject_wiki/wiki/progress/experiments.md
> **Migration note:** Selected run entries are preserved verbatim as historical project memory; they are not a new status or findings system.

### Run PLS-STUDENT-OUTLET-EXT-2026-06-08
- Run ID: `PLS-STUDENT-OUTLET-EXT-2026-06-08` (`Assumed` setup label until the Fluent case filename is confirmed)
- Date: 2026-06-08
- Objective: Test whether moving the steam pressure-outlet boundary downstream of the central outlet-pipe entrance reduces outlet backflow reversal and stabilizes steam-outlet mass-flux reports.
- Geometry: child of `../purnanto-07-pure-phase-actual-area/setup.md`; uses the `purnantov2` geometry branch with setup `07` pure liquid / pure steam split inlet, plus the downstream steam-outlet extension so `steam_outlet` is placed at the end of the longer outlet path.
- Mesh: pending student-edition rebuild; record nodes, cells, minimum orthogonal quality, maximum skewness, and outlet-extension local mesh quality before running.
- Physics model: inherit setup `07` steady pressure-based `Mixture` model; primary phase steam/vapor, secondary phase liquid water; `RNG k-epsilon`; energy off unless the rebuilt Fluent case forces a documented change.
- Solver settings: inherit setup `07` (`SIMPLE`, `PRESTO!`, second-order momentum/turbulence schemes, setup `07` volume-fraction scheme, hybrid initialization) unless explicitly recorded as changed.
- Boundary and initial conditions: same setup `07` split inlet values: `inlet_liquid_outer` velocity inlet at `27.118 m/s`, liquid VF `1.0`, hydraulic diameter `0.01338 m`; `inlet_steam_inner` velocity inlet at `27.118 m/s`, liquid VF `0.0`, hydraulic diameter `0.72061 m`; `steam_outlet` pressure outlet moved to the end of the extended outlet path.
- Iteration budget: pending; choose after mesh count and student-edition runtime limit are known.
- Convergence monitors: residuals, inlet liquid/steam phase fluxes, steam-outlet phase fluxes, outlet-face backflow warnings, velocity vectors near the central outlet intake, velocity vectors inside the outlet extension, and liquid volume fraction near the outlet intake.
- Outcome: `Planned`.
- Evidence-use label: planned student-edition geometry diagnostic only. This branch can test boundary-placement sensitivity, but it is not final separator-performance evidence unless mesh quality, residual/monitor stability, and flux stability are documented.
- Hypothesized cause (if non-converged): `Inferred` pressure-outlet boundary placement at the immediate outlet-pipe entrance may expose the boundary to local swirling/recirculating flow, causing backflow reversal and unstable outlet mass-flux reporting.
- Next action: build the setup `08a` geometry from `setup.md`, confirm the former outlet-pipe entrance is internal flow passage rather than a boundary face, then initialize and verify inlet fluxes before running.
