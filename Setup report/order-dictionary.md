# Setup Report Order Dictionary

## Purpose

This file is the ordering reference for `Setup report/`.

Use it to answer two questions quickly:

1. which setup came before or after another;
2. which filename should be used when reports are renamed into a strict sequence.

This is an ordering aid, not proof that every branch was run to completion.
Where the history is uncertain, the ordering below reflects the current best reconstruction from:

- `ResearchProject_wiki/wiki/log.md`
- `ResearchProject_wiki/wiki/progress/current-status.md`
- `ResearchProject_wiki/wiki/progress/experiments.md`
- internal parent/child notes inside each setup report

## Naming Rule

Recommended stable filename pattern:

```text
NN[-branch]-short-description.md
```

Where:

- `NN` = primary sequence number
- optional `branch` = side branch from that stage, for example `02b` or `03a`
- `short-description` = concise setup identity, not status words like `current`

Rules:

- Keep numbers stable once assigned.
- Add branch suffixes instead of renumbering old reports.
- Avoid words like `current`, `latest`, or `final`.
- Keep the main sequence for the dominant setup lineage.
- Mark abandoned or invalid side branches in notes, not in the numbering itself.

## Proposed Strict Order

| Order | Role in lineage | Current file | Proposed stable filename | Confidence | Last known state | Notes |
|---|---|---|---|---|---|---|
| `00` | baseline reference | `00-baseline-spiral-boc-reference.md` | `00-baseline-spiral-boc-reference.md` | High | reference baseline | source-style baseline report used as the root reference for later variants |
| `00a` | live Purnanto baseline audit | `00a-purnanto-setup-5000-live-audit.md` | `00a-purnanto-setup-5000-live-audit.md` | High | loaded 5000-iteration case/data audit | child audit of `00`; records the Fluent 2024 R2 case/data snapshot without making it part of the main project variant lineage |
| `01` | first split-inlet branch | `01-split-two-zone-massflow-inlet.md` | `01-split-two-zone-massflow-inlet.md` | High | superseded concept branch | first explicit two-zone split concept; keeps `Mass-Flow Inlet` |
| `02` | velocity-inlet full-geometry branch | `02-split-two-zone-velocity-inlet-brine-outlet.md` | `02-split-two-zone-velocity-inlet-brine-outlet.md` | Medium | superseded diagnostic parent | appears to be the next branch after `01` |
| `02b` | side experiment branch | `02b-vof-split-inlet-transient.md` | `02b-vof-split-inlet-transient.md` | Medium | retired invalid side branch | experimental branch; later marked invalid and not continued |
| `03` | mixed wet-half main branch | `03-mixed-wet-half-velocity-inlet.md` | `03-mixed-wet-half-velocity-inlet.md` | High | stalled diagnostic parent | replaces pure split with equal-velocity wet-half concept |
| `03a` | child of `03` | `03a-mixed-wet-half-velocity-inlet-water-pool.md` | `03a-mixed-wet-half-velocity-inlet-water-pool.md` | High | diagnostic child run only | explicit child case of `03` |
| `04` | actual-area recalculation branch | `04-mixed-wet-half-actual-area.md` | `04-mixed-wet-half-actual-area.md` | High | active calculation parent | same mixed wet-half idea, updated to measured actual inlet area |
| `05` | full-inlet alternative branch | `05-complete-two-phase-actual-area-no-brine-outlet.md` | `05-complete-two-phase-actual-area-no-brine-outlet.md` | High | planned diagnostic branch | branch from `04`; one full inlet, no active brine outlet |
| `06` | fixed-velocity pure-phase alternative | `06-pure-phase-split-fixed-velocity.md` | `06-pure-phase-split-fixed-velocity.md` | High | alternate retained | branch from later actual-area work; preserves `26.81 m/s` |
| `07` | pure-phase actual-area branch | `07-pure-phase-split-actual-area.md` | `07-pure-phase-split-actual-area.md` | High | professional baseline flux diagnostic completed | selected next setup definition after `06` was kept as alternate; professional-license run now recorded with incomplete surface flux balance pending brine/liquid outlet report |
| `07a` | split-inlet carrier mesh-convergence branch | `07a-split-inlet-carrier-mesh-convergence.md` | `07a-split-inlet-carrier-mesh-convergence.md` | High | completed diagnostic / iteration and mesh independence unresolved | child of `07`; seven carrier-only meshes completed at 3000 iterations and a 900k diagnostic reached 6000, but increasing closed-bottom liquid inventory prevents an accepted steady mesh-convergence claim |
| `07b` | constant-water-level liquid-sink branch | `07b-split-inlet-constant-water-level-liquid-sink.md` | `07b-split-inlet-constant-water-level-liquid-sink.md` | High | completed diagnostic / physical qualification failed | child of `07`; clean 900k `tau=0.1 s` run reached 6,000 full-strength iterations with zero passing windows, sink far below liquid inlet and increasing domain inventory; use only as diagnostic evidence and move the next steady branch to a resolved brine outlet |
| `07c` | thickened constant-water-level liquid-sink sensitivity | `07c-split-inlet-thickened-constant-water-level-liquid-sink.md` | `07c-split-inlet-thickened-constant-water-level-liquid-sink.md` | High | completed diagnostic / physical qualification failed | diagnostic child of `07b`; a 16-layer-equivalent bottom-local band increased sink removal but reached 2,000 full-strength iterations with zero passing windows, rising inventory/pressure and no steady liquid closure |
| `07d` | capacity-matched thick-sink strength sensitivity | `07d-split-inlet-capacity-matched-thick-sink.md` | `07d-split-inlet-capacity-matched-thick-sink.md` | High | completed diagnostic / unresolved | controlled child of `07c`; a fivefold coefficient increase produced only a 2.09x sink, removed 40.2% of liquid feed and still failed liquid closure and pressure/inventory stability |
| `07e` | adaptive mass-balance sink control | `07e-split-inlet-adaptive-mass-balance-sink-control.md` | `07e-split-inlet-adaptive-mass-balance-sink-control.md` | High | completed diagnostic / unresolved | controlled child of `07d`; completed 3,000 total iterations with a `50.954294 kg/s` sink, `56.419329%` corrected liquid imbalance, failed stability/residual gates and zero passing windows; proves the local source remains capacity-limited and does not replace a resolved brine outlet |
| `07f` | sink thickness and rate diagnostic matrix | `07f-split-inlet-sink-thickness-rate-matrix.md` | `07f-split-inlet-sink-thickness-rate-matrix.md` | High | running diagnostic matrix | bounded user-requested extension of `07c`-`07e`; queues doubled/tripled bottom-local bands and faster fixed source coefficients from the verified clean 900k origin, with DPM off and no physical outlet claim |
| `07g` | resolved brine-outlet dry-start qualification | `07g-split-inlet-resolved-brine-outlet-qualification.md` | `07g-split-inlet-resolved-brine-outlet-qualification.md` | High | stopped at verified iteration 500 / diagnostic unresolved | clean resolved-outlet branch preserved both net outlet flows outward, but brine flow was vapor-dominant with liquid reversing inward; later live state diverged and is excluded |
| `07h` | resolved brine-outlet initial-liquid-pool qualification | `07h-split-inlet-resolved-brine-outlet-initial-liquid-pool.md` | `07h-split-inlet-resolved-brine-outlet-initial-liquid-pool.md` | High | stopped at verified iteration 250 / diagnostic unresolved | controlled child of `07g`; the geometry-inferred pool initially established the intended phase route, but brine liquid outflow became nonphysical and the next block ended in AMG divergence/floating-point exception at residual row 292 |
| `07i` | resolved brine-outlet WFGC-only sensitivity | `07i-split-inlet-resolved-brine-outlet-wfgc-sensitivity.md` | `07i-split-inlet-resolved-brine-outlet-wfgc-sensitivity.md` | High | failed diagnostic at raw iteration 21 / terminal | one-factor child of `07h`; corrected connectivity evidence proves 16 solver processes (`n0..n15`, with `/20` denoting hardware cores), so the WFGC/pool preparation was valid; continuity reached `6.9888e14` at transcript row 20 and the GUI then recorded Node-4 SIGSEGV/server shutdown at iteration 21; zero complete blocks were credited, no divergent checkpoint was written, and setup `07j` transient VOF is next |
| `07j` | resolved brine-outlet transient VOF qualification | `07j-split-inlet-resolved-brine-outlet-transient-vof.md` | `07j-split-inlet-resolved-brine-outlet-transient-vof.md` | High | stopped diagnostic at step 2 / equal-pressure bracket rejected | source-free successor to `07i`; clean transient explicit VOF preparation passed, but the equal-`1.12 MPa` outlet bracket produced `-4692.8688 kg/s` brine-liquid drainage at `t=0.0002 s`; inventory/flux closure proves the drainage is physical to the model, so the field is not resumed and setup `07k` is the controlled prescribed-flow sensitivity |
| `07k` | resolved brine-outlet transient VOF prescribed-flow diagnostic | `07k-split-inlet-transient-vof-massflow-brine-outlet.md` | `07k-split-inlet-transient-vof-massflow-brine-outlet.md` | High | failed diagnostic at step 3 / terminal | controlled child of `07j`; the prescribed `116.92 kg/s` liquid route held exactly, but step 3 developed `-4.1102e13 Pa` steam-outlet pressure and `5.2599e6 m/s` outlet velocity; the step-4 RPC timed out uncredited, no controller remains and this field must not be resumed |
| `07l` | resolved brine-outlet hydrostatic-rest isolation | `07l-split-inlet-hydrostatic-rest-isolation.md` | `07l-split-inlet-hydrostatic-rest-isolation.md` | High | completed / accepted bounded diagnostic | forensic child of `07j/07k`; deletes six inherited DPM injections, closes the brine face and zeros inlets, then proves the 620,431-cell pool remains bounded for ten `1e-6 s` steps; observed lower-face head `2090.4 Pa` is close to `rho_l g h=2197.24 Pa`, so the open production boundary remains unresolved |
| `07m` | zero-feed pressure opening and guarded inlet startup | `07m-split-inlet-zero-feed-pressure-opening-and-inlet-ramp.md` | `07m-split-inlet-zero-feed-pressure-opening-and-inlet-ramp.md` | High | retained numerical diagnostic / stopped at 1% continuity gate | child of setup `07l`; nine pressure/time-step openings and the 0.1% hold were bounded, 0.2% and 0.5% passed, and the finite 1% checkpoint stopped at continuity `0.0177001`; the proposed same-flow hold had a zero-step connection timeout and is now optional numerical evidence rather than the main physical continuation, while the level and pressure remain unvalidated |
| `07n` | resolved brine-outlet constant-level model and solver screening | `07n-resolved-brine-outlet-model-solver-screening.md` | `07n-resolved-brine-outlet-model-solver-screening.md` | High | short low-feed drainage accepted / sustained control unresolved | the ten-step 0.05% member retained excellent residuals, balance and steam sealing. Fixed pressure drifted, per-step feedback overshot or remained slow, and an evidence-calibrated `+23.2188 Pa` step passed every numerical/seal gate but failed the 70-step final-ten balance gate at `0.01155 kg/s` liquid imbalance. All endpoints are ineligible and non-resumable; Fluent VOF exposes no bulk mass-flow-outlet rate, the pressure is CFD-derived, and full flow, level control and mesh convergence remain unproved |
| `08` | direct Purnanto-recreation branch | `08-purnanto-one-inlet-massflow-recreation.md` | `08-purnanto-one-inlet-massflow-recreation.md` | High | selected direct baseline-rebuild branch | returns to the paper-style one-inlet mixed steam-water `Mass-Flow Inlet` package using the live Purnanto audit and reusable CFD baseline as the concrete rebuild target |
| `08a` | steam-outlet boundary-placement trial | `08a-steam-outlet-extension-student-trial.md` | `08a-steam-outlet-extension-student-trial.md` | High | planned student-edition diagnostic branch | child of `07`; keeps the Purnanto spiral-inlet body and setup `07` split two-phase inlet, but extends the central steam outlet path so the pressure-outlet boundary is downstream of the outlet-pipe entrance |
| `08b` | Purnanto baseline enthalpy and DPM sweep | `08b-purnanto-baseline-enthalpy-dpm-sweep.md` | `08b-purnanto-baseline-enthalpy-dpm-sweep.md` | High | completed six-condition calculation branch | child of `08`; uses `baseline.cas.h5`, Bangma-target Harwell inputs, 1500 evidenced iterations per case, and injection-level DPM fate exports; geometry identity and convergence remain unresolved |
| `08c` | Purnanto spiral-inlet enthalpy and DPM sweep | `08c-purnanto-spiral-inlet-enthalpy-dpm-sweep.md` | `08c-purnanto-spiral-inlet-enthalpy-dpm-sweep.md` | High | completed six-condition calculation branch | sibling of `08b` under `08`; uses the spiral baseline, spiral-area Harwell inputs, 1500 evidenced iterations per case, and injection-level DPM fate exports |
| `09` | multiphase sensitivity family parent | `09-multiphase-separator-sensitivity-family.md` | `09-multiphase-separator-sensitivity-family.md` | High | active family container | child of `07`; replaces the retired VOF-only idea with a parent container for literature-backed `DPM`, `RSM-DPM`, and `DPM + EWF` child branches |
| `09a` | split-inlet DPM carryover branch | `09a-dpm-split-inlet-carryover.md` | `09a-dpm-split-inlet-carryover.md` | High | planned first carryover branch | child of `09`; keeps the setup `07` continuous-field basis and adds `DPM` as the lowest-risk literature-backed next step for droplet escape sensitivity |
| `09b` | split-inlet RSM-DPM accuracy branch | `09b-rsm-dpm-split-inlet-accuracy.md` | `09b-rsm-dpm-split-inlet-accuracy.md` | High | planned higher-accuracy branch | child of `09`; upgrades the carrier-field turbulence closure to `RSM` and adds `DPM`, following the stronger recent separator-method anchor from Chen 2025 |
| `09c` | split-inlet DPM + EWF wall-film branch | `09c-dpm-ewf-wall-film-reentrainment.md` | `09c-dpm-ewf-wall-film-reentrainment.md` | High | planned wall-film mechanism branch | child of `09`; treats wall-film persistence and re-entrainment as the main unresolved mechanism rather than only droplet escape |

