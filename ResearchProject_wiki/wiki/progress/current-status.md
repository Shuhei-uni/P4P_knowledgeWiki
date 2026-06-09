# Current Status

## Snapshot
- Date: 2026-06-09
- Phase: Setup `08` student-edition outlet-extension trial planning, with setup `07` retained as the parent baseline
- Focus: preserve setup `07` as the active scoped steam-carryover baseline while testing whether downstream steam-outlet boundary placement reduces outlet backflow reversal in a student-edition geometry trial.
- Current issue: setup `07` has promising apparent steam-line carryover, but user-observed steam-outlet backflow reversal and inconsistent mass-flux reports may be affected by placing the pressure-outlet boundary directly at the outlet-pipe entrance.
- Current mesh scale: professional setup `07` run reported at approximately `1.3M` nodes and `7.6M` cells; older project mesh scale was approximately `1.8M` nodes.
- Current controlled setup change: professional setup `07` uses the pure liquid / pure steam actual-area split; older `FFF-2-OP0` pressure-reference parity work remains historical troubleshooting context.
- Latest diagnostic result: `PLS-PRO-2026-06-03-A` reports very low apparent liquid carryover at the steam outlet (`0.03663388722044243 kg/s`, `0.03135 %` of liquid inlet if interpreted as carryover magnitude). Treat this as a scoped steam-carryover diagnostic, not a full brine-drainage balance.
- New baseline audit: `PURNANTO-LIVE-AUDIT-2026-06-05` loaded `purnanto-setup.cas.h5` and `purnanto-setup-5000.dat.h5`; the live case matches the core Purnanto baseline solver stack and records a `2,964,593`-cell tetra mesh with minimum orthogonal quality `0.277635`.
- Fresh HDF5 extraction: the local `PyAnsys/data/4800-iterations-300412-1.cas.h5` and `PyAnsys/data/4800-iterations-300412-1-05000.dat.h5` pair was extracted successfully, confirming the same baseline stack in a portable audit-friendly form and giving a new friendly reference page for the live setup values.
- Active setup branch: `../../../Setup report/08-steam-outlet-extension-student-trial.md` is the next planned student-edition diagnostic child of setup `07`; `../../../Setup report/07-pure-phase-split-actual-area.md` remains the professional-license parent baseline.
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
- New setup `08` is now defined as a student-edition geometry trial: keep Purnanto's spiral-inlet separator body and the setup `07` pure-phase split inlet, but extend the central steam outlet path so the `steam_outlet` pressure boundary is placed downstream of the outlet-pipe entrance.
- New literature anchors are now linked into the project layer: Pointon et al. 2009 adds a geothermal HP-separator CFD scale/pressure-drop/scrolled-entry check, and Chen et al. 2025 adds an experiment-backed `RSM-DPM` separator-method benchmark for any later turbulence-model sensitivity decision.
- Newest documented run: `PLS-PRO-2026-06-03-A`, based on `Setup report/07-pure-phase-split-actual-area.md`.
- Newest baseline audit: `PURNANTO-LIVE-AUDIT-2026-06-05`, recorded in `../../../Setup report/00a-purnanto-setup-5000-live-audit.md`.
- Older water-pool run `MWH-WP-2026-05-07-A` showed more plausible swirl after 3500 steady iterations but is retained only as historical troubleshooting evidence.

