> **Retired source:** ResearchProject_wiki/wiki/progress/experiments.md
> **Migration note:** These excerpts preserve the historical run-note record; no status or interpretation has been rewritten. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# Historical run notes

> **Retired source:** ResearchProject_wiki/wiki/progress/experiments.md
> **Migration note:** Selected run entries are preserved verbatim as historical project memory; they are not a new status or findings system.

### Run EWF-010V2A-POST-2026-07-22
- Run ID: `EWF-010V2A-POST-2026-07-22`
- Date: 2026-07-22
- Objective: Read-only post-simulation assessment of `010V2a`, the isolated Eulerian wall-film particle-splash branch.
- Geometry: active Purnanto-style separator branch with `liquidinlet`, `steaminlet`, `steamoutlet`, `bottom`, and `wall`; no lower liquid drain/brine outlet appears in the extracted flux report.
- Mesh: not captured by this post-processing pass.
- Physics model: two-phase Mixture carrier; RNG `k-epsilon`; global DPM interaction with the continuous phase `Off`; EWF splash is the intended isolated branch change, but the standard collector did not capture live EWF readback.
- Solver settings: DPM unsteady tracking `Off`; maximum particle steps `10000`; detailed EWF film numerics not captured.
- Boundary/initial condition values: phase flux extraction gives liquid inlet `111.074 kg/s`, vapour inlet `80.690 kg/s`, and vapour steam outlet `81.4218 kg/s`.
- Iteration budget: residual history through iteration `1963`.
- Convergence indicators: velocity residuals are low, but continuity finishes at `2.290e-3`; final-100 `k` spans `1.115e-2`–`3.889e-1` and epsilon spans `1.323e-2`–`5.526e-1`. The derived lower-liquid/whole-domain imbalance is `110.3422 kg/s` (`57.54 %` of inlet).
- Outcome: `Partially Converged / Diagnostic Only`.
- DPM result: the retried Particle Tracks Summary completed for all six live injections. Displayed escaped/trapped/incomplete counts are respectively `2162/0/7`, `2158/2/4`, `2007/5/4`, `1510/20/3`, `1008/33/3`, and `435/54/0` from `5.63` through `348.88 um`. The compact summary does not close to the tracked count for every injection; the unclassified differences are `1`, `6`, `158`, `641`, `1130`, and `1681`, so they remain unresolved rather than being assigned a physical fate. No splash-mass count is available.
- Assumptions: retained liquid is allowed for this no-brine-outlet EWF diagnostic; it is not a closed separator balance. Incomplete DPM tracks are retained as an unresolved long-residence population that may later escape by entrainment, not counted as completed escape or collection.
- Next action: monitor EWF film CFL, film mass/inventory, thickness, DPM-film source, film outflow, splashed represented mass, and a DPM report that identifies the unclassified fate category before comparing with `010V2`.
