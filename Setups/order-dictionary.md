# Setups Order Dictionary

> **LEGACY / REFERENCE ONLY**
> This file records historical numbered lineage. It is not current routing or project authority.
> New selected experiments belong in [`Project/experiments/`](../Project/experiments/); do not assign a new global setup number here.

## Purpose

This file is the ordering and lineage reference for `Setups/`.

Use it only to answer historical questions quickly:

1. which setup came before or after another;
2. which filename should be used when reports are renamed into a strict sequence.

This is an ordering aid, not proof that every branch was run to completion.
Where the history is uncertain, the ordering below reflects the current best reconstruction from:

- `ResearchProject_wiki/wiki/log.md`
- `ResearchProject_wiki/wiki/progress/current-status.md`
- `ResearchProject_wiki/wiki/progress/experiments.md`
- `ResearchProject_wiki/wiki/project/roadmap.md`
- internal parent/child notes inside each setup report

## Project Linkage

For current project state and selected experiments, start with [`Project/index.md`](../Project/index.md). Use this dictionary only when a retained numbered record or its provenance is involved.

Use this file together with:

- `../ResearchProject_wiki/wiki/project/roadmap.md`

Reason:

- this dictionary tells you where a setup sits in the lineage;
- the roadmap tells you which setup branch is the active project path and what the next simulation stages are.

Current project-level interpretation:

- setup `08c` is a past reported inlet-velocity/loading diagnostic while keeping the same enthalpy basis;
- setup `09c` is a past reported two-way-DPM diagnostic;
- setup `09cV2` and the complete `010V2` family are past reported diagnostics; its `09cV3` fine-mist PSD child remains active;
- setup `08b` is the past reported parity-reset parent and numerical reference for the `09` DPM family;
- setup `07` is retained as comparison context rather than the primary next V&V parent;
- setups `04`, `07`, `08b`, `08c`, `09a`, `09b`, `09c`, `09cV2`, the `010V2` family, and `10a-splash` are past reported because they contain actual efficiency and/or DPM trajectory/fate numerics;
- setup `08a` and the remaining older setup definitions are archived until stronger numerical evidence is recorded;
- setup-family branches grown from `08b` or later accepted parity-reset branches should be checked against the roadmap before creating or reviving additional setup reports;
- lifecycle state is a filing decision, not a permanent judgment: update the setup's lifecycle and linked report when new evidence changes its role.

## Lifecycle Classification Rule

Use `active` for setups currently being run or actively changed.

Use `future` for a planned branch intended for later execution.

Use `reported` only when the setup record or linked report contains actual numerical evidence of at least one of:

- flux-based efficiency, carryover, or phase-balance calculation using actual result values;
- DPM injection trajectory/fate results with numerical `escaped`, `trapped`, or `incomplete` counts.

Use `archived` for historical, superseded, invalid, planned-but-parked, or setup-only records that do not yet meet the reported-evidence rule.