## Parent-Child Map

```text
00 baseline
 -> 00a Purnanto setup 5000 live audit
    -> 08 Purnanto one-inlet mass-flow recreation
       -> 08b Purnanto baseline enthalpy and DPM sweep
       -> 08c Purnanto spiral-inlet enthalpy and DPM sweep
 -> 01 split two-zone mass-flow inlet
    -> 02 split two-zone velocity inlet with brine outlet
       -> 02b VOF split-inlet transient side branch
       -> 03 mixed wet-half velocity inlet
          -> 03a mixed wet-half with initialized water pool
          -> 04 mixed wet-half actual-area
             -> 05 complete two-phase actual-area no-brine-outlet
             -> 06 pure-phase split fixed velocity
             -> 07 pure-phase split actual-area
                -> 07a split-inlet carrier mesh convergence
                -> 07b constant-water-level liquid sink
                   -> 07c thickened constant-water-level sink diagnostic
                      -> 07d capacity-matched thick-sink strength diagnostic
                         -> 07e adaptive mass-balance sink control diagnostic
                            -> 07f sink thickness/rate diagnostic matrix
                -> 07g resolved brine-outlet dry-start qualification
                   -> 07h resolved brine-outlet initial-liquid-pool qualification
                      -> 07i WFGC sensitivity
                         -> 07j transient VOF equal-pressure diagnostic
                            -> 07k prescribed brine-flow diagnostic
                            -> 07l hydrostatic-rest isolation diagnostic
                               -> 07m zero-feed pressure opening and guarded inlet ramp
                                  -> 07n resolved brine-outlet model and solver screening
                -> 08a steam outlet extension student-edition trial
                -> 09 multiphase sensitivity family
                   -> 09a split-inlet DPM carryover
                   -> 09b split-inlet RSM-DPM accuracy
                   -> 09c split-inlet DPM + EWF wall-film
```

