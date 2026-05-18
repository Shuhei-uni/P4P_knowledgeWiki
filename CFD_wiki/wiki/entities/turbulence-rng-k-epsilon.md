# Entity: RNG k-epsilon Turbulence Model

## Definition
Two-equation RANS turbulence model selected in this domain as a practical balance between cost and cyclone-flow prediction quality.

## Usage in Wiki
- Used as baseline turbulence model in `purnanto-2013` for high-swirl separator flow ([purnanto-2013], p.1, p.3, p.9).
- Used in the Workbench cyclone separator settings report with the Swirl Dominated Zone option because the report treats RNG as a rotating-flow accuracy improvement (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).

## Linked Sources
- [purnanto-2013-cfd-geothermal-separator](../sources/purnanto-2013-cfd-geothermal-separator.md)
- [user-cyclone-workbench-rng-dpm-settings-report](../sources/user-cyclone-workbench-rng-dpm-settings-report.md)

## Notes
- Future sources should record whether results are sensitive to model change (for example RSM or LES).
- The cyclone separator tutorial explicitly recommends [turbulence-reynolds-stress-model](turbulence-reynolds-stress-model.md) over standard k-epsilon-style RANS for strong cyclone swirl (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes). Relation: `differs`.
- Current cyclone exemplars therefore contain a useful model-choice contrast: RNG k-epsilon plus swirl option for a lower-cost Workbench workflow vs RSM for a higher-fidelity/high-convergence-cost ICEM workflow.