The evidence-use label must still state whether a reported result is diagnostic, incomplete, non-converged, inherited, or suitable for stronger claims.

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
| `02c` | unprimed Mixture brine-outlet pressure sensitivity | `active/02c-mixture-brine-outlet-pressure-sensitivity-unprimed.md` | `02c-mixture-brine-outlet-pressure-sensitivity-unprimed.md` | High | active setup-definition branch | child of archived `02`; fixed velocity-inlet parent and 1.115/1.120/1.125 MPa brine-pressure matrix; no result evidence yet |
| `02d` | transient VOF brine-outlet model-form sensitivity | `future/02d-transient-vof-brine-outlet-model-form-sensitivity.md` | `02d-transient-vof-brine-outlet-model-form-sensitivity.md` | High | planned setup-definition branch | VOF model-form comparison against the `02c` Mixture control; baseline `1.120 MPa` qualification, human-gated patch variants, and no numerical evidence yet |
| `03` | mixed wet-half main branch | `03-mixed-wet-half-velocity-inlet.md` | `03-mixed-wet-half-velocity-inlet.md` | High | stalled diagnostic parent | replaces pure split with equal-velocity wet-half concept |
| `03a` | child of `03` | `03a-mixed-wet-half-velocity-inlet-water-pool.md` | `03a-mixed-wet-half-velocity-inlet-water-pool.md` | High | diagnostic child run only | explicit child case of `03` |
| `04` | actual-area recalculation branch | `04-mixed-wet-half-actual-area.md` | `04-mixed-wet-half-actual-area.md` | High | past reported diagnostic | contains flux-efficiency and DPM tracking numerics; incomplete tracks remain dominant |
| `05` | full-inlet alternative branch | `05-complete-two-phase-actual-area-no-brine-outlet.md` | `05-complete-two-phase-actual-area-no-brine-outlet.md` | High | archived planned branch | branch from `04`; one full inlet, no active brine outlet |
| `06` | fixed-velocity pure-phase alternative | `06-pure-phase-split-fixed-velocity.md` | `06-pure-phase-split-fixed-velocity.md` | High | archived setup-only alternate | branch from later actual-area work; preserves `26.81 m/s` |
| `07` | pure-phase actual-area branch | `07-pure-phase-split-actual-area.md` | `07-pure-phase-split-actual-area.md` | High | past reported diagnostic | contains scoped flux carryover efficiency and DPM injection-fate numerics |
| `08` | direct Purnanto-recreation branch on `purnantov2` geometry | `08-purnanto-one-inlet-massflow-recreation.md` | `08-purnanto-one-inlet-massflow-recreation.md` | High | retained automation parity scaffold | keeps the direct paper-style one-inlet mixed steam-water `Mass-Flow Inlet` package, but on the later `purnantov2` geometry line rather than on the earlier `purnanto` geometry line |
| `08a` | `purnantov2` outlet-boundary-placement trial | `08a-steam-outlet-extension-student-trial.md` | `08a-steam-outlet-extension-student-trial.md` | High | archived planned branch | child of `07`; result fields remain pending |
| `08b` | extraction-first parity split-inlet rebuild | `08b-purnanto-parity-split-inlet-rebuild.md` | `08b-purnanto-parity-split-inlet-rebuild.md` | High | past reported parity parent | contains scoped flux efficiency and partial-bin DPM fate numerics |
| `08c` | parity-child inlet-velocity sensitivity branch | `past/reported/08c-purnanto-parity-inlet-velocity-sensitivity.md` | `08c-purnanto-parity-inlet-velocity-sensitivity.md` | High | past reported loading-sensitivity diagnostic | child of `08b`; partial/nonconverged scoped outlet and DPM-fate evidence is recorded |
| `09` | post-parity DPM sensitivity family parent | `09-multiphase-separator-sensitivity-family.md` | `09-multiphase-separator-sensitivity-family.md` | High | archived family definition | child reports carry the numerical DPM evidence |
| `09a` | one-way DPM tracking cleanup branch | `09a-dpm-split-inlet-carryover.md` | `09a-dpm-split-inlet-carryover.md` | High | past reported DPM branch | contains deterministic DPM fate numerics, including inherited parent evidence |
| `09b` | one-way DPM stochastic sensitivity branch | `09b-rsm-dpm-split-inlet-accuracy.md` | `09b-rsm-dpm-split-inlet-accuracy.md` | High | past reported DPM branch | contains stochastic fate numerics and escape-fraction comparisons |
| `09c` | two-way DPM coupling branch | `past/reported/09c-dpm-ewf-wall-film-reentrainment.md` | `09c-dpm-ewf-wall-film-reentrainment.md` | High | past reported diagnostic | child of `09`; partial coupled carrier-flux evidence is recorded but not converged |
| `09cV2` | Skoog partition and injection control | `past/reported/09cV2-skoog-partition-injection-control.md` | `09cV2-skoog-partition-injection-control.md` | High | past reported allocation-control diagnostic | child of `09c`; mass-partitioned DPM parent with diagnostic fate evidence |
| `09cV3` | fine-mist 5% DPM PSD rerun | `active/09cV3-fine-mist-5pct-psd-rerun.md` | `09cV3-fine-mist-5pct-psd-rerun.md` | High | active PSD-comparison branch | child of `09cV2`; preserves the 5% DPM allocation while replacing only the legacy six-bin injection PSD with the provisional seven-bin `5–100 µm` fine-mist distribution |
| `010V2` | clean EWF deposition and film-inventory control | `past/reported/010V2-ewf-deposition-film-inventory.md` | `010V2-ewf-deposition-film-inventory.md` | High | past reported EWF diagnostic | child of `09cV2`; numerical film and DPM-fate evidence is recorded, but carrier closure is open |
| `010V2a` | EWF splash sensitivity | `past/reported/010V2a-ewf-splash.md` | `010V2a-ewf-splash.md` | High | past reported splash diagnostic | child of `010V2`; numerical DPM-fate evidence is recorded, but not converged |
| `010V2b` | EWF edge-separation sensitivity | `past/reported/010V2b-ewf-edge-separation.md` | `010V2b-ewf-edge-separation.md` | High | past reported edge-separation diagnostic | child of `010V2`; partial numerical DPM-fate evidence is recorded |
| `010V2c` | EWF particle-stripping sensitivity | `past/reported/010V2c-ewf-particle-stripping.md` | `010V2c-ewf-particle-stripping.md` | High | past reported stripping diagnostic | child of `010V2`; numerical DPM-fate evidence is recorded, but not converged |
| `010V2d` | combined EWF interaction confirmation | `past/reported/010V2d-ewf-combined-interaction.md` | `010V2d-ewf-combined-interaction.md` | High | past reported combined-EWF diagnostic | numerical film and DPM-fate evidence is recorded, but acceptance remains unresolved |
| `010V2d-2` | combined EWF with global DPM interaction | `past/reported/010V2d-2-ewf-combined-global-dpm.md` | `010V2d-2-ewf-combined-global-dpm.md` | High | past reported coupled-combination diagnostic | child of `010V2d`; numerical film and DPM-fate evidence is recorded, but not converged |
| `10` | wall-film / re-entrainment / custom-DPM escalation family | `10-wall-film-reentrainment-and-dpm-interaction-plan.md` | `10-wall-film-reentrainment-and-dpm-interaction-plan.md` | Medium | future staged family | child plans `10a`, `10b`, and `10c` may be executed once the parent case/change readback is ready; report-quality interpretation still requires the evidence gate |
| `10a` | intended EWF deposition/drainage child | `past/archived/10a-ewf-deposition.md` | `10a-ewf-deposition.md` | High | archived setup-only control | the intended no-splash control has no qualifying clean result; the saved artifact was splash-enabled |
| `10a-splash` | initialized EWF splash child | `past/reported/10a-splash-ewf-deposition.md` | `10a-splash-ewf-deposition.md` | High | past reported diagnostic | splash-enabled EWF artifact with preliminary numerical carrier/flux evidence |
| `10b` | DPM wall-return/re-entrainment surrogate child | `10-wall-film-reentrainment-and-dpm-interaction-plan.md` | `10-wall-film-reentrainment-and-dpm-interaction-plan.md` | Medium | future child | parent `09c`; EWF off, controlled wall-return sensitivity |
| `10c` | custom DPM trajectory/material child | `10-wall-film-reentrainment-and-dpm-interaction-plan.md` | `10-wall-film-reentrainment-and-dpm-interaction-plan.md` | Medium | future child | parent `09c`; EWF and wall-return off, one custom law/material change at a time |
| `11` | combined wall-film and DPM physics family | `11-combined-wallfilm-dpm-plan.md` | `11-combined-wallfilm-dpm-plan.md` | Medium | future staged family | combines selected stable `10` mechanisms |
| `11a` | combined EWF + re-entrainment child | `11-combined-wallfilm-dpm-plan.md` | `11-combined-wallfilm-dpm-plan.md` | Medium | future child | parent `10a`; adds selected `10b` closure |
| `11b` | combined EWF + re-entrainment + custom DPM/material child | `11-combined-wallfilm-dpm-plan.md` | `11-combined-wallfilm-dpm-plan.md` | Medium | future child | parent `11a`; adds selected stable `10c` change |
| `12` | carrier-field mesh-convergence family | `future/12-carrier-mesh-convergence-plan.md` | `12-carrier-mesh-convergence-plan.md` | High | planned numerical-verification branch | freezes a selected `08b`-compatible carrier case and varies only mesh resolution around `0.4M`, `0.9M`, the observed `1.309M`-node reference, and `1.6M` |