## Working Interpretation

- Main lineage:
  `00 -> 01 -> 02 -> 03 -> 04 -> 07 -> 09`
- Child/side branches:
  `00a`, `02b`, `03a`, `05`, `06`, `07a`, `07b`, `07c`, `07d`, `07e`, `07f`, `07g`, `07h`, `08`, `08a`, `08b`, `08c`, `09a`, `09b`, `09c`

Interpretation note:

- `07f` is an intentionally bounded diagnostic extension requested while geometry editing is unavailable; it does not supersede the resolved-brine-outlet recommendation.
- `07g` is the dry-start resolved-outlet diagnostic; its verified iteration-500 field must not be used as an accepted carrier baseline.
- `07h` tests the same resolved outlet with an explicit lower liquid reservoir. Failure or initialization dependence in `07h` triggers a transient successor, not arbitrary pressure tuning.
- `07n` is the fresh carrier-only constant-level/model/solver sensitivity
  family for the resolved brine outlet. It uses 07l/07m as evidence rather than
  assuming their field, level or pressure is physically authoritative, corrects
  the scope of the older setup-09 VOF statement and does not activate the
  DPM/EWF carryover branches. Stage 0 now has accepted crown/area/inventory and
  an exact whole-cell selection plateau. The direct adjacent-cell vertex height
  and plant level remain unknown. The diagnostic 07n-a relaxation now extends
  through step 940 / `0.22271 s`. Matched `dt/2` and `dt/4` windows reached the
  same `0.22783 s`, but the half-to-quarter discrepancies did not contract
  (`1.43%` average velocity, `1.40%` vorticity and `7.49%` maximum velocity).
  A matched 100-inner branch reproduced the 20-inner field within `0.000009%`,
  clearing inner convergence as the cause. Accepted localization places all
  maxima in the same interfacial cell and excludes the known limiter cell.
  The matched `dt/8` branch also failed to contract the differences, so
  explicit halving stopped. Accepted zero-step readback then enabled matched
  implicit/PISO Compressive and Modified-HRIC branches: all gates passed, but
  the best implicit endpoint retained a `6.831%` maximum-velocity difference
  from explicit. Explicit plain Coupled reproduced PISO within `0.000063%` at
  `3.234x` the summed solve-step wall time. PISO is retained for bounded
  diagnostics; no solver endpoint is promoted, and outlet/control work remains
  separately gated.
  A separately configured server-2 endpoint was subsequently distinguished
  from the partner's occupied Fluent 2025 R2 endpoint. It ran a clean,
  non-authoritative closed-pool reconstruction on Fluent 2024 R2/16 ranks:
  `dt=2.56e-4 s` is the last clean independent comparison and `dt=5.12e-4 s`
  is a terminal residual-envelope failure. That chain has zero feed and a
  closed brine wall, cannot be merged into the server-1 lineage and does not
  qualify drainage, level control or operating mass balance.
  On 25 August a same-`dt` closed control from its clean step-90 pair passed
  four fully monitored steps, then stalled in post-solve scratch-report cleanup
  after an uncredited fifth step. A separately labelled pressure-bracket
  attempt stopped before authentication because Fluent gRPC/Scheme did not
  return its version string. Both are non-resumable diagnostics; no outlet was
  opened and the last clean step-90 pair remains the only eligible independent
  starting point.
