# Current Status

## Snapshot
- Date: 2026-06-09
- Phase: direct Purnanto-recreation reset plus retained setup `07` archive context
- Focus: rebuild the paper-style Purnanto setup on the current project path using one mixed steam-water inlet rather than the later split-inlet branches.
- Current issue: setup `07` has promising apparent steam-line carryover; bottom truncation/no brine outlet/no water pool is now accepted as out of scope for this project branch.
- Current mesh scale: professional setup `07` run reported at approximately `1.3M` nodes and `7.6M` cells; older project mesh scale was approximately `1.8M` nodes.
- Current controlled setup change: new setup `08` returns to the one-inlet Purnanto mass-flow package; older split-inlet and velocity-inlet branches remain comparison context only.
- Latest diagnostic result: `PLS-PRO-2026-06-03-A` reports very low apparent liquid carryover at the steam outlet (`0.03663388722044243 kg/s`, `0.03135 %` of liquid inlet if interpreted as carryover magnitude). Treat this as a scoped steam-carryover diagnostic, not a full brine-drainage balance.
- New baseline audit: `PURNANTO-LIVE-AUDIT-2026-06-05` loaded `purnanto-setup.cas.h5` and `purnanto-setup-5000.dat.h5`; the live case matches the core Purnanto baseline solver stack and records a `2,964,593`-cell tetra mesh with minimum orthogonal quality `0.277635`.
- New direct-rebuild branch: setup `08` now records the paper-style one-inlet mixed steam-water `Mass-Flow Inlet` package so the project can return to the closest Purnanto recreation before judging split-inlet alternatives.
- New PyFluent result: the local `trial3.msh` one-inlet reconstruction now launches, creates manual water vapor/liquid materials, hybrid-initializes, and completes a `10`-iteration smoke test through the script in `../../../PyAnsys/scripts/reconstruct_purnanto_trial3.py`.
- New hardened PyFluent result: the same one-inlet reconstruction path now runs on `trial4.msh` with clean `Operating Pressure = 0 Pa`, confirmed 2026 R1 numerics paths, mass-flow sanity reporting, and both case/data writes.
- New longer PyFluent result: a controlled `500`-iteration `trial4` diagnostic run has now completed on the one-steam-outlet branch with chunked reporting, checkpointing, vapor recovery approximately `1.0092`, liquid carryover approximately `3.97e-25`, and a rough residual-history plot recovered from the Fluent transcript.
- Active setup branch: `../../../Setup report/08-purnanto-one-inlet-massflow-recreation.md` is now the selected direct baseline-rebuild branch; `../../../Setup report/07-pure-phase-split-actual-area.md` is retained as a comparison-only split-inlet branch.
- Archive guard: do not archive chats that were active on or after `2026-05-25`; older chats can be archived only after their durable outcomes are confirmed in the wiki and setup-report files.

## What Is Done
- Rough literature overview completed.
- Baseline geometry provided and run attempts started.
- Initial non-convergence signal observed.
- Baseline steady two-phase setup defined in Fluent (pressure-based, RNG k-epsilon, Mixture model, gravity, isothermal assumption).
- A first project-specific inlet-regime change has now been defined conceptually: split inlet with wall-side liquid and inner-side steam.
- Geometry context has been clarified: this split-inlet plan is for the **spiral-inlet** baseline case.
- Mesh density increased from earlier approximately 300k-node run to approximately 1.8M nodes.
- Team split clarified: partner is working on validation/parameter-sweep comparison against analytical data, while Shuhei's immediate lane is now setup `07` steam-carryover/DPM post-processing.
- Current attempted setup history includes two-phase inlet design, brine outlet representation, and a downstream water-pool child case, but setup `07` now explicitly treats bottom liquid handling as out of scope.
- Current usable simulation evidence is limited to documented above-threshold or professional-license diagnostics: `FFF-2` at approximately `1020` iterations, `MWH-WP-2026-05-07-A` at approximately `3500` iterations, and `PLS-PRO-2026-06-03-A` as the newest professional setup `07` flux diagnostic.
- Parent no-water-pool run `FFF-2`, Phase 0 outlet audit, and `FFF-2-OP0` remain historical troubleshooting evidence for older brine-outlet branches.
- A report-facing calculation scaffold now records the actual inlet-half area `2.6209e5 mm2 = 0.26209 m2`, giving total liquid inlet `115.59 kg/s`, total steam inlet `79.77 kg/s`, and total inlet flow `195.36 kg/s` for the mixed wet-half velocity-inlet setup.
- A new complete two-phase no-brine-outlet setup report now converts the same actual-area basis into one full-inlet velocity condition: `26.81 m/s`, liquid volume fraction `0.009328`, steam volume fraction `0.990672`, full inlet area `0.52418 m2`, calculated liquid inlet `115.59 kg/s`, steam inlet `79.77 kg/s`, and total inlet `195.37 kg/s`.
- The pure-liquid/pure-steam equal-velocity split has now been recalculated using Purnanto's `1600 kJ/kg` target phase flows and the current `0.724 m x 0.724 m` inlet: common velocity `27.118 m/s`, liquid strip area `0.0048896 m2`, steam area `0.5192864 m2`, and split line `0.006754 m` from the liquid-side edge if split along `x`.
- A separate fixed-velocity pure-phase split report now keeps Purnanto's reported spiral-inlet velocity `26.81 m/s`; with the current `0.724 m x 0.724 m` inlet and the same `0.006754 m` liquid-side split, the expected inlet mass flows are liquid `115.59 kg/s`, steam `79.77 kg/s`, and total `195.37 kg/s`.
- Active decision: for the next pure liquid / pure steam split-inlet case, use the current-area exact-mass velocity `27.118 m/s`, not the fixed reported-velocity `26.81 m/s` alternate.
- New active setup report created for the pure liquid / pure steam actual-area velocity-inlet case with turbulence intensity `2.10999999 %`, liquid hydraulic diameter `0.01338 m`, and steam hydraulic diameter `0.72061 m`.
- Two rough student-edition pure-phase split diagnostics are now documented against that same inlet sizing. Setup 2 reduced steam-line liquid carryover from `10.67 kg/s` to `7.73 kg/s`, improving implied carryover-based efficiency from `90.87 %` to `93.39 %` and steam-outlet dryness from `88.39 %` to `91.33 %`, but both remain non-converged low-mesh diagnostics only.
- Professional-license setup `07` flux diagnostic is now documented: mesh approximately `1.3M` nodes and `7.6M` cells; liquid inlet `116.8523 kg/s`; steam inlet `81.6395 kg/s`; steam outlet steam `86.2934 kg/s`; steam outlet liquid `0.03663 kg/s`.
- New literature anchors are now linked into the project layer: Pointon et al. 2009 adds a geothermal HP-separator CFD scale/pressure-drop/scrolled-entry check, and Chen et al. 2025 adds an experiment-backed `RSM-DPM` separator-method benchmark for any later turbulence-model sensitivity decision.
- Newest documented run: `PLS-PRO-2026-06-03-A`, based on `Setup report/07-pure-phase-split-actual-area.md`.
- Newest baseline audit: `PURNANTO-LIVE-AUDIT-2026-06-05`, recorded in `../../../Setup report/00a-purnanto-setup-5000-live-audit.md`.
- New direct-rebuild report: `../../../Setup report/08-purnanto-one-inlet-massflow-recreation.md`.
- New local automation note: `../technical/pyfluent-trial3-one-inlet-reconstruction-smoke-test.md`.
- New local reusable doc: `../../../PyAnsys/docs/LOCAL_ONE_INLET_SMOKE_TEST.md`.
- New residual artifact set: `trial4-purnanto-recon-500-residuals.png` and `trial4-purnanto-recon-500-residuals.csv` now exist beside the `500`-iteration case/data outputs.
- Older water-pool run `MWH-WP-2026-05-07-A` showed more plausible swirl after 3500 steady iterations but is retained only as historical troubleshooting evidence.