## What Is In Progress
- Confirming residual/monitor stability for professional setup `07` before treating the high apparent steam-carryover efficiency as report-ready.
- Preparing quick DPM post-processing using `../../../CFD_wiki/wiki/synthesis/fluent-separator-efficiency-methods.md` and `../../../CFD_wiki/wiki/guidance/fluent-general-click-by-click.md`.
- Historical convergence and physical-behavior notes for the parent mixed wet-half velocity-inlet/brine-outlet case are retained, but they are not active setup `07` blockers.
- The Purnanto baseline assumptions that were still lingering in project pages are now being replaced by the audited live HDF5 setup reference so the setup stack does not need to be reconstructed from memory again.
- Verification of flow settings and numerical configuration.
- Review of whether mesh quality, worst-cell location, and mesh-independence evidence are sufficient for stable solution progression.
- Building a result-interpretation workflow to connect contour outputs to separator performance decisions.
- Post-processing the professional setup `07` case/data for residual/monitor stability and DPM particle fate counts.
- Building the setup `08` geometry/mesh as a controlled outlet-boundary-placement diagnostic. The purpose is to test the user's hypothesis that the immediate top outlet boundary caused backflow reversal and unstable mass-flux reports.
- Preparing the first geometry/mesh-level inlet modification so it changes only boundary representation, not the full solver stack.
- Deciding whether the rough Setup 2 trend is real or mostly caused by the simultaneous switch from velocity inlet to mass-flow inlet.
- Any future return to parent-case outlet behavior, solver/numerics, or water-pool depletion should be treated as a separate scope decision, not part of the setup `07` baseline.
- Older `MWH-WP-2026-05-07-A` remains qualitative historical evidence only; `PLS-PRO-2026-06-03-A` is now the newest documented diagnostic.
- Lower-iteration runs remain useful only for setup history and failure-mode hints, not for quantitative performance claims.
- Deferred run branch: complete two-phase full spiral inlet with no active brine outlet remains an older inlet/mixing diagnostic option, not the immediate next action.

## Chat Cleanup Readiness
- Older chats should be treated as archive candidates only after the decision, evidence, blocker state, and next action are visible in repo files.
- Recent chats from `2026-05-25` onward are intentionally excluded from cleanup for now, even if their contents are already logged.
- The main remaining archive-risk before removing reliance on older chats was the stale snapshot date on this page and ambiguous branch state in the setup-order dictionary; this cleanup pass addresses those two gaps.

## Immediate Next Actions
1. Record residual/monitor stability for `PLS-PRO-2026-06-03-A` so the flux result can be classified beyond `Baseline Flux Diagnostic`.
2. For `PURNANTO-LIVE-AUDIT-2026-06-05`, run phase mass-flow reports, locate turbulent-viscosity-limited cells, and visually confirm which Purnanto geometry variant this case represents.
3. Use the currently applied baseline DPM settings: one-way deterministic tracking, step factor `2`, flow rate `1e-6 kg/s`, particle rotation off, and stochastic tracking off.
4. Use the current project interpretation for setup `07`: treat incomplete DPM particles as trapped when they are assumed to be wall-stuck.
5. Report scoped DPM removal efficiencies for the updated water-density runs as `63.0 %` at `5 um`, `88.5 %` at `1 um`, `93.0 %` at `10 um`, and `100 %` at `41 um` and `100 um`.
6. Treat the deterministic `5 um` water-density case as the primary fine-droplet reference; DRW and rotation sensitivities still shift it only a few percentage points.
7. Leave transient Eulerian Wall Film modelling as an exploratory follow-up until the basic DPM fate counts are stable.
8. Optionally increase DPM max steps to `100,000` and rerun at least the `10 um` case to test whether the `93.0 %` result survives with fewer incomplete tracks.
9. Build setup `08` from `../../../Setup report/08-steam-outlet-extension-student-trial.md` in the student-edition environment, keeping setup `07` inlet and solver settings unchanged except for the steam outlet extension.
10. For setup `08`, save geometry screenshots, boundary-zone screenshots, mesh statistics, residuals, inlet fluxes, steam-outlet fluxes, and outlet-intake velocity/vector evidence before interpreting any efficiency change.
11. If the rough student-edition Setup 2 direction is still worth keeping, repeat it later as a controlled comparison without changing inlet boundary type at the same time.
12. Fold the new HDF5 audit reference into the Purnanto setup pages so future runs can cite the extracted case instead of repeating the same setup assumptions.

## Roadmap Link
- Run-efficiency roadmap: `../project/roadmap.md`
