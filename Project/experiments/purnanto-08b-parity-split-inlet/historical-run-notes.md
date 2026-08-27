> **Retired source:** ResearchProject_wiki/wiki/progress/experiments.md
> **Migration note:** These excerpts preserve the historical run-note record; no status or interpretation has been rewritten. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# Historical run notes

> **Retired source:** ResearchProject_wiki/wiki/progress/experiments.md
> **Migration note:** Selected run entries are preserved verbatim as historical project memory; they are not a new status or findings system.

### Run PURNANTO-08B-POSTPROCESS-2026-07-02
- Run ID: `PURNANTO-08B-POSTPROCESS-2026-07-02`
- Date: 2026-07-02
- Objective: post-process the already-run setup `08b` `5000`-iteration case/data on the live Fluent server, record the current phase-flux result, and refresh the active 6-injection DPM summary without rebuilding the case.
- Geometry: `purnanto` split-inlet parity-reset branch from `setup.md`; two `mass-flow-inlet` zones (`liquidinlet`, `steaminlet`), one `pressure-outlet` zone (`steamoutlet`), walls `bottom` and `wall`.
- Mesh: `1,309,312` nodes and `7,601,261` tetrahedral cells (`Observed` from the live case readback during the manual load and server-side post-processing session).
- Physics model: steady pressure-based `Mixture` with `2` phases; `phase-1 = water-vapor-at-psep`; `phase-2 = water-liquid-at-psep`; `RNG k-epsilon`; energy off; one-way DPM active with `pressure force = on`, `virtual mass = on`, `max_num_steps = 10000`, and `step-length-factor = 5`.
- Solver settings: carrier field already solved to the saved `5000`-iteration state before this post-processing pass; no rebuild, no new carrier iterations, and no new injections were created during this run.
- Boundary and initial conditions: liquid inlet target `116.92 kg/s`; steam inlet target `80.69 kg/s`; steam outlet only for exported phase-flux result; active DPM subset contains `5.63`, `28.14`, `56.27`, `112.54`, `168.81`, and `348.88 um` steam-side surface injections. Larger `562.70`, `844.06`, and `1631.84 um` bins were intentionally omitted from this pass.
- Iteration budget: carrier field already saved at `5000` iterations; one DPM refresh pass run through Fluent `/solve/dpm-update`.
- Convergence monitors: live post-processing extracted phase-flux output and the refreshed aggregate `dpm-summary`; no new residual history was generated because the carrier solve was not rerun.
- Outcome: `Post-processed / DPM Diagnostic Only`.
- Flux result: liquid inlet `116.92 kg/s`; steam inlet `80.69 kg/s`; steam outlet vapor `81.464165 kg/s`; steam outlet liquid `0.082132007 kg/s`.
- Calculated flux metrics: scoped steam-line liquid-removal efficiency `eta_phase = 99.92975367 %`; steam-outlet dryness `x_out = 99.89928175 %`.
- Mass-balance caution: the same live report gives mixture inlet `197.61 kg/s`, mixture outlet `81.546281 kg/s`, and mixture imbalance `116.063719 kg/s`, so the carryover result is still a scoped steam-line diagnostic, not a closed whole-separator efficiency result.
- DPM summary result: aggregate Fluent summary reports `13012` incomplete and `8` escaped particles, with no `trapped` row printed in the refreshed summary output; escaped represented mass flow is `7.005e-04 kg/s`, while incomplete represented mass is `29.22 kg/s`.
- Per-injection sampled result: one-injection-at-a-time `dpm-sample` to `steamoutlet` gives `2170` tracked particles per active injection. `injection-5-micron` reports `8` escaped and `2162` incomplete; `injection-28-micron`, `injection-56-micron`, `injection-112-micron`, `injection-168-micron`, and `injection-348-micron` each report `2170` incomplete and `0` escaped / `0` trapped in this sampled pass.
- DPM interpretation: the current active 6-bin DPM pass is dominated by incomplete tracks, so it should stay `Debug only` and should not yet be promoted to a report-facing removal-efficiency claim. The one-injection-at-a-time sample now supports the narrower statement that the observed completed sampled escape is confined to `injection-5-micron` in this pass, but the result is still not strong enough for full per-bin fate claims because tracking completion remains poor.
- Evidence-use label: valid as a live post-processing record for setup `08b` and as a current DPM-screening result for the active 6-bin subset; not valid as a full validation result or a full 9-bin historical-parity DPM result.
- Hypothesized cause (if non-converged): the dominant issue is DPM tracking completion, not obvious high escaped mass. The unresolved lower liquid inventory and lack of a separate drain/outlet closure also keep the carrier flux result from becoming a stronger whole-separator efficiency claim.
- Next action: increase DPM tracking budget first, then rerun the same active 6-bin subset before interpreting DPM more strongly; if needed, export per-injection zone summaries instead of relying only on the aggregate Fluent `dpm-summary` output.
