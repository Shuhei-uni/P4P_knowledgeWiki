# Setup 010V2d-2 — Combined EWF with Global DPM Interaction

## Setup metadata

| Field | Value |
|---|---|
| Setup ID | `010V2d-2` |
| Lifecycle | `future` |
| Role | global-DPM coupling sensitivity after combined EWF mechanisms |
| Parent setup | accepted [010V2d](../active/010V2d-ewf-combined-interaction.md) |
| Controlled change | global `DPM Interaction with Continuous Phase` only |
| Evidence-use label | diagnostic until carrier-source and film mass balances close |
| Outcome | needs follow-up |
| Linked report | [diagnostic results](../reports/010V2d-2/results.md) |

## Objective

Determine how enabling global DPM source interaction changes the accepted combined EWF case. This branch must be created from a stable, mass-reconciled `010V2d` case and must not be used to rescue an unstable isolated mechanism.

## Inherited setup

Keep identical to the accepted `010V2d` case:

- EWF wall, film material, wall condition, fixed transient controls, and film solution settings;
- accepted subset of splash, edge separation, and particle stripping;
- six original injections and any Fluent-generated separation/stripping injection;
- corrected DPM tracking controls: unsteady tracking off, no `0.001 s` particle-time-step override, and maximum particle steps `10000`;
- all inlet, outlet, phase, material, mesh, and wall settings.

## Controlled change

Change only:

| Setting | `010V2d-2` value |
|---|---|
| Global `DPM Interaction with Continuous Phase` | `On` |
| Update DPM sources every flow iteration | retain parent value (`On`) |
| DPM iteration interval | retain parent value (`1`) |

Do not change the EWF mechanism settings, fixed flow timestep, DPM tracking correction, or wall-film settings in this branch.

## Click-by-click procedure

1. Open the accepted/read-back-verified `010V2d` case/data pair.
2. Save as `010V2d-2-ewf-combined-global-dpm.cas.h5` and its corresponding data checkpoint.
3. Go to `Models > Discrete Phase > Interaction`.
4. Enable `Interaction with Continuous Phase`.
5. Retain source updates every flow iteration and iteration interval `1`.
6. Reopen the panel and read back all three interaction settings.
7. Confirm the EWF mechanism flags and generated injection identities are unchanged from `010V2d`.
8. Save the case/data checkpoint before running.
9. Run only after the parent combined case has passed its stability and mass-closure gate.

## Required comparison outputs

- carrier phase source terms and continuity imbalance versus `010V2d`;
- direct DPM-to-carrier mass and momentum source totals;
- film storage, film outflow, splash mass, separated mass, and stripped mass;
- original and generated-particle fates;
- film CFL, residuals, maximum film thickness, and total liquid closure.

## Acceptance gate

Keep `010V2d-2` diagnostic unless the difference from `010V2d` can be attributed to global DPM source interaction without an unbounded film inventory, unexplained carrier imbalance, or floating-point failure.

## Linked evidence

- [010V2d parent](../active/010V2d-ewf-combined-interaction.md)
- [010V2 control](../active/010V2-ewf-deposition-film-inventory.md)
