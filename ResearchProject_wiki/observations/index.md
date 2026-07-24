# Simulation Observations

This folder is the project-level comparison layer for simulation results. A setup record says what was configured; an observation explains what changed between related setups, what can presently be inferred, and why that points to the next simulation.

These are working engineering observations, not validation records. Every observation keeps the numerical and evidence limits visible, especially incomplete DPM tracks, open carrier balances, unmatched iteration/time windows, and missing EWF source histories.

## Observation sequence

1. [01 — 08b/08c inlet-loading family](01-08b-08c-inlet-loading.md)
2. [02 — 09a/09b DPM injection and dispersion](02-09a-09b-dpm-dispersion.md)
3. [03 — 08b/09c global DPM interaction](03-08b-09c-global-dpm-interaction.md)
4. [04 — 010V2 isolated and combined EWF mechanisms](04-010v2-ewf-mechanism-comparison.md)
5. [05 — 010V2d/010V2d-2 global DPM interaction with EWF](05-010v2d-global-dpm-interaction.md)
6. [06 — 010V2a–010V2d iteration continuation](06-010v2-iteration-continuation.md)

See the [observation order dictionary](order-dictionary.md) for the intended controlled comparison and the next decision each observation supports.

## Use rule

When a new case is run, update the relevant observation before creating another physics branch. Record:

- the comparison window and checkpoints;
- what was intentionally changed and what was held fixed;
- the numerical quantities that moved;
- the narrowest justified interpretation; and
- the one next simulation that resolves the remaining ambiguity.

Do not convert an observation into a separator-efficiency, steam-purity, or validation claim until its underlying carrier and field-wise mass-balance gates are met.
