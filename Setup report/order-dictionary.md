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
| `08` | direct Purnanto-recreation branch | `08-purnanto-one-inlet-massflow-recreation.md` | `08-purnanto-one-inlet-massflow-recreation.md` | High | selected direct baseline-rebuild branch | returns to the paper-style one-inlet mixed steam-water `Mass-Flow Inlet` package using the live Purnanto audit and reusable CFD baseline as the concrete rebuild target |
| `08a` | steam-outlet boundary-placement trial | `08a-steam-outlet-extension-student-trial.md` | `08a-steam-outlet-extension-student-trial.md` | High | planned student-edition diagnostic branch | child of `07`; keeps the Purnanto spiral-inlet body and setup `07` split two-phase inlet, but extends the central steam outlet path so the pressure-outlet boundary is downstream of the outlet-pipe entrance |
| `09` | multiphase sensitivity family parent | `09-multiphase-separator-sensitivity-family.md` | `09-multiphase-separator-sensitivity-family.md` | High | active family container | child of `07`; replaces the retired VOF-only idea with a parent container for literature-backed `DPM`, `RSM-DPM`, and `DPM + EWF` child branches |
| `09a` | split-inlet DPM carryover branch | `09a-dpm-split-inlet-carryover.md` | `09a-dpm-split-inlet-carryover.md` | High | planned first carryover branch | child of `09`; keeps the setup `07` continuous-field basis and adds `DPM` as the lowest-risk literature-backed next step for droplet escape sensitivity |
| `09b` | split-inlet RSM-DPM accuracy branch | `09b-rsm-dpm-split-inlet-accuracy.md` | `09b-rsm-dpm-split-inlet-accuracy.md` | High | planned higher-accuracy branch | child of `09`; upgrades the carrier-field turbulence closure to `RSM` and adds `DPM`, following the stronger recent separator-method anchor from Chen 2025 |
| `09c` | split-inlet DPM + EWF wall-film branch | `09c-dpm-ewf-wall-film-reentrainment.md` | `09c-dpm-ewf-wall-film-reentrainment.md` | High | planned wall-film mechanism branch | child of `09`; treats wall-film persistence and re-entrainment as the main unresolved mechanism rather than only droplet escape |

## Parent-Child Map

```text
00 baseline
 -> 00a Purnanto setup 5000 live audit
    -> 08 Purnanto one-inlet mass-flow recreation
 -> 01 split two-zone mass-flow inlet
    -> 02 split two-zone velocity inlet with brine outlet
       -> 02b VOF split-inlet transient side branch
       -> 03 mixed wet-half velocity inlet
          -> 03a mixed wet-half with initialized water pool
          -> 04 mixed wet-half actual-area
             -> 05 complete two-phase actual-area no-brine-outlet
             -> 06 pure-phase split fixed velocity
             -> 07 pure-phase split actual-area
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
  `00a`, `02b`, `03a`, `05`, `06`, `08`, `08a`, `09a`, `09b`, `09c`

Interpretation note:

- `08` is intentionally a reset-to-baseline branch rather than the next pure-phase child of `07`.
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