## Parent-Child Map

```text
00 baseline
 -> 00a Purnanto setup 5000 live audit
    -> 08 Purnanto one-inlet mass-flow recreation
    -> 08b Purnanto parity split-inlet rebuild
       -> 08c Purnanto parity inlet-velocity sensitivity
 -> 01 split two-zone mass-flow inlet
    -> 02 split two-zone velocity inlet with brine outlet
       -> 02b VOF split-inlet transient side branch
       -> 02c unprimed Mixture brine-outlet pressure sensitivity
          -> 02d transient VOF brine-outlet model-form sensitivity
       -> 03 mixed wet-half velocity inlet
          -> 03a mixed wet-half with initialized water pool
          -> 04 mixed wet-half actual-area
             -> 05 complete two-phase actual-area no-brine-outlet
             -> 06 pure-phase split fixed velocity
             -> 07 pure-phase split actual-area
                -> 08a purnantov2 outlet-boundary-placement trial
                -> 09 multiphase sensitivity family
                   -> 09a one-way DPM tracking cleanup
                   -> 09b one-way DPM stochastic sensitivity
                   -> 09c two-way DPM coupling
                      -> 09cV2 Skoog partition and injection control
                         -> 09cV3 fine-mist 5% DPM PSD rerun
                         -> 010V2 clean EWF deposition and film-inventory control
                            -> 010V2a EWF splash sensitivity
                            -> 010V2b EWF edge-separation sensitivity
                            -> 010V2c EWF particle-stripping sensitivity
                            -> 010V2d combined EWF interaction confirmation
                               -> 010V2d-2 combined EWF with global DPM interaction
                      -> 10 wall-film / re-entrainment / custom-DPM escalation family
                         -> 10a EWF deposition/drainage
                            -> 10a-splash EWF deposition with particle splashing
                         -> 10b DPM wall-return surrogate
                         -> 10c custom DPM/material sensitivity
                            -> 11 combined wall-film / DPM family
                               -> 11a EWF + re-entrainment
                               -> 11b all selected mechanisms
 -> 12 carrier-field mesh-convergence family (frozen `08b`-compatible carrier baseline)
```

