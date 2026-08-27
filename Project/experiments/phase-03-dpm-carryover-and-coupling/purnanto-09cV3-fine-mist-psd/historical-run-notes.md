> **Retired source:** ResearchProject_wiki/wiki/progress/experiments.md
> **Migration note:** These excerpts preserve the historical run-note record; no status or interpretation has been rewritten. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# Historical run notes

> **Retired source:** ResearchProject_wiki/wiki/progress/experiments.md
> **Migration note:** Selected run entries are preserved verbatim as historical project memory; they are not a new status or findings system.

### Run 09cV3-RUN-STUDENT-2026-08-04
- Run ID: `09cV3-RUN-STUDENT-2026-08-04`
- Date: 2026-08-04
- Objective: Hybrid-initialize the verified Student `09cV3` fine-mist child, run the first `50` iterations, save a paired checkpoint, explicitly resume from that pair, and continue toward `100` until the user requested a stop.
- Geometry: inherited Student `09cV2` velocity-inlet adaptation geometry with split `liquidinlet` / `steaminlet` topology; original case-only child remains `C:\Users\Shuhei Yokkaichi\Documents\CFD\base files\09cV3-fDPM-05pct-finemist-5to100um-velocity-inlet-adaptation.cas.h5`.
- Mesh: `177,564` nodes and `992,771` tetrahedral cells; unchanged throughout the run.
- Physics model: steady Mixture multiphase model; RNG `k-epsilon`; energy off; two-way DPM interaction on; DPM source update every flow iteration; DPM interval `1`; EWF not activated.
- Solver settings: hybrid initialization once; Settings-API iteration calls in chunks of `10`; paired case/data save at the first checkpoint; explicit case/data resume without reinitialization for the second stage.
- Boundary and initial conditions: `liquidinlet` water-liquid velocity `25.7621 m/s`; `steaminlet` water-vapor velocity `27.118 m/s`; seven active fine-mist surface injections on `steaminlet`; total DPM flow `5.846000 kg/s`; inherited input accounting `111.074000 + 5.846000 = 116.920000 kg/s`.
- Iteration budget: first stage completed at `50`; second stage was requested as `50` additional iterations, but the user stopped during the `51–60` chunk after the transcript reached `51–59`; exact in-memory progress at interruption is not claimed; no iteration-100 checkpoint was written.
- Convergence monitors: at iteration 50, continuity `6.4197e-1`; x/y/z velocity `7.1907e-4 / 6.6254e-4 / 6.6994e-4`; `k = 7.5132e-3`; epsilon `1.5149e-2`; water-liquid-VF residual `1.2477e-2`; reversed flow on `35` pressure-outlet faces; turbulent-viscosity ratio limited to `1.0e5` in `26` cells.
- DPM monitor at iteration 50: `21,581` tracked, `20,928` escaped, `650` trapped, and `3` incomplete. These are iteration monitor counts, not a completed per-injection fate result.
- Outcome: `Partially completed / User stopped / Diagnostic only`.
- Hypothesized cause (if non-converged): no causal diagnosis is promoted; the iteration-50 state still has high continuity residual and outlet reverse flow, while the inherited live mass-flow closure remains unverified for the velocity-inlet adaptation.
- Evidence-use label: valid as a run/checkpoint lineage record; not valid as converged carrier evidence, separator-performance evidence, or a per-injection DPM-fate result.
- Next action: leave the live session at the verified iteration-50 checkpoint; resume from that paired case/data only if explicitly requested.

### Run 09cV3-BUILD-2026-08-04
- Run ID: `09cV3-BUILD-2026-08-04`
- Date: 2026-08-04
- Objective: Build and strictly verify the case-only `09cV3` fine-mist PSD child from the read-back-verified Student `09cV2` velocity-inlet adaptation, changing only the active DPM injection population.
- Geometry: inherited Student `09cV2` velocity-inlet adaptation geometry and split `liquidinlet` / `steaminlet` topology; the child case is `C:\Users\Shuhei Yokkaichi\Documents\CFD\base files\09cV3-fDPM-05pct-finemist-5to100um-velocity-inlet-adaptation.cas.h5`.
- Mesh: `177,564` nodes and `992,771` tetrahedral cells, read back while loading the explicit parent and child case; no mesh change was made.
- Physics model: steady Mixture multiphase model; RNG `k-epsilon`; energy off; DPM interaction on; DPM source update every flow iteration; DPM interval `1`; EWF not activated in the inherited branch.
- Solver settings: inherited carrier and DPM tracking settings; no initialization, no solution iteration, no data read, and case-only writes only.
- Boundary and initial conditions: `liquidinlet` water-liquid velocity `25.7621 m/s`; `steaminlet` water-vapor velocity `27.118 m/s`; seven active `Surface` injections on `steaminlet`; flow inputs `0.409128`, `1.165149`, `1.267410`, `1.092501`, `1.329262`, `0.468606`, and `0.113944 kg/s`; read-back total `5.846000 kg/s`; setup-level accounting `111.074000 + 5.846000 = 116.920000 kg/s`.
- Iteration budget: `0` flow iterations; the planned `20–50`-iteration smoke test was not run in this build.
- Convergence monitors: not applicable to a case-only build; strict reload read back inlet velocities, model controls, material identities, seven injection payloads, wall fates, and the input accounting closure.
- Outcome: `Case-only build verified / diagnostic only`.
- Hypothesized cause (if non-converged): not applicable; the inherited velocity-inlet adaptation still lacks an independent live mass-flow report for the `111.074000 kg/s` Eulerian-liquid reference, and no converged carrier result is claimed.
- Evidence-use label: valid as a setup and lineage record; not valid as a separator-performance, convergence, or DPM-fate result. The seven-bin PSD is an `Assumed`, medium-risk engineering prior rather than measured inlet data.
- Next action: if the user authorizes execution, run the documented short smoke test from the saved child, preserving the case-only checkpoint and recording residuals, phase fluxes, DPM source terms, and per-injection fates.