- `08` is intentionally a reset-to-baseline branch rather than the next pure-phase child of `07`.
- `08b` and `08c` are completed sibling sweeps under `08`; neither is the parent of the other.
- `08b` is Bangma-targeted but must not be called an exact Bangma geometry until the baseline geometry is visually verified.
- `08c` changes geometry, inlet area, velocity, and Harwell diameters together, so it is not a geometry-only sensitivity.
- `09` returns to the split-inlet comparison lineage as a family parent from `07`, not as a continuation of the one-inlet reset branch.
- Use `08` when the task is to recreate the Purnanto setup itself with one inlet carrying both phases, not when the task is to continue the split-inlet comparison lineage.

This means `09-multiphase-separator-sensitivity-family.md` is now the current parent in the split-inlet comparison chain, while `09a`, `09b`, and `09c` are the concrete planned child branches. `08` remains the active reset-to-baseline branch and `08a` is the retained outlet-extension child diagnostic.

## Branch-State Reading Guide

- `reference baseline`: use as the root reconstruction source, not as proof of current Fluent state.
- `superseded concept branch`: useful for lineage and reasoning, but no longer the preferred setup path.
- `superseded diagnostic parent` or `stalled diagnostic parent`: keep for failure history and comparisons, not for report-facing performance claims.
- `diagnostic child run only`: useful for qualitative behavior and failure modes, not as a stable operating case.
- `active calculation parent`: current numerical-definition base for downstream setup branches.
- `planned diagnostic branch`: defined well enough to build next, but not yet confirmed as run.
- `alternate retained`: keep as a controlled comparison option, not the selected next case.
- `selected next setup definition`: the branch currently chosen for the next concrete build/check path.

## Rename Guidance

If files are renamed later, do it in this order:

1. rename files to the proposed stable filenames;
2. update links in `ResearchProject_wiki/wiki/index.md`;
3. update links inside setup reports that reference parent reports;
4. leave this dictionary in place as the mapping table from old names to new names.

## Open Memory Checks

These items are still marked as reconstructed rather than proven:

- whether `02` and `03` were strictly sequential in real execution or partly parallel;
- the exact real-world run position of `02b`;
- whether `05` was only planned or also built/run in Fluent.