## Working Interpretation

- Main lineage:
  `00 -> 00a -> 08b -> 08c`
- Child/side branches:
  `01`, `02`, `02b`, `03`, `03a`, `04`, `05`, `06`, `07`, `08`, `08a`, `09`, `09a`, `09b`, `09c`, `09cV2`, `09cV3`, `010V2`, `010V2a`, `010V2b`, `010V2c`, `010V2d`, `010V2d-2`

Interpretation note:

- `08` is intentionally a reset-to-baseline branch rather than the next pure-phase child of `07`.
- `08b` is the extraction-first reset branch for recovering setup fidelity before new V&V claims are made.
- `08c` is the immediate child branch for supervisor-directed inlet-velocity sensitivity while keeping the same inlet enthalpy basis.
- use `purnanto` for the closer paper-parity geometry label and `purnantov2` for the later cleaned geometry with downstream steam-outlet boundary placement.
- setups `04`, `05`, `06`, `07`, `08b`, and `08c` use `purnanto` geometry; setup `08` and `08a` use `purnantov2` unless a setup report explicitly overrides that.
- geometry naming is separate from inlet boundary-condition style.
- `09` is now the manual DPM sensitivity/reporting family once setup `08b` has a solved carrier field and the DPM setup can be verified manually.
- Use `08` when the task is to recreate the Purnanto setup itself with one inlet carrying both phases, not when the task is to continue the split-inlet comparison lineage.
- Use `08b` when the task is to preserve the observed Purnanto setup as closely as possible while introducing the project's split-inlet objective and extraction-driven DPM rebuild.
- Use `08c` when the task is to test how changed inlet loading/velocity affects efficiency without mixing in a new enthalpy assumption.

This means `08b-purnanto-parity-split-inlet-rebuild.md`, `08c-purnanto-parity-inlet-velocity-sensitivity.md`, `09cV2-skoog-partition-injection-control.md`, and all `010V2` setup records are past reported diagnostics; `09cV3-fine-mist-5pct-psd-rerun.md` remains active; `09c-dpm-ewf-wall-film-reentrainment.md` is past reported; and `08` remains the archived one-inlet automation/parity scaffold.

Current roadmap alignment note:

- setup `07` no longer carries the primary V&V burden;
- setup `08b` remains the parity parent because setup fidelity took priority over continuing the older split-inlet chain;
- setup `08c` is a past reported sensitivity diagnostic for inlet-loading/velocity effect at fixed enthalpy basis;
- `09a`, `09b`, `09c`, and `09cV2` are past reported DPM-output/coupling branches; `09cV3` remains active, while all `010V2` branches are past reported diagnostics;
- setup `09a` should be used first for deterministic one-way DPM fate counts on the accepted `08b` carrier field;
- setup `09b` should be used second for one-way DPM turbulent-dispersion sensitivity after `09a` fate counts are recorded;
- PyFluent automation for the injection calculations is treated as a convenience path only; manual Fluent runs are acceptable if the DPM setup values and fate-count outputs are reported in the corresponding setup reports;
- later wall-film and re-entrainment work should move into a future `10` family.
- future `10` work is now recorded as a staged family: first EWF deposition/drainage, then re-entrainment/impingement, then custom DPM trajectory and material sensitivity.
- future `11` work is reserved for combinations: `11a` combines EWF with the selected re-entrainment closure, and `11b` adds only the selected stable custom DPM/material change.

## Technical Companions

These files are companion reports, not new lineage entries in the strict numbering table:

- [00 technical extraction](reports/00/technical-extraction.md)
- [07 technical extraction](reports/07/technical-extraction.md)

Use them when the live Fluent export needs to be separated from the human narrative report. They capture replay-relevant geometry/mesh context and report-versus-extraction drift without replacing the main branch order.

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

1. preserve the assigned setup ID and filename;
2. update the lifecycle index and linked report path;
3. update links inside setup reports that reference parent reports;
4. leave this dictionary in place as the mapping table for lineage and branch identity.

## Open Memory Checks

These items are still marked as reconstructed rather than proven:

- whether `02` and `03` were strictly sequential in real execution or partly parallel;
- the exact real-world run position of `02b`;
- whether `05` was only planned or also built/run in Fluent.
