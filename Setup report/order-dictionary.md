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
- `ResearchProject_wiki/wiki/project/roadmap.md`
- internal parent/child notes inside each setup report

## Project Linkage

Use this file together with:

- `../ResearchProject_wiki/wiki/project/roadmap.md`

Reason:

- this dictionary tells you where a setup sits in the lineage;
- the roadmap tells you which setup branch is the active project path and what the next simulation stages are.

Current project-level interpretation:

- setup `08b` is the active parity-reset parent and V&V authority branch for the roadmap;
- setup `08c` is the immediate next child branch for inlet-velocity/loading sensitivity while keeping the same enthalpy basis;
- setup `07` is retained as comparison context rather than the primary next V&V parent;
- setup-family branches grown from `08b` or later accepted parity-reset branches should be checked against the roadmap before creating or reviving additional setup reports;
- brine-outlet and water-initialization branches remain part of the historical lineage, but they are currently parked as future exploratory work rather than active roadmap steps.

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
| `08` | direct Purnanto-recreation branch on `purnantov2` geometry | `08-purnanto-one-inlet-massflow-recreation.md` | `08-purnanto-one-inlet-massflow-recreation.md` | High | retained automation parity scaffold | keeps the direct paper-style one-inlet mixed steam-water `Mass-Flow Inlet` package, but on the later `purnantov2` geometry line rather than on the earlier `purnanto` geometry line |
| `08a` | `purnantov2` outlet-boundary-placement trial | `08a-steam-outlet-extension-student-trial.md` | `08a-steam-outlet-extension-student-trial.md` | High | planned student-edition diagnostic branch | child of `07`; uses the later `purnantov2` geometry label, including downstream steam-outlet boundary placement and later project cleanup to the spiral-inlet / dish-head reconstruction |
| `08b` | extraction-first parity split-inlet rebuild | `08b-purnanto-parity-split-inlet-rebuild.md` | `08b-purnanto-parity-split-inlet-rebuild.md` | High | selected parity-reset and V&V candidate | starts from the live Purnanto audit, preserves observed Fluent settings as the primary authority, and changes only the inlet representation plus later project DPM injection definition |
| `08c` | parity-child inlet-velocity sensitivity branch | `08c-purnanto-parity-inlet-velocity-sensitivity.md` | `08c-purnanto-parity-inlet-velocity-sensitivity.md` | High | planned next loading-sensitivity branch | child of `08b`; keeps the same split-inlet topology and enthalpy basis while varying inlet loading to test efficiency sensitivity |
| `09` | post-parity DPM sensitivity family parent | `09-multiphase-separator-sensitivity-family.md` | `09-multiphase-separator-sensitivity-family.md` | High | parked future family container | reserved for later DPM sensitivity work after the parity-reset branch is accepted rather than immediately after setup `07` |
| `09a` | one-way DPM tracking cleanup branch | `09a-dpm-split-inlet-carryover.md` | `09a-dpm-split-inlet-carryover.md` | High | planned first post-baseline branch | child of `09`; uses the accepted carrier field and tests only DPM tracking completeness and robustness |
| `09b` | one-way DPM stochastic sensitivity branch | `09b-rsm-dpm-split-inlet-accuracy.md` | `09b-rsm-dpm-split-inlet-accuracy.md` | High | planned second post-baseline branch | child of `09`; legacy filename retained, but current role is stochastic / turbulence sensitivity within one-way DPM rather than an immediate `RSM-DPM` jump |
| `09c` | two-way DPM coupling branch | `09c-dpm-ewf-wall-film-reentrainment.md` | `09c-dpm-ewf-wall-film-reentrainment.md` | High | planned third post-baseline branch | child of `09`; legacy filename retained, but current role is DPM coupling sensitivity, with wall-film and re-entrainment deferred to a later family |

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
```

## Working Interpretation

- Main lineage:
  `00 -> 00a -> 08b -> 08c`
- Child/side branches:
  `01`, `02`, `02b`, `03`, `03a`, `04`, `05`, `06`, `07`, `08`, `08a`, `09`, `09a`, `09b`, `09c`

Interpretation note:

- `08` is intentionally a reset-to-baseline branch rather than the next pure-phase child of `07`.
- `08b` is the extraction-first reset branch for recovering setup fidelity before new V&V claims are made.
- `08c` is the immediate child branch for supervisor-directed inlet-velocity sensitivity while keeping the same inlet enthalpy basis.
- use `purnanto` for the closer paper-parity geometry label and `purnantov2` for the later cleaned geometry with downstream steam-outlet boundary placement.
- setups `04`, `05`, `06`, `07`, `08b`, and `08c` use `purnanto` geometry; setup `08` and `08a` use `purnantov2` unless a setup report explicitly overrides that.
- geometry naming is separate from inlet boundary-condition style.
- `09` remains reserved for later DPM sensitivity work once the parity-reset branch is accepted.
- Use `08` when the task is to recreate the Purnanto setup itself with one inlet carrying both phases, not when the task is to continue the split-inlet comparison lineage.
- Use `08b` when the task is to preserve the observed Purnanto setup as closely as possible while introducing the project's split-inlet objective and extraction-driven DPM rebuild.
- Use `08c` when the task is to test how changed inlet loading/velocity affects efficiency without mixing in a new enthalpy assumption.

This means `08b-purnanto-parity-split-inlet-rebuild.md` remains the parity authority branch, `08c-purnanto-parity-inlet-velocity-sensitivity.md` is the next child branch for loading sensitivity, `08` remains the one-inlet automation/parity scaffold, `08a` remains the retained outlet-extension child diagnostic, and `09a` to `09c` stay parked until a stronger parent branch exists.

Current roadmap alignment note:

- setup `07` no longer carries the primary V&V burden;
- setup `08b` remains the parity parent because setup fidelity now takes priority over continuing the older split-inlet chain;
- setup `08c` is the next sensitivity branch because the current project question is inlet-loading/velocity effect at fixed enthalpy basis;
- family `09` remains limited to smaller DPM-only escalation steps, but only after setup `08b` is accepted;
- later wall-film and re-entrainment work should move into a future `10` family.

## Technical Companions

These files are companion reports, not new lineage entries in the strict numbering table:

- [00-baseline-spiral-boc-reference-technical.md](00-baseline-spiral-boc-reference-technical.md)
- [07-pure-phase-split-actual-area-technical.md](07-pure-phase-split-actual-area-technical.md)

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

1. rename files to the proposed stable filenames;
2. update links in `ResearchProject_wiki/wiki/index.md`;
3. update links inside setup reports that reference parent reports;
4. leave this dictionary in place as the mapping table from old names to new names.

## Open Memory Checks

These items are still marked as reconstructed rather than proven:

- whether `02` and `03` were strictly sequential in real execution or partly parallel;
- the exact real-world run position of `02b`;
- whether `05` was only planned or also built/run in Fluent.