## What Is In Progress
- Preparing the direct one-inlet rebuild from setup `08` so the project returns to the closest Purnanto boundary package.
- Narrowing the remaining PyFluent caveats to the operating-pressure API path and the correct 2026 R1 solution-method setter paths.
- Narrowing the remaining PyFluent caveats further to pressure-outlet setting inactivity cleanup and cleaner balance reporting.
- The direct one-inlet PyFluent path now has a longer controlled diagnostic result; remaining cleanup is mainly pressure-outlet setting inactivity, cleaner balance reporting, and a better direct residual export path.
- Preparing quick DPM post-processing using `../../../CFD_wiki/wiki/synthesis/fluent-separator-efficiency-methods.md` and `../../../CFD_wiki/wiki/guidance/fluent-general-click-by-click.md`.
- Historical convergence and physical-behavior notes for the parent mixed wet-half velocity-inlet/brine-outlet case are retained, but they are not active setup `07` blockers.
- Verification of flow settings and numerical configuration.
- Review of whether mesh quality, worst-cell location, and mesh-independence evidence are sufficient for stable solution progression.
- Building a result-interpretation workflow to connect contour outputs to separator performance decisions.
- Post-processing the professional setup `07` case/data for residual/monitor stability and DPM particle fate counts.
- Preparing the first geometry/mesh-level inlet modification so it changes only boundary representation, not the full solver stack.
- Deciding whether the rough Setup 2 trend is real or mostly caused by the simultaneous switch from velocity inlet to mass-flow inlet.
- Any future return to parent-case outlet behavior, solver/numerics, or water-pool depletion should be treated as a separate scope decision, not part of the setup `07` baseline.
- Older `MWH-WP-2026-05-07-A` remains qualitative historical evidence only; `PLS-PRO-2026-06-03-A` is now the newest documented diagnostic.
- Lower-iteration runs remain useful only for setup history and failure-mode hints, not for quantitative performance claims.
- Deferred run branch: complete two-phase full spiral inlet with no active brine outlet remains an older inlet/mixing diagnostic option, not the immediate next action.
- Split-inlet branches remain archived comparison options, not the immediate direct-baseline action.

## Chat Cleanup Readiness
- Older chats should be treated as archive candidates only after the decision, evidence, blocker state, and next action are visible in repo files.
- Recent chats from `2026-05-25` onward are intentionally excluded from cleanup for now, even if their contents are already logged.
- The main remaining archive-risk before removing reliance on older chats was the stale snapshot date on this page and ambiguous branch state in the setup-order dictionary; this cleanup pass addresses those two gaps.

## Immediate Next Actions
1. Check whether the remaining pressure-outlet subsetting inactivity needs a different setting order or can be treated as harmless for the current controlled diagnostic path.
2. Keep the direct one-inlet `trial4` PyFluent path as the active local parity and longer-diagnostic baseline.
3. If useful, improve the direct residual-export path so future plots do not depend on transcript parsing.
4. Treat setup `07` and its DPM evidence as comparison-only context until the direct Purnanto-recreation branch is cleaner and more repeatable.

## Roadmap Link
- Run-efficiency roadmap: `../project/roadmap.md`
