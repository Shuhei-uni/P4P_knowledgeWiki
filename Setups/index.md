# Setups

This is the primary index for concrete Fluent experiments, setup branches, and numerical findings.

## Lifecycle views

- [Active setups](active/index.md): cases currently being run or actively changed.
- [Future setups](future/index.md): planned branches not yet started.
- [Past reported setups](past/reported/index.md): setups with numerical efficiency or DPM trajectory/fate evidence.
- [Past archived setups](past/archived/index.md): setup definitions retained for lineage, failed approaches, or historical context without a complete numerical report.
- [Reports](reports/index.md): detailed numerical findings linked to a setup.

## Rule of thumb

Create a setup record when the Fluent inputs or controlled experiment branch are defined. Create a report when numerical results are available.

Reported results must contain at least one of:

- a flux-based efficiency, carryover, or phase-balance calculation using actual result values;
- a DPM injection result with numerical observed escape at a named outlet.

Do not promote a setup based only on planned values, target calculations, screenshots without extracted numbers, or placeholder result tables.

## Setup record contract

Every setup record should identify:

| Field | Meaning |
|---|---|
| Setup ID | Stable sequence/branch identifier such as `08b`; never change it after assignment. |
| Lifecycle | `active`, `future`, `reported`, or `archived`. |
| Role | Reference, experiment, sensitivity branch, audit, or other concrete purpose. |
| Parent / children | Direct lineage links. |
| Controlled changes | What differs from the parent setup. |
| Evidence-use label | Diagnostic, setup calculation only, report-quality, parity-closed baseline, etc. |
| Outcome | Keep, reject, or needs follow-up. |
| Linked report | Report path, or `none` when numerical findings do not yet exist. |

## Report contract

Each report belongs to one setup and should contain:

- run identity and case/data files;
- changed variables and inherited setup state;
- residuals and named-outlet phase fluxes;
- efficiency calculations and/or DPM trajectory/fate tables;
- visual and numerical findings;
- uncertainty, raw evidence categories, and assumptions;
- conclusion and next action.

The setup record remains the authority for the case definition. The report is the authority for the documented result of that run.

## Lineage authority

- [Setup order dictionary](order-dictionary.md)
- [Technical setup report template](templates/technical-setup-report-template.md)
