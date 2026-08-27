# Setup Subagent Brief

Work in `Project/experiments/` for ordinary current selected experiments, keeping `setup.md` and `results.md` together. Use `Setups/` only for retained setup/report provenance, historical lineage, or an explicitly authorized repair; do not create new selected experiment records in its mirrored trees.

## Mission

Maintain concrete setup-instance records:
- named setup branches
- parent/child lineage
- report-facing boundary-condition packages
- ordering and naming stability
- current experiment setup/results contracts under `Project/experiments/`

## Primary Files You May Touch

- `Setups/`
- `Project/experiments/`
- `Project/index.md`
- especially `Setups/order-dictionary.md` for historical lineage only

## Do

- read `Project/index.md` first for current work;
- read `Setups/index.md` and `Setups/order-dictionary.md` only for retained or historical setup lineage
- preserve existing numbering once assigned
- preserve existing numbers or branch suffixes when repairing old files; do not create new numbers for Project experiments
- keep retained setup reports concrete: BCs, assumptions, calculation notes, branch identity
- note lineage effects whenever branch identity, ordering, or naming changes

## Do Not

- write generic CFD guidance
- do not use `Setups/` for new selected experiment records or day-to-day progress logging
- update `Project/experiments/` for current selected experiment setup/results when assigned that scope
- use status words like `current`, `latest`, or `final` in setup filenames

## Handoff Back to Main Agent

Return:
- the setup-branch change
- whether `order-dictionary.md` changed or should change
- any project-status implication that belongs in `ResearchProject_wiki`
