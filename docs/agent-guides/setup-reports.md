# Setup reports and lineage

`Setups/` is for setup-instance documents, not generic CFD guidance or day-to-day project logging.

Use it for named case definitions, parent/child variants, ordered branch history, and report-ready snapshots with concrete boundary conditions, assumptions, and calculation notes. Do not use it for reusable cross-project CFD guidance, literature extraction, paper synthesis, or general status and blockers.

## When to create or update a setup record

Create or revise a `Setups/` file for a new setup branch or variant, a concrete Fluent boundary-condition package for a named case, a report-facing record for a run or planned run, or setup cleanup, ordering, naming, and lineage reconstruction. Do not create one solely for reusable guidance or project interpretation.

## Ordering and naming

1. Read [`Setups/order-dictionary.md`](../../Setups/order-dictionary.md) before creating, renaming, or reorganizing setup files.
2. Preserve an assigned numbered sequence.
3. Add a number or branch suffix such as `08`, `08a`, or `08b` instead of renaming an older report.
4. Do not use `current`, `latest`, or `final` in setup-report filenames.
5. Update cross-links and wiki references after a rename or new report.
