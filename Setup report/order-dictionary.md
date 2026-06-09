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
```

## Working Interpretation

- Main lineage:
  `00 -> 01 -> 02 -> 03 -> 04 -> 07`
- Child/side branches:
  `00a`, `02b`, `03a`, `05`, `06`, `08`

Interpretation note:

- `08` is intentionally a reset-to-baseline branch rather than the next pure-phase child of `07`.
- Use `08` when the task is to recreate the Purnanto setup itself with one inlet carrying both phases, not when the task is to continue the split-inlet comparison lineage.

This means `07-pure-phase-split-actual-area.md` is the latest named branch in the reconstructed chain, but the filename does not depend on it being "current".

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
